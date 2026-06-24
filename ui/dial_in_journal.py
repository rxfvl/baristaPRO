# ui/dial_in_journal.py — Extraction Bitácora with interactive flavor wheel

import math
import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date
from tkinter import messagebox, filedialog
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label
from logic.api_client import api
from logic.export import export_bean_report, REPORTLAB_AVAILABLE


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.colors as mcolors

# ── Flavor wheel categories ───────────────────────────────────────────────────
FLAVOR_CATEGORIES = [
    ("Frutal",    "#F4C060", ["Cítrico", "Rojos", "Tropical", "Manzana", "Melocotón"]),
    ("Dulce",     "#E8703A", ["Caramelo", "Chocolate", "Miel", "Vainilla", "Panela"]),
    ("Floral",    "#E8A8D0", ["Jazmín", "Rosa", "Hibisco", "Lavanda", "Azahar"]),
    ("Nueces",    "#A0784C", ["Almendra", "Avellana", "Cacahuate", "Nuez", "Pecana"]),
    ("Especias",  "#7A5C3C", ["Canela", "Clavo", "Pimienta", "Jengibre", "Anís"]),
    ("Terroso",   "#688C50", ["Madera", "Tabaco", "Hierba", "Tierra", "Cedro"]),
]

class FlavorWheelMatplotlib(ctk.CTkFrame):
    """High-quality interactive flavor wheel using Matplotlib."""
    
    def __init__(self, parent, on_select=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.on_select = on_select
        self._selected = set()
        
        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.fig.patch.set_facecolor(COLORS["bg_card"])
        self.ax = self.fig.add_subplot(111, polar=True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        self._build_data()
        self._draw_wheel()

    def _build_data(self):
        # Prepare data for plotting
        self.theta = []
        self.radii = []
        self.colors = []
        self.labels = []
        self.types = []
        self.base_colors = []
        
        n_cats = len(FLAVOR_CATEGORIES)
        cat_width = 2 * np.pi / n_cats
        
        for i, (cat, color, subs) in enumerate(FLAVOR_CATEGORIES):
            cat_start = i * cat_width
            # Inner ring
            self.theta.append(cat_start + cat_width / 2)
            self.radii.append(0.5)  # Width of inner bar
            self.colors.append(color)
            self.labels.append(cat)
            self.types.append("cat")
            self.base_colors.append(color)
            
            # Outer ring
            n_subs = len(subs)
            sub_width = cat_width / n_subs
            for j, sub in enumerate(subs):
                sub_start = cat_start + j * sub_width
                self.theta.append(sub_start + sub_width / 2)
                self.radii.append(1.0)  # Width of outer bar
                self.colors.append(color)
                self.labels.append(sub)
                self.types.append("sub")
                self.base_colors.append(color)

    def _dim_color(self, hex_color: str) -> str:
        rgb = mcolors.hex2color(hex_color)
        return mcolors.to_hex([c * 0.35 for c in rgb])

    def _draw_wheel(self):
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        
        n_cats = len(FLAVOR_CATEGORIES)
        cat_width = 2 * np.pi / n_cats
        
        # We will draw patches manually or using bar
        self.wedges = []
        
        for i, (cat, color, subs) in enumerate(FLAVOR_CATEGORIES):
            cat_start = i * cat_width
            cat_end = cat_start + cat_width
            
            # Subcategories (outer ring)
            n_subs = len(subs)
            sub_width = cat_width / n_subs
            for j, sub in enumerate(subs):
                sub_start = cat_start + j * sub_width
                sub_end = sub_start + sub_width
                
                is_selected = sub in self._selected
                facecolor = color if is_selected else self._dim_color(color)
                
                bar = self.ax.bar(
                    x=(sub_start + sub_end) / 2,
                    height=0.4,
                    width=sub_width * 0.98,
                    bottom=0.6,
                    color=facecolor,
                    edgecolor=COLORS["bg_card"],
                    linewidth=1
                )
                self.wedges.append({"type": "sub", "label": sub, "bar": bar[0], "start": sub_start, "end": sub_end, "bottom": 0.6, "top": 1.0})
                
                # Text
                text_angle = (sub_start + sub_end) / 2
                screen_angle = (90 - np.degrees(text_angle)) % 360
                rotation = screen_angle - 180 if 90 < screen_angle <= 270 else screen_angle
                self.ax.text(
                    text_angle, 0.8, sub,
                    ha='center', va='center', rotation=rotation,
                    fontsize=7, color='white' if is_selected else '#888888',
                    fontweight='bold' if is_selected else 'normal'
                )

            # Category (inner ring)
            is_selected = cat in self._selected
            facecolor = color if is_selected else self._dim_color(color)
            bar = self.ax.bar(
                x=(cat_start + cat_end) / 2,
                height=0.4,
                width=cat_width * 0.98,
                bottom=0.2,
                color=facecolor,
                edgecolor=COLORS["bg_card"],
                linewidth=1
            )
            self.wedges.append({"type": "cat", "label": cat, "bar": bar[0], "start": cat_start, "end": cat_end, "bottom": 0.2, "top": 0.6})
            
            # Text
            text_angle = (cat_start + cat_end) / 2
            screen_angle = (90 - np.degrees(text_angle)) % 360
            rotation = screen_angle - 180 if 90 < screen_angle <= 270 else screen_angle
            self.ax.text(
                text_angle, 0.4, cat,
                ha='center', va='center', rotation=rotation,
                fontsize=8, color='white' if is_selected else '#AAAAAA',
                fontweight='bold'
            )
            
        # Center circle
        self.ax.bar(0, 0.2, width=2*np.pi, bottom=0, color=COLORS["accent"])
        self.ax.text(0, 0, "☕", ha='center', va='center', fontsize=16)
        
        self.ax.set_ylim(0, 1.05)
        self.canvas.draw_idle()

    def _on_click(self, event):
        if event.inaxes != self.ax:
            return
            
        r = event.ydata
        theta = event.xdata % (2 * np.pi)
        
        for w in self.wedges:
            if w["bottom"] <= r <= w["top"]:
                if w["start"] <= theta <= w["end"]:
                    label = w["label"]
                    if label in self._selected:
                        self._selected.remove(label)
                    else:
                        self._selected.add(label)
                    
                    self._draw_wheel()
                    if self.on_select:
                        self.on_select(sorted(self._selected))
                    break

    def get_selected(self) -> list:
        return sorted(self._selected)

    def set_selected(self, labels: list):
        self._selected = set(labels)
        self._draw_wheel()


class DialInJournalView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        self._selected_ext_id = None
        self._build()

    def _build(self):
        self._build_header()
        self._build_left_panel()
        self._build_right_panel()
        self._load_list()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 0))
        header.columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text=L("journal_title"),
                     font=FONTS["display"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text=L("journal_subtitle"),
                     font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
            row=1, column=0, sticky="w"
        )
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e")
        ctk.CTkButton(
            btn_frame, text=f"+ {L('new_shot')}",
            font=FONTS["body"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            command=self._new_extraction
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btn_frame, text="📄 Exportar PDF",
            font=FONTS["body"], fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._export_pdf
        ).pack(side="right")

    def _build_left_panel(self):
        self.left = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.left.grid(row=1, column=0, sticky="nsew", padx=(24, 8), pady=16)
        self.left.columnconfigure(0, weight=1)
        self.left.rowconfigure(1, weight=1)

        # Filter bar
        filter_row = ctk.CTkFrame(self.left, fg_color="transparent")
        filter_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        filter_row.columnconfigure(0, weight=1)
        self._filter_var = ctk.StringVar()
        self._filter_var.trace_add("write", lambda *_: self._load_list())
        ctk.CTkEntry(
            filter_row, textvariable=self._filter_var,
            placeholder_text=L("search"),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"]
        ).grid(row=0, column=0, sticky="ew")

        self.list_scroll = ctk.CTkScrollableFrame(
            self.left, fg_color="transparent", corner_radius=0
        )
        self.list_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.list_scroll.columnconfigure(0, weight=1)

    def _build_right_panel(self):
        self.right = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12
        )
        self.right.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=16)
        self.right.columnconfigure(0, weight=1)
        self._show_empty_right()

    def _show_empty_right(self):
        for w in self.right.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.right,
            text="← Selecciona una extracción o crea una nueva\n← Select a shot or create a new one",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        ).pack(expand=True, pady=60)

    # ── List panel ──────────────────────────────────────────────────────────────
    def _load_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
        query_str = self._filter_var.get().lower() if hasattr(self, "_filter_var") else ""

        try:
            extractions = api.get_extractions()[:100]
            # Extractions from API have bean_batch and bean nested already
        except Exception as e:
            extractions = []
            print(f"Error fetching extractions: {e}")

            count = 0
            for i, ext in enumerate(extractions):
                if ext.bean_batch and ext.bean_batch.bean:
                    bdate = ext.bean_batch.roast_date.strftime("%d/%m") if ext.bean_batch.roast_date else "—"
                    bean_name = f"{ext.bean_batch.bean.name} ({bdate})"
                else:
                    bean_name = L("no_bean")
                
                if query_str and query_str not in bean_name.lower() and query_str not in (ext.flavor_notes or "").lower():
                    continue
                self._ext_list_card(count, ext, bean_name)
                count += 1
            if count == 0:
                ctk.CTkLabel(self.list_scroll, text="No se encontraron extracciones", text_color=COLORS["text_muted"]).pack(pady=20)

    def _ext_list_card(self, idx, ext, bean_name):
        is_locked = ext.is_locked
        bg = COLORS["bg_card"] if not is_locked else "#1E1500"
        card = ctk.CTkFrame(self.list_scroll, fg_color=bg, corner_radius=8)
        card.grid(row=idx, column=0, sticky="ew", padx=4, pady=(0, 4))
        card.columnconfigure(0, weight=1)
        card.bind("<Button-1>", lambda e, eid=ext.id: self._select_extraction(eid))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)
        inner.columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")
        star = "★ " if is_locked else ""
        ctk.CTkLabel(top_row, text=f"{star}{bean_name}", font=FONTS["body"],
                     text_color=COLORS["accent"] if is_locked else COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top_row, text=f"⭐ {ext.score:.1f}", font=FONTS["small"],
                     text_color=COLORS["text_muted"]).pack(side="right")

        bot_row = ctk.CTkFrame(inner, fg_color="transparent")
        bot_row.pack(fill="x")
        ctk.CTkLabel(bot_row, text=f"{ext.dose_in}g → {ext.yield_out}g | {ext.ratio_str} | {ext.extraction_time}s",
                     font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(side="left")
        ctk.CTkLabel(bot_row, text=ext.timestamp.strftime("%d/%m/%y"),
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(side="right")

        for w in [card, inner, top_row, bot_row]:
            w.bind("<Button-1>", lambda e, eid=ext.id: self._select_extraction(eid))

    def _select_extraction(self, ext_id: int):
        self._selected_ext_id = ext_id
        try:
            extractions = api.get_extractions()
            ext = next((e for e in extractions if e.id == ext_id), None)
            if ext:
                self._show_extraction_form(ext, mode="view")
        except Exception as e:
            print(f"Error selecting extraction: {e}")

    def _new_extraction(self):
        self._selected_ext_id = None
        self._show_extraction_form(None, mode="new")

    def _show_extraction_form(self, ext, mode="new"):
        for w in self.right.winfo_children():
            w.destroy()
        ExtractionForm(
            self.right, ext, mode, app=self.app, 
            on_save=self._on_form_save, on_delete=self._on_form_delete
        )

    def _on_form_save(self):
        self._load_list()
        self.app.refresh_view("dashboard")

    def _on_form_delete(self):
        self._load_list()
        self.app.refresh_view("dashboard")
        self._show_empty_right()

    def _export_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("ReportLab no instalado", "Instala ReportLab: pip install reportlab")
            return
        with get_session() as db:
            beans = db.query(Bean).filter_by(is_archived=False).all()
        if not beans:
            messagebox.showinfo("Sin datos", "No hay cafés registrados.")
            return
        ExportBeanSelector(self, beans)


class ExtractionForm(ctk.CTkFrame):
    """Embedded form for a single extraction entry."""

    def __init__(self, parent, ext, mode, app, on_save, on_delete=None):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=12, pady=12)
        self.ext       = ext
        self.mode      = mode
        self.app       = app
        self.on_save   = on_save
        self.on_delete = on_delete
        self._entries = {}
        self._flavor_wheel = None
        self.columnconfigure((0, 1), weight=1)
        self._build()
        if ext and mode == "view":
            self._populate(ext)

    def _build(self):
        row = 0
        title_txt = get_label("new_shot") if self.mode == "new" else get_label("shot_detail")
        ctk.CTkLabel(self, text=title_txt, font=FONTS["heading"], text_color=COLORS["text_primary"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        try:
            beans = api.get_beans()
            batches = []
            for b in beans:
                if hasattr(b, 'batches'):
                    for batch in b.batches:
                        batch.bean = b
                        if not getattr(batch, 'is_archived', False):
                            batches.append(batch)
            
            bean_options = [L("no_bean")] + [
                f"{b.id}: {b.bean.name} — {b.bean.roaster} (Tueste: {b.roast_date})" for b in batches
            ]
            equipments = api.get_equipment()
            grinders = [e for e in equipments if getattr(e, 'type', '') == "Grinder"]
            eq_options = [L("no_equip")] + [f"{e.id}: {e.brand} {e.model}" for e in grinders]
        except Exception:
            bean_options = [L("no_bean")]
            eq_options = [L("no_equip")]

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ctk.CTkLabel(top_frame, text=get_label("bean"), font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self._bean_combo = ctk.CTkComboBox(
            top_frame, values=bean_options, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_card"], width=300, command=self._on_bean_select
        )
        self._bean_combo.pack(fill="x", pady=(0, 4))
        
        self._history_hint_label = ctk.CTkLabel(
            top_frame, text=L("no_history"), font=FONTS["caption"], text_color=COLORS["text_muted"]
        )
        self._history_hint_label.pack(anchor="w")

        # STOCK INDICATOR
        stock_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(4, 0))
        self._stock_bar = ctk.CTkProgressBar(stock_frame, progress_color=COLORS["accent"], height=8)
        self._stock_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._stock_bar.set(0)
        self._stock_label = ctk.CTkLabel(stock_frame, text="", font=FONTS["small"], text_color=COLORS["text_muted"])
        self._stock_label.pack(side="right")

        # TABS
        self.tabs = ctk.CTkTabview(self, fg_color=COLORS["bg_secondary"], segmented_button_selected_color=COLORS["accent"], segmented_button_selected_hover_color=COLORS["accent_hover"])
        self.tabs.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        
        t_recipe = self.tabs.add("Receta")
        t_sensory = self.tabs.add("Sensorial")
        t_notes = self.tabs.add("Notas & IA")

        # RECIPE
        t_recipe.columnconfigure((0, 1), weight=1)
        r_row = 0
        for key, label, default, col in [("dose_in", L("ext_dose"), "0", 0), ("yield_out", L("ext_yield"), "0", 1)]:
            self._label_entry(t_recipe, r_row, col, key, label, default)
        r_row += 1

        ratio_row = ctk.CTkFrame(t_recipe, fg_color="transparent")
        ratio_row.grid(row=r_row, column=0, columnspan=2, sticky="ew", pady=(0, 8), padx=8)
        ctk.CTkLabel(ratio_row, text="Ratio:", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(side="left")
        self._ratio_label = ctk.CTkLabel(ratio_row, text="1:2.0", font=FONTS["subhead"], text_color=COLORS["accent"])
        self._ratio_label.pack(side="left", padx=8)
        r_row += 1

        for key in ("dose_in", "yield_out"):
            entry = self._entries.get(key)
            if entry: entry.bind("<KeyRelease>", lambda e: self._update_ratio())

        for key, label, default, col in [("extraction_time", L("ext_time"), "27", 0), ("water_temp", L("ext_temp"), "93", 1)]:
            self._label_entry(t_recipe, r_row, col, key, label, default)
        r_row += 1

        eq_frame = ctk.CTkFrame(t_recipe, fg_color="transparent")
        eq_frame.grid(row=r_row, column=0, sticky="ew", padx=(8, 8), pady=2)
        ctk.CTkLabel(eq_frame, text=get_label("eq_grinder"), font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self._equipment_combo = ctk.CTkComboBox(eq_frame, values=eq_options, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self._equipment_combo.pack(fill="x")
        self._label_entry(t_recipe, r_row, 1, "grind_size", L("ext_grind"), "")
        r_row += 1

        for key, label, default, col in [("pressure", L("ext_pressure"),"9.0", 0), ("pre_infusion_time", L("ext_preinfusion"), "0", 1)]:
            self._label_entry(t_recipe, r_row, col, key, label, default)
        r_row += 1
        
        date_frame = ctk.CTkFrame(t_recipe, fg_color="transparent")
        date_frame.grid(row=r_row, column=0, sticky="ew", padx=(8, 8), pady=2)
        date_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(date_frame, text="Fecha (YYYY-MM-DD)", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        
        entry_row = ctk.CTkFrame(date_frame, fg_color="transparent")
        entry_row.pack(fill="x")
        entry_row.columnconfigure(0, weight=1)
        
        entry = ctk.CTkEntry(entry_row, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._entries["timestamp"] = entry
        
        ctk.CTkButton(entry_row, text="▼", width=28, font=FONTS["small"], fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"], command=lambda: self._shift_date(-1)).grid(row=0, column=1, padx=(0, 2))
        ctk.CTkButton(entry_row, text="Hoy", width=40, font=FONTS["small"], fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"], command=self._set_today).grid(row=0, column=2, padx=(0, 2))
        ctk.CTkButton(entry_row, text="▲", width=28, font=FONTS["small"], fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"], command=lambda: self._shift_date(1)).grid(row=0, column=3)
        r_row += 1

        # SENSORY
        t_sensory.columnconfigure((0, 1), weight=1)
        s_row = 0
        sensory_labels = [("acidity", L("ext_acidity")), ("sweetness", L("ext_sweetness")), ("body", L("ext_body")), ("bitterness",L("ext_bitterness"))]
        for i, (key, label) in enumerate(sensory_labels):
            col = i % 2
            if i % 2 == 0 and i > 0: s_row += 1
            self._slider_field(t_sensory, s_row, col, key, label)
        s_row += 1

        for key, label, default, col in [("tds", "TDS %", "", 0), ("ey", "EY %", "", 1)]:
            self._label_entry(t_sensory, s_row, col, key, label, default)
        s_row += 1

        wheel_frame = ctk.CTkFrame(t_sensory, fg_color=COLORS["bg_card"], corner_radius=12)
        wheel_frame.grid(row=s_row, column=0, columnspan=2, pady=(8, 8), sticky="ew", padx=8)
        self._flavor_wheel = FlavorWheelMatplotlib(wheel_frame, on_select=self._on_flavor_select)
        self._flavor_wheel.pack(padx=10, pady=10, fill="both", expand=True)
        s_row += 1

        self._flavor_label = ctk.CTkLabel(t_sensory, text="Selecciona sabores", font=FONTS["small"], text_color=COLORS["text_muted"])
        self._flavor_label.grid(row=s_row, column=0, columnspan=2, sticky="w", padx=8)
        s_row += 1

        score_row = ctk.CTkFrame(t_sensory, fg_color="transparent")
        score_row.grid(row=s_row, column=0, columnspan=2, sticky="ew", pady=(8, 8), padx=8)
        ctk.CTkLabel(score_row, text="Score (1-10):", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(side="left")
        self._score_var = ctk.DoubleVar(value=7.0)
        score_slider = ctk.CTkSlider(score_row, from_=1, to=10, variable=self._score_var, number_of_steps=18, progress_color=COLORS["accent"], button_color=COLORS["accent"])
        score_slider.pack(side="left", padx=(8, 8), fill="x", expand=True)
        self._score_display = ctk.CTkLabel(score_row, text="7.0", font=FONTS["subhead"], text_color=COLORS["accent"])
        self._score_display.pack(side="left")
        self._score_var.trace_add("write", lambda *_: self._score_display.configure(text=f"{self._score_var.get():.1f}"))
        s_row += 1

        self._locked_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(t_sensory, text=L("ext_locked"), variable=self._locked_var, font=FONTS["body"], text_color=COLORS["accent"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], checkmark_color="#000000").grid(row=s_row, column=0, columnspan=2, sticky="w", pady=(0, 12), padx=8)

        # NOTES
        t_notes.columnconfigure(0, weight=1)
        ctk.CTkLabel(t_notes, text=L("ext_notes"), font=FONTS["label"], text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        self._entries["notes"] = ctk.CTkTextbox(t_notes, height=80, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self._entries["notes"].grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        # ACTION BUTTONS
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ctk.CTkButton(btn_row, text=L("save"), fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], text_color="#000000", corner_radius=CORNER_RADIUS["button"], command=self._save).pack(side="right", padx=(8, 0))
        if self.ext:
            ctk.CTkButton(btn_row, text=get_label("duplicate"), fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"], corner_radius=CORNER_RADIUS["button"], command=self._duplicate_shot).pack(side="right", padx=(8, 0))
            ctk.CTkButton(btn_row, text=L("delete"), fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"], text_color=COLORS["danger"], corner_radius=CORNER_RADIUS["button"], command=self._delete).pack(side="right")

    def _duplicate_shot(self):
        self.ext = None
        self.mode = "new"
        self._entries["timestamp"].delete(0, "end")
        from tkinter import messagebox
        messagebox.showinfo("Duplicado", "La receta ha sido duplicada. Haz tus cambios y guarda para crear una nueva entrada.")

    def _shift_date(self, days: int):
        from datetime import datetime, timedelta
        val = self._entries["timestamp"].get()
        if val:
            try:
                dt = datetime.strptime(val, "%Y-%m-%d")
                dt += timedelta(days=days)
                self._entries["timestamp"].delete(0, "end")
                self._entries["timestamp"].insert(0, dt.strftime("%Y-%m-%d"))
            except ValueError:
                pass

    def _set_today(self):
        from datetime import datetime
        self._entries["timestamp"].delete(0, "end")
        self._entries["timestamp"].insert(0, datetime.now().strftime("%Y-%m-%d"))

    def _label_entry(self, parent, row, col, key, label, default=""):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=(8, 8), pady=2)
        frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        entry = ctk.CTkEntry(frame, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        entry.pack(fill="x")
        if default: entry.insert(0, default)
        self._entries[key] = entry

    def _slider_field(self, parent, row, col, key, label):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=(8, 8), pady=4)
        frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        var = ctk.IntVar(value=5)
        val_label = ctk.CTkLabel(frame, text="5/10", font=FONTS["small"], text_color=COLORS["accent"])
        slider = ctk.CTkSlider(frame, from_=1, to=10, variable=var, number_of_steps=9, progress_color=COLORS["accent"], button_color=COLORS["accent"])
        slider.pack(fill="x")
        val_label.pack(anchor="e")
        var.trace_add("write", lambda *_, v=var, l=val_label: l.configure(text=f"{v.get()}/10"))
        self._entries[key] = var

    def _update_ratio(self):
        try:
            dose = float(self._entries["dose_in"].get())
            yld  = float(self._entries["yield_out"].get())
            if dose > 0:
                ratio = yld/dose
                color = COLORS["accent"]
                if ratio < 1.5: color = "#4DA6FF" # Blue
                elif ratio > 2.5: color = "#FF7F50" # Orange
                else: color = "#2ECC71" # Green
                self._ratio_label.configure(text=f"1:{ratio:.2f}", text_color=color)
        except (ValueError, KeyError):
            pass

    def _on_flavor_select(self, selected: list):
        if selected:
            self._flavor_label.configure(text=", ".join(selected))
        else:
            self._flavor_label.configure(text=L("select_flavors"))

    def _on_bean_select(self, choice: str):
        if not choice or ":" not in choice:
            self._history_hint_label.configure(text=L("no_history"))
            if hasattr(self, '_stock_bar'):
                self._stock_bar.set(0)
                self._stock_label.configure(text="")
            return
            
        try:
            bean_id = int(choice.split(":")[0])
        except ValueError:
            return
            
        try:
            beans = api.get_beans()
            batch = None
            for b in beans:
                if hasattr(b, 'batches'):
                    batch = next((bt for bt in b.batches if getattr(bt, 'id', None) == bean_id), None)
                    if batch:
                        batch.bean = b
                        break

            if batch:
                extractions = api.get_extractions()
                batch_exts = [e for e in extractions if getattr(e, 'bean_batch_id', None) == bean_id]
                consumed = sum(getattr(e, 'dose_in', 0) for e in batch_exts)
                stock = getattr(batch, 'stock_grams', 0)
                total_initial = consumed + stock
                
                if total_initial > 0:
                    pct = stock / total_initial
                else:
                    pct = 0
                
                if hasattr(self, '_stock_bar'):
                    color = COLORS["accent"]
                    if pct < 0.2: color = COLORS.get("danger", "#FF4444")
                    elif pct < 0.5: color = "#F4C060" # Orange/Yellow
                    self._stock_bar.configure(progress_color=color)
                    self._stock_bar.set(pct)
                    self._stock_label.configure(text=f"{stock:.1f}g ({int(pct*100)}%)")
            
            last_ext_batch = None
            last_ext_bean = None
            if batch:
                # API returns extractions ordered by date desc
                last_ext_batch = next((e for e in extractions if getattr(e, 'bean_batch_id', None) == bean_id and e.id != getattr(self.ext, 'id', None)), None)
                last_ext_bean = next((e for e in extractions if e.bean_batch and getattr(e.bean_batch, 'bean_id', None) == getattr(batch, 'bean_id', None) and getattr(e, 'bean_batch_id', None) != bean_id), None)
            
            text_lines = []
            if last_ext_batch:
                grind = getattr(last_ext_batch, 'grind_size', "N/A") or "N/A"
                text_lines.append(f"Último (este lote): Molienda {grind} | {last_ext_batch.dose_in}g → {last_ext_batch.yield_out}g en {last_ext_batch.extraction_time}s (⭐ {last_ext_batch.score:.1f})")
            
            if last_ext_bean:
                grind = getattr(last_ext_bean, 'grind_size', "N/A") or "N/A"
                text_lines.append(f"Último (otros lotes): Molienda {grind} | {last_ext_bean.dose_in}g → {last_ext_bean.yield_out}g en {last_ext_bean.extraction_time}s (⭐ {last_ext_bean.score:.1f})")
                
            if text_lines:
                self._history_hint_label.configure(text="\n".join(text_lines), text_color=COLORS["accent"])
            else:
                self._history_hint_label.configure(text=L("first_shot"), text_color=COLORS["text_muted"])
        except Exception as e:
            print(f"Error checking bean history: {e}")

    def _populate(self, ext):
        def set_entry(key, val):
            w = self._entries.get(key)
            if w is None or val is None:
                return
            if isinstance(w, ctk.CTkEntry):
                w.delete(0, "end")
                w.insert(0, str(val))
            elif isinstance(w, ctk.IntVar):
                w.set(int(val))
            elif isinstance(w, ctk.CTkTextbox):
                w.delete("1.0", "end")
                w.insert("1.0", str(val))

        if ext.bean_batch_id:
            for opt in self._bean_combo.cget("values"):
                if opt.startswith(f"{ext.bean_batch_id}:"):
                    self._bean_combo.set(opt)
                    break

        set_entry("dose_in",           ext.dose_in)
        set_entry("yield_out",         ext.yield_out)
        set_entry("extraction_time",   ext.extraction_time)
        set_entry("water_temp",        ext.water_temp)
        set_entry("grind_size",        ext.grind_size)
        set_entry("pressure",          ext.pressure)
        set_entry("pre_infusion_time", ext.pre_infusion_time)
        set_entry("acidity",           ext.acidity)
        set_entry("sweetness",         ext.sweetness)
        set_entry("body",              ext.body)
        set_entry("bitterness",        ext.bitterness)
        set_entry("notes",             ext.notes)
        set_entry("tds",               ext.tds)
        set_entry("ey",                ext.ey)
        if ext.timestamp:
            set_entry("timestamp", ext.timestamp.strftime("%Y-%m-%d"))
        
        if ext.equipment_id and hasattr(self, "_equipment_combo"):
            for opt in self._equipment_combo.cget("values"):
                if opt.startswith(f"{ext.equipment_id}:"):
                    self._equipment_combo.set(opt)
                    break

        self._score_var.set(ext.score)
        self._locked_var.set(ext.is_locked)
        self._update_ratio()

        if ext.flavor_notes and self._flavor_wheel:
            flavors = [f.strip() for f in ext.flavor_notes.split(",") if f.strip()]
            self._flavor_wheel.set_selected(flavors)
            self._on_flavor_select(flavors)

        shot_params = {
            "dose_in":           ext.dose_in,
            "yield_out":         ext.yield_out,
            "extraction_time":   ext.extraction_time,
            "water_temp":        ext.water_temp,
            "pressure":          ext.pressure,
            "pre_infusion_time": ext.pre_infusion_time,
            "acidity":           ext.acidity,
            "sweetness":         ext.sweetness,
            "body":              ext.body,
            "bitterness":        ext.bitterness,
        }
        self._show_ai_suggestion(shot_params)

    def _get(self, key, default=None):
        w = self._entries.get(key)
        if w is None:
            return default
        if isinstance(w, ctk.CTkEntry):
            return w.get().strip()
        if isinstance(w, ctk.IntVar):
            return w.get()
        if isinstance(w, ctk.CTkTextbox):
            return w.get("1.0", "end").strip()
        return default

    def _save(self):
        try:
            dose  = float(self._get("dose_in") or 0)
            yld   = float(self._get("yield_out") or 0)
            time_ = int(self._get("extraction_time") or 0)
            temp  = float(self._get("water_temp") or 93)
            press = float(self._get("pressure") or 9)
            pre   = float(self._get("pre_infusion_time") or 0)
        except ValueError:
            messagebox.showerror("Error", L("err_numeric"))
            return

        bean_id = None
        bean_selection = self._bean_combo.get()
        if bean_selection and ":" in bean_selection:
            try:
                bean_id = int(bean_selection.split(":")[0])
            except ValueError:
                pass

        flavor_notes = ", ".join(self._flavor_wheel.get_selected()) if self._flavor_wheel else ""

        notes_w = self._entries.get("notes")
        notes_val = notes_w.get("1.0", "end").strip() if isinstance(notes_w, ctk.CTkTextbox) else None
        tds_val = self._get("tds")
        ey_val = self._get("ey")
        
        eq_selection = self._equipment_combo.get() if hasattr(self, "_equipment_combo") else ""
        equipment_id = int(eq_selection.split(":")[0]) if eq_selection and ":" in eq_selection else None

        ext_data = {
            "bean_batch_id": bean_id,
            "dose_in": dose,
            "yield_out": yld,
            "extraction_time": time_,
            "water_temp": temp,
            "grind_size": self._get("grind_size") or None,
            "pressure": press,
            "pre_infusion_time": pre,
            "acidity": int(self._get("acidity") or 5),
            "sweetness": int(self._get("sweetness") or 5),
            "body": int(self._get("body") or 5),
            "bitterness": int(self._get("bitterness") or 5),
            "flavor_notes": flavor_notes or None,
            "notes": notes_val,
            "score": round(self._score_var.get(), 1),
            "is_locked": self._locked_var.get(),
            "tds": float(tds_val) if tds_val else None,
            "ey": float(ey_val) if ey_val else None,
            "equipment_id": equipment_id
        }

        ts_str = self._get("timestamp")
        if ts_str:
            ext_data["timestamp"] = ts_str + "T00:00:00"

        if self.ext:
            # TODO: update api.update_extraction
            pass
        else:
            api.create_extraction(ext_data)

        # Update progress bar UI
        self._on_bean_select(self._bean_combo.get())

        # ── IA: Retrain advisor in background and show loading ──────────────
        shot_params = {
            "dose_in":           dose,
            "yield_out":         yld,
            "extraction_time":   time_,
            "water_temp":        temp,
            "pressure":          press,
            "pre_infusion_time": pre,
            "acidity":           int(self._get("acidity") or 5),
            "sweetness":         int(self._get("sweetness") or 5),
            "body":              int(self._get("body") or 5),
            "bitterness":        int(self._get("bitterness") or 5),
        }
        
        self._show_training_indicator()

        import threading
        self._training_done = False

        def _train_task():
            import time
            time.sleep(0.8) # Ensure the animation is visible so the user knows it's thinking
            self._retrain_advisor_sync()
            self._training_done = True

        t = threading.Thread(target=_train_task, daemon=True)
        t.start()
        
        self._check_training_loop(t, shot_params)

        if self.on_save:
            self.on_save()

    def _check_training_loop(self, t, shot_params):
        if self._training_done:
            self._show_ai_suggestion(shot_params)
        else:
            self.after(100, self._check_training_loop, t, shot_params)

    def _show_training_indicator(self):
        """Render a temporary loading card while AI retrains."""
        for w in self.winfo_children():
            if getattr(w, "_is_ai_card", False):
                w.destroy()
                
        loading_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        loading_card._is_ai_card = True
        loading_card.grid(row=99, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
        ctk.CTkLabel(
            loading_card,
            text=L("training_ai"),
            font=FONTS["small"],
            text_color=COLORS["accent"]
        ).pack(pady=20)

    def _show_ai_suggestion(self, params: dict):
        """Render ShotAdvisorCard below the form after saving."""
        # Remove any previous card (including loading indicator)
        for w in self.winfo_children():
            if getattr(w, "_is_ai_card", False):
                w.destroy()
        try:
            from ui.ai_widgets import ShotAdvisorCard
            card = ShotAdvisorCard(self, params)
            card._is_ai_card = True
            # Place it at a very high row index so it always appears at the bottom
            card.grid(row=99, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        except Exception as e:
            print(f"[AI widget] {e}")

    def _retrain_advisor_sync(self):
        """Retrain the Shot Advisor with updated real data synchronously."""
        import pandas as pd
        from logic.ai.shot_advisor import advisor

        try:
            with get_session() as db:
                exts = db.query(ExtractionLog).all()
            if not exts:
                return
            df = pd.DataFrame([{
                "dose_in":           e.dose_in,
                "yield_out":         e.yield_out,
                "extraction_time":   e.extraction_time,
                "water_temp":        e.water_temp,
                "pressure":          e.pressure,
                "pre_infusion_time": e.pre_infusion_time,
                "score":             e.score,
            } for e in exts])
            advisor.train(df)
        except Exception as e:
            print(f"[AI retrain] {e}")

    def _delete(self):
        from logic.api_client import api
        if not self.ext:
            return
        if messagebox.askyesno(L("delete"), L("del_shot")):
            if api.delete_extraction(self.ext.id):
                if self.on_delete:
                    self.on_delete()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la extracción")


class ExportBeanSelector(ctk.CTkToplevel):
    def __init__(self, parent, beans):
        super().__init__(parent)
        self.beans = beans
        self.title(L("export_pdf"))
        self.geometry("400x300")
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()

        ctk.CTkLabel(self, text="Selecciona el café a exportar\\nSelect a bean to export",
                     font=FONTS["body"], text_color=COLORS["text_primary"]).pack(pady=(20, 8))

        self._combo = ctk.CTkComboBox(
            self,
            values=[f"{b.id}: {b.name} — {b.roaster}" for b in beans],
            fg_color=COLORS["bg_input"], dropdown_fg_color=COLORS["bg_card"],
            width=340
        )
        self._combo.pack(pady=8)

        ctk.CTkButton(
            self, text="📄 Exportar PDF",
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            command=self._do_export
        ).pack(pady=16)

    def _do_export(self):
        selection = self._combo.get()
        if ":" not in selection:
            return
        bean_id = int(selection.split(":")[0])
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"espressolab_{bean_id}.pdf"
        )
        if not output_path:
            return
        with get_session() as db:
            bean = db.get(Bean, bean_id)
            exts = (
                db.query(ExtractionLog)
                .join(BeanBatch, ExtractionLog.bean_batch_id == BeanBatch.id)
                .filter(BeanBatch.bean_id == bean_id)
                .order_by(ExtractionLog.timestamp.desc())
                .all()
            )
            try:
                export_bean_report(bean, exts, output_path)
                messagebox.showinfo("✓ PDF Exportado", f"Guardado en:\\n{output_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        self.destroy()
