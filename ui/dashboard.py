# ui/dashboard.py — Main dashboard view

import customtkinter as ctk
from datetime import date
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label
from db.models import Bean, BeanBatch, ExtractionLog, MaintenanceTask, Equipment
from logic.degassing import STATUS_COLORS, STATUS_LABELS
from logic.api_client import api


class DashboardView(ctk.CTkScrollableFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.app = app
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        try:
            # Fetch data from API
            beans       = api.get_beans()
            extractions = api.get_extractions()
            equipment   = api.get_equipment()
            tasks       = api.get_maintenance_tasks()
            
            # Since beans includes batches:
            batches = []
            for b in beans:
                if hasattr(b, 'batches'):
                    for batch in b.batches:
                        # Attach bean reference to batch for UI compatibility
                        batch.bean = b
                        batches.append(batch)
            
            beans_count = len(beans)

            peak_batches    = [b for b in batches if hasattr(b, 'degassing_status') and b.degassing_status == "peak"]
            resting_batches = [b for b in batches if hasattr(b, 'degassing_status') and b.degassing_status == "resting"]
            locked_shots  = [e for e in extractions if getattr(e, 'is_locked', False)]
            last_optimal  = locked_shots[0] if locked_shots else None
            urgent_tasks  = [t for t in tasks if getattr(t, 'is_urgent', False) or getattr(t, 'is_overdue', False)]
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            beans_count = 0
            batches = []
            extractions = []
            equipment = []
            tasks = []
            peak_batches = []
            resting_batches = []
            last_optimal = None
            urgent_tasks = []

        row = 0

        # ── Header ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=row, column=0, sticky="ew", padx=24, pady=(24, 0))
        header.columnconfigure(1, weight=1)
        ctk.CTkLabel(
            header, text="Dashboard",
            font=FONTS["display"], text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text=date.today().strftime("%A, %d %B %Y"),
            font=FONTS["body"], text_color=COLORS["text_muted"]
        ).grid(row=1, column=0, sticky="w")
        row += 1

        # ── Quick stats bar ─────────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(16, 0))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        week_shots = [
            e for e in extractions
            if (date.today() - e.timestamp.date()).days <= 7
        ]
        avg_score = (
            sum(e.score for e in extractions) / len(extractions)
            if extractions else 0
        )

        stats = [
            ("☕", str(len(week_shots)),      "Shots esta semana"),
            ("⭐", f"{avg_score:.1f}/10",     "Score promedio"),
            ("🌱", str(len(batches)),          "Lotes activos"),
            ("⚠️", str(len(urgent_tasks)),    "Alertas mantenimiento"),
        ]
        for col, (icon, val, lbl) in enumerate(stats):
            self._stat_card(stats_frame, icon, val, lbl, col)
        row += 1

        # ── Peak Beans ──────────────────────────────────────────────────────
        row = self._section_header(row, L("dash_peak_beans"))
        if peak_batches or resting_batches:
            beans_frame = ctk.CTkFrame(self, fg_color="transparent")
            beans_frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 4))
            beans_frame.columnconfigure((0, 1, 2), weight=1)
            display_batches = (peak_batches + resting_batches)[:6]
            for i, batch in enumerate(display_batches):
                self._bean_card(beans_frame, batch, i % 3, i // 3)
        else:
            self._empty_state(row, L("dash_no_batches"))
        row += 1

        # ── Last Optimal Recipe ─────────────────────────────────────────────
        row = self._section_header(row, L("dash_last_opt"))
        if last_optimal:
            self._optimal_recipe_card(row, last_optimal)
        else:
            self._empty_state(row, L("dash_no_optimal"))
        row += 1

        # ── Maintenance Alerts ──────────────────────────────────────────────
        row = self._section_header(row, L("dash_maint_alerts"))
        if urgent_tasks:
            alerts_frame = ctk.CTkFrame(self, fg_color="transparent")
            alerts_frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 4))
            alerts_frame.columnconfigure(0, weight=1)
            for i, task in enumerate(urgent_tasks[:5]):
                equip = next((e for e in equipment if e.id == task.equipment_id), None)
                self._alert_card(alerts_frame, task, equip, i)
        else:
            self._empty_state(row, L("dash_maint_ok"), color=COLORS["success"])
        row += 1

        # ── Burr Life ─────────────────────────────────────────────────────────────
        grinders = [e for e in equipment if e.type == "Grinder"]
        if grinders:
            row = self._section_header(row, L("dash_burrs"))
            for i, grinder in enumerate(grinders):
                self._burr_life_card(row + i, grinder)
                row += 1

        # ── AI Extraction Clusters ────────────────────────────────────────────────
        row = self._section_header(row, L("dash_clusters"))
        self._ai_cluster_section(row, extractions)
        row += 1

        row += 1  # Bottom padding

    # ── Widget helpers ──────────────────────────────────────────────────────────
    def _stat_card(self, parent, icon, value, label, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=CORNER_RADIUS["card"])
        card.grid(row=0, column=col, sticky="ew", padx=(0, 8) if col < 3 else 0, pady=0)
        card.columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 22)).pack(pady=(14, 2))
        ctk.CTkLabel(card, text=value, font=FONTS["heading"], text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(card, text=label, font=FONTS["small"], text_color=COLORS["text_muted"]).pack(pady=(0, 14))

    def _section_header(self, row, title):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(20, 8))
        frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            frame, text=title,
            font=FONTS["subhead"], text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkFrame(frame, height=1, fg_color=COLORS["border"]).grid(
            row=1, column=0, sticky="ew", pady=(4, 0)
        )
        return row + 1

    def _bean_card(self, parent, batch, col, row_offset):
        status   = batch.degassing_status
        s_color  = STATUS_COLORS.get(status, COLORS["text_muted"])
        s_label  = STATUS_LABELS.get(status, status)
        days     = batch.days_since_roast

        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=CORNER_RADIUS["card"])
        card.grid(row=row_offset, column=col, sticky="ew",
                  padx=(0, 8) if col < 2 else 0, pady=(0, 8))
        card.columnconfigure(0, weight=1)

        # Status indicator bar
        bar_frame = ctk.CTkFrame(card, height=4, fg_color=s_color, corner_radius=2)
        bar_frame.pack(fill="x", padx=0, pady=0)
        bar_frame.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        inner.columnconfigure(0, weight=1)

        # Bean name and roaster
        ctk.CTkLabel(inner, text=batch.bean.name, font=FONTS["subhead"],
                     text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
        ctk.CTkLabel(inner, text=batch.bean.roaster, font=FONTS["small"],
                     text_color=COLORS["text_muted"], anchor="w").pack(fill="x")

        # Degassing progress bar
        progress = batch.degassing_progress
        ctk.CTkProgressBar(inner, progress_color=s_color,
                           fg_color=COLORS["bg_input"], height=6, corner_radius=3).pack(
            fill="x", pady=(8, 4)
        )

        # Days and status
        days_text = f"Día {days}" if days is not None else "Sin fecha tueste"
        bottom = ctk.CTkFrame(inner, fg_color="transparent")
        bottom.pack(fill="x")
        ctk.CTkLabel(bottom, text=days_text, font=FONTS["small"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        status_badge = ctk.CTkLabel(
            bottom, text=f" {s_label} ",
            font=FONTS["caption"],
            text_color=s_color,
            fg_color=COLORS["bg_primary"],
            corner_radius=CORNER_RADIUS["badge"],
        )
        status_badge.pack(side="right")

        # Fix progress bar value
        for widget in inner.winfo_children():
            if isinstance(widget, ctk.CTkProgressBar):
                widget.set(progress)

    def _optimal_recipe_card(self, row, ext):
        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=CORNER_RADIUS["card"])
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 4))
        card.columnconfigure((0, 1, 2, 3, 4), weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Gold star accent left border
        accent = ctk.CTkFrame(card, width=4, fg_color=COLORS["accent"], corner_radius=0)
        accent.pack(side="left", fill="y")

        stats = [
            ("Dosis/Dose",   f"{ext.dose_in}g"),
            ("Yield",        f"{ext.yield_out}g"),
            ("Ratio",        ext.ratio_str),
            ("Tiempo/Time",  f"{ext.extraction_time}s"),
            ("Temp",         f"{ext.water_temp}°C"),
            ("Score",        f"⭐ {ext.score:.1f}"),
        ]
        for col, (lbl, val) in enumerate(stats):
            frame = ctk.CTkFrame(inner, fg_color="transparent")
            frame.grid(row=0, column=col, padx=12, sticky="w")
            ctk.CTkLabel(frame, text=lbl, font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack()
            ctk.CTkLabel(frame, text=val, font=FONTS["subhead"],
                         text_color=COLORS["text_primary"]).pack()

        # Bean name
        if ext.bean_batch and ext.bean_batch.bean:
            ctk.CTkLabel(inner, text=f"☕ {ext.bean_batch.bean.name} · {ext.bean_batch.bean.roaster}",
                         font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
                row=1, column=0, columnspan=6, sticky="w", pady=(8, 0)
            )
        if ext.grind_size:
            ctk.CTkLabel(inner, text=f"{L('ext_grind')}: {ext.grind_size}",
                         font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
                row=2, column=0, columnspan=6, sticky="w"
            )

    def _alert_card(self, parent, task, equip, idx):
        is_overdue = task.is_overdue
        color      = COLORS["danger"] if is_overdue else COLORS["warning"]
        bg         = COLORS["danger_dim"] if is_overdue else COLORS["warning_dim"]
        days_label = (
            L("dash_overdue") if is_overdue
            else L("dash_in_days").format(task.days_until_due)
        )
        equip_name = f"{equip.brand} {equip.model}" if equip else "—"

        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8)
        card.grid(row=idx, column=0, sticky="ew", pady=(0, 6))
        card.columnconfigure(1, weight=1)

        # Color strip
        strip = ctk.CTkFrame(card, width=4, fg_color=color, corner_radius=0)
        strip.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        ctk.CTkLabel(card, text=task.task_name, font=FONTS["body"],
                     text_color=COLORS["text_primary"]).grid(
            row=0, column=1, sticky="w", pady=8
        )
        ctk.CTkLabel(card, text=equip_name, font=FONTS["small"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=2, padx=12)
        ctk.CTkLabel(card, text=days_label, font=FONTS["small"],
                     text_color=color).grid(row=0, column=3, padx=12)

    def _burr_life_card(self, row, grinder):
        pct    = grinder.burr_life_percent
        color  = COLORS["success"] if pct < 0.7 else (COLORS["warning"] if pct < 0.9 else COLORS["danger"])

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=CORNER_RADIUS["card"])
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 8))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        inner.columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text=f"⚙️ {grinder.brand} {grinder.model}",
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(inner, text=f"{grinder.total_kg_ground:.1f} / {grinder.burr_change_interval_kg:.0f} kg",
                     font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
            row=0, column=1, sticky="e"
        )
        pb = ctk.CTkProgressBar(inner, progress_color=color, fg_color=COLORS["bg_input"], height=8)
        pb.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        pb.set(pct)
        ctk.CTkLabel(inner, text=f"{pct*100:.1f} {L('dash_burr_life')}",
                     font=FONTS["caption"], text_color=color).grid(
            row=2, column=0, columnspan=2, sticky="e"
        )

    def _empty_state(self, row, msg, color=None):
        color = color or COLORS["text_muted"]
        ctk.CTkLabel(self, text=msg, font=FONTS["body"],
                     text_color=color).grid(row=row, column=0, pady=8, padx=24, sticky="w")

    def _ai_cluster_section(self, row, extractions):
        """Render K-Means extraction cluster cards."""
        try:
            from logic.ai.shot_cluster import cluster_extractions
            from ui.ai_widgets import ClusterSection

            clusters = cluster_extractions(list(extractions))
            section = ClusterSection(self, clusters)
            section.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 8))
        except Exception as e:
            ctk.CTkLabel(
                self,
                text=f"{L('dash_clusters_err')}: {e}",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).grid(row=row, column=0, sticky="w", padx=24, pady=4)
