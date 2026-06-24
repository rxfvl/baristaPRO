# ui/equipment.py — Equipment & Maintenance module

import customtkinter as ctk
from datetime import date, timedelta
from tkinter import messagebox
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label
from logic.api_client import api

EQUIPMENT_TYPES = [L("eq_machine"), L("eq_grinder"), L("eq_other")]

DEFAULT_MAINTENANCE_TASKS = {
    L("eq_machine"): [
        (L("task_chem_backflush"), 7),
        (L("task_water_backflush"), 1),
        (L("task_descaling"), 90),
        ("Cambio de juntas (Gaskets)", 365),
        (L("task_water_filter"), 180),
        (L("task_group_clean"), 1),
    ],
    L("eq_grinder"): [
        (L("task_burr_clean"), 30),
        (L("task_gen_clean"), 7),
        (L("task_calibration"), 90),
    ],
}


class EquipmentView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        self._build_header()
        self._build_equipment_panel()
        self._build_maintenance_panel()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 0))
        header.columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text=L("eq_title"),
                     font=FONTS["display"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text=L("eq_subtitle"),
                     font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
            row=1, column=0, sticky="w"
        )
        ctk.CTkButton(
            header, text=L("add_eq"),
            font=FONTS["body"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            command=self._open_add_equipment
        ).grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_equipment_panel(self):
        self.equip_scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12
        )
        self.equip_scroll.grid(row=1, column=0, sticky="nsew", padx=(24, 8), pady=16)
        self.equip_scroll.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.equip_scroll, text=L("reg_eq"),
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 8)
        )
        self._refresh_equipment()

    def _refresh_equipment(self):
        # Clear except header
        children = self.equip_scroll.winfo_children()
        for w in children[1:]:
            w.destroy()

        try:
            equipment = api.get_equipment()
        except Exception:
            equipment = []

        if not equipment:
            ctk.CTkLabel(
                self.equip_scroll,
                text="No hay equipos registrados.\nAdd your espresso machine and grinder.",
                font=FONTS["body"], text_color=COLORS["text_muted"]
            ).grid(row=1, column=0, pady=40)
            return

        for i, equip in enumerate(equipment):
            self._equipment_card(i + 1, equip)

    def _equipment_card(self, row_idx, equip):
        is_grinder = "Grinder" in equip.type or "Molino" in equip.type
        pct = equip.burr_life_percent if is_grinder else 0

        card = ctk.CTkFrame(self.equip_scroll, fg_color=COLORS["bg_card"], corner_radius=10)
        card.grid(row=row_idx, column=0, sticky="ew", padx=8, pady=(0, 8))
        card.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)
        inner.columnconfigure(0, weight=1)

        # Title row
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        icon = "⚙️" if is_grinder else "☕"
        ctk.CTkLabel(top, text=f"{icon} {equip.brand} {equip.model}",
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).pack(side="left")
        type_badge = ctk.CTkLabel(
            top, text=f" {equip.type} ",
            font=FONTS["caption"], text_color=COLORS["accent"],
            fg_color=COLORS["accent_dark"], corner_radius=8
        )
        type_badge.pack(side="left", padx=8)

        # Purchase date
        if equip.purchase_date:
            ctk.CTkLabel(inner, text=f"Adquirido: {equip.purchase_date.strftime('%d %b %Y')}",
                         font=FONTS["small"], text_color=COLORS["text_muted"]).grid(
                row=1, column=0, sticky="w", pady=(4, 0)
            )

        # Grinder: burr life bar
        if is_grinder:
            ctk.CTkFrame(inner, height=1, fg_color=COLORS["border"]).grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=8
            )
            burr_row = ctk.CTkFrame(inner, fg_color="transparent")
            burr_row.grid(row=3, column=0, columnspan=2, sticky="ew")
            burr_row.columnconfigure(0, weight=1)

            color = (COLORS["success"] if pct < 0.7
                     else COLORS["warning"] if pct < 0.9
                     else COLORS["danger"])

            ctk.CTkLabel(burr_row, text=L("burr_life"),
                         font=FONTS["label"], text_color=COLORS["text_muted"]).grid(
                row=0, column=0, sticky="w"
            )
            ctk.CTkLabel(burr_row,
                         text=f"{equip.total_kg_ground:.1f} / {equip.burr_change_interval_kg:.0f} kg ({pct*100:.1f}%)",
                         font=FONTS["body"], text_color=color).grid(
                row=0, column=1, sticky="e"
            )
            pb = ctk.CTkProgressBar(burr_row, progress_color=color,
                                    fg_color=COLORS["bg_input"], height=8, corner_radius=4)
            pb.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 6))
            pb.set(pct)

            # Quick add kg
            add_row = ctk.CTkFrame(inner, fg_color="transparent")
            add_row.grid(row=4, column=0, columnspan=2, sticky="ew")
            ctk.CTkLabel(add_row, text=L("add_kg"),
                         font=FONTS["label"], text_color=COLORS["text_muted"]).pack(side="left")
            kg_entry = ctk.CTkEntry(add_row, width=70, fg_color=COLORS["bg_input"],
                                    border_color=COLORS["border"], placeholder_text="kg")
            kg_entry.pack(side="left", padx=6)
            ctk.CTkButton(
                add_row, text="+ Añadir", width=70, height=26, font=FONTS["small"],
                fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                corner_radius=6,
                command=lambda eid=equip.id, e=kg_entry: self._add_kg_ground(eid, e)
            ).pack(side="left")

        # Action buttons
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ctk.CTkButton(
            btn_row, text="+ Tarea Mantenimiento", width=160, height=28, font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6,
            command=lambda eid=equip.id, et=equip.type: self._add_maintenance_task(eid, et)
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            btn_row, text="✕", width=28, height=28, font=FONTS["small"],
            fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"],
            text_color=COLORS["danger"], corner_radius=6,
            command=lambda eid=equip.id: self._delete_equipment(eid)
        ).pack(side="left")

    def _build_maintenance_panel(self):
        self.maint_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12
        )
        self.maint_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=16)
        self.maint_frame.columnconfigure(0, weight=1)
        self.maint_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.maint_frame, text=L("maint_cal"),
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 8)
        )
        self.maint_scroll = ctk.CTkScrollableFrame(
            self.maint_frame, fg_color="transparent", corner_radius=0
        )
        self.maint_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.maint_scroll.columnconfigure(0, weight=1)
        self._refresh_maintenance()

    def _refresh_maintenance(self):
        for w in self.maint_scroll.winfo_children():
            w.destroy()

        try:
            tasks = api.get_maintenance_tasks()
            # Sort by next_due_date
            tasks.sort(key=lambda t: getattr(t, 'next_due_date', ''))
            equipment = api.get_equipment()
        except Exception:
            tasks = []
            equipment = []

        equip_map = {e.id: e for e in equipment}

        if not tasks:
            ctk.CTkLabel(self.maint_scroll,
                         text="No hay tareas de mantenimiento.\nAdd equipment to generate tasks.",
                         font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=24)
            return

        for i, task in enumerate(tasks):
            equip = equip_map.get(task.equipment_id)
            self._task_card(i, task, equip)

    def _task_card(self, idx, task, equip):
        is_overdue = task.is_overdue
        is_urgent  = task.is_urgent

        if is_overdue:
            bg, color = COLORS["danger_dim"], COLORS["danger"]
            status_text = L("dash_overdue")
        elif is_urgent:
            bg, color = COLORS["warning_dim"], COLORS["warning"]
            days = task.days_until_due
            status_text = L("in_days").format(days)
        else:
            bg, color = COLORS["bg_card"], COLORS["text_muted"]
            days = getattr(task, 'days_until_due', None)
            status_text = L("in_days").format(days) if days is not None else "—"

        card = ctk.CTkFrame(self.maint_scroll, fg_color=bg, corner_radius=8)
        card.grid(row=idx, column=0, sticky="ew", padx=8, pady=(0, 5))
        card.columnconfigure(1, weight=1)

        # Color strip
        strip = ctk.CTkFrame(card, width=4, fg_color=color, corner_radius=0)
        strip.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="ew", pady=8, padx=(0, 8))
        content.columnconfigure(0, weight=1)

        ctk.CTkLabel(content, text=task.task_name, font=FONTS["body"],
                     text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
        equip_name = f"{equip.brand} {equip.model}" if equip else "—"
        ctk.CTkLabel(content, text=equip_name, font=FONTS["small"],
                     text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w")
        last_done = task.last_done_date.strftime("%d/%m/%y") if task.last_done_date else L("never")
        ctk.CTkLabel(content, text=f"Último: {last_done}  •  Cada {task.frequency_days}d",
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(
            row=2, column=0, sticky="w"
        )

        # Status + Done button
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=2, padx=(0, 8), pady=8, sticky="e")
        ctk.CTkLabel(right, text=status_text, font=FONTS["small"], text_color=color).pack()
        ctk.CTkButton(
            right, text="✓ Hecho", width=72, height=26, font=FONTS["small"],
            fg_color=COLORS["success_dim"], hover_color=COLORS["success"],
            text_color=COLORS["success"], corner_radius=6,
            command=lambda tid=task.id: self._mark_done(tid)
        ).pack(pady=(4, 0))

    # ── Actions ─────────────────────────────────────────────────────────────────
    def _open_add_equipment(self):
        EquipmentDialog(self, mode="add", on_save=self._on_equip_saved)

    def _on_equip_saved(self):
        self._refresh_equipment()
        self._refresh_maintenance()
        self.app.refresh_view("dashboard")

    def _delete_equipment(self, equip_id: int):
        if messagebox.askyesno("Eliminar", L("del_eq")):
            api.delete_equipment(equip_id)
            self._on_equip_saved()

    def _add_kg_ground(self, equip_id: int, entry: ctk.CTkEntry):
        try:
            kg = float(entry.get())
        except ValueError:
            messagebox.showerror("Error", L("err_num2"))
            return
        api.add_kg_ground(equip_id, kg)
        entry.delete(0, "end")
        self._on_equip_saved()

    def _add_maintenance_task(self, equip_id: int, equip_type: str):
        MaintenanceTaskDialog(self, equip_id=equip_id, equip_type=equip_type,
                              on_save=self._refresh_maintenance)

    def _mark_done(self, task_id: int):
        api.mark_maintenance_task_done(task_id)
        self._refresh_maintenance()
        self.app.refresh_view("dashboard")


class EquipmentDialog(ctk.CTkToplevel):
    def __init__(self, parent, mode="add", on_save=None):
        super().__init__(parent)
        self.mode    = mode
        self.on_save = on_save
        self.title(L("add_eq"))
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()
        self._entries = {}
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.columnconfigure((0, 1), weight=1)
        row = 0

        ctk.CTkLabel(scroll, text=L("add_eq"),
                     font=FONTS["heading"], text_color=COLORS["text_primary"]).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )
        row += 1

        # Type
        ctk.CTkLabel(scroll, text=L("eq_type"), font=FONTS["label"],
                     text_color=COLORS["text_muted"]).grid(row=row, column=0, sticky="w")
        row += 1
        self._type_combo = ctk.CTkComboBox(
            scroll, values=EQUIPMENT_TYPES,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        self._type_combo.set(EQUIPMENT_TYPES[0])
        self._type_combo.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        row += 1

        fields = [
            ("brand",                   L("eq_brand"),                      0, row),
            ("model",                   L("eq_model"),                     1, row),
        ]
        for key, label, col, r in fields:
            self._field(scroll, r, col, key, label)
        row += 1

        self._field(scroll, row, 0, "purchase_date", "Fecha compra (YYYY-MM-DD)")
        row += 1

        ctk.CTkLabel(scroll, text=L("only_grinder"),
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(8, 2)
        )
        row += 1

        self._field(scroll, row, 0, "burr_change_interval_kg", "Intervalo cambio muelas (kg)")
        self._entries["burr_change_interval_kg"].delete(0, "end")
        self._entries["burr_change_interval_kg"].insert(0, "500")
        row += 1

        # Add default tasks checkbox
        self._add_tasks_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            scroll, text=L("add_def_tasks"),
            variable=self._add_tasks_var, font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            checkmark_color="#000000"
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=8)
        row += 1

        ctk.CTkLabel(scroll, text=L("ext_notes"), font=FONTS["label"],
                     text_color=COLORS["text_muted"]).grid(
            row=row, column=0, columnspan=2, sticky="w"
        )
        row += 1
        self._entries["notes"] = ctk.CTkTextbox(
            scroll, height=60, fg_color=COLORS["bg_input"], border_color=COLORS["border"]
        )
        self._entries["notes"].grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        # Buttons
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ctk.CTkButton(
            btn_row, text=L("save"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", command=self._save
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="Cancelar", fg_color=COLORS["bg_input"],
                      command=self.destroy).pack(side="right")

    def _field(self, parent, row, col, key, label):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=(0, 8) if col == 0 else (8, 0), pady=4)
        frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        entry = ctk.CTkEntry(frame, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        entry.pack(fill="x")
        self._entries[key] = entry

    def _get(self, key):
        w = self._entries.get(key)
        if w is None:
            return ""
        if isinstance(w, ctk.CTkTextbox):
            return w.get("1.0", "end").strip()
        return w.get().strip()

    def _save(self):
        brand = self._get("brand")
        model = self._get("model")
        if not brand or not model:
            messagebox.showerror("Error", L("err_brand"))
            return

        purchase_date = None
        raw = self._get("purchase_date")
        if raw:
            try:
                purchase_date = date.fromisoformat(raw)
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

        equip_type = self._type_combo.get()
        try:
            burr_kg = float(self._get("burr_change_interval_kg") or 500)
        except ValueError:
            burr_kg = 500

        equip_data = {
            "type": equip_type,
            "brand": brand,
            "model": model,
            "purchase_date": purchase_date.isoformat() if purchase_date else None,
            "burr_change_interval_kg": burr_kg,
            "notes": self._get("notes") or None,
        }
        
        equip = api.create_equipment(equip_data)

        # Add default maintenance tasks
        if equip and self._add_tasks_var.get():
            defaults = None
            for type_key, tasks in DEFAULT_MAINTENANCE_TASKS.items():
                if type_key.split("/")[0].strip() in equip_type:
                    defaults = tasks
                    break

            if defaults:
                for task_name, freq_days in defaults:
                    task_data = {
                        "equipment_id": equip.id,
                        "task_name": task_name,
                        "frequency_days": freq_days,
                        "next_due_date": (date.today() + timedelta(days=freq_days)).isoformat(),
                    }
                    api.create_maintenance_task(task_data)

        if self.on_save:
            self.on_save()
        self.destroy()


class MaintenanceTaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, equip_id, equip_type, on_save=None):
        super().__init__(parent)
        self.equip_id   = equip_id
        self.equip_type = equip_type
        self.on_save    = on_save
        self.title("Nueva Tarea de Mantenimiento")
        self.geometry("420x320")
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()
        self._build()

    def _build(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=L("new_task"),
                     font=FONTS["heading"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(frame, text=L("task_name"), font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        self._name_entry = ctk.CTkEntry(frame, fg_color=COLORS["bg_input"],
                                         border_color=COLORS["border"])
        self._name_entry.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame, text=L("freq_days"), font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        self._freq_entry = ctk.CTkEntry(frame, fg_color=COLORS["bg_input"],
                                         border_color=COLORS["border"])
        self._freq_entry.insert(0, "7")
        self._freq_entry.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame, text="Próximo vencimiento (YYYY-MM-DD, opcional)",
                     font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self._due_entry = ctk.CTkEntry(frame, fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"])
        self._due_entry.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(
            btn_row, text=L("save"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", command=self._save
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="Cancelar", fg_color=COLORS["bg_input"],
                      command=self.destroy).pack(side="right")

    def _save(self):
        name = self._name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", L("err_name"))
            return
        try:
            freq = int(self._freq_entry.get())
        except ValueError:
            freq = 7

        due_date = None
        raw = self._due_entry.get().strip()
        if raw:
            try:
                due_date = date.fromisoformat(raw)
            except ValueError:
                due_date = date.today() + timedelta(days=freq)
        else:
            due_date = date.today() + timedelta(days=freq)

        task_data = {
            "equipment_id": self.equip_id,
            "task_name": name,
            "frequency_days": freq,
            "next_due_date": due_date.isoformat(),
        }
        api.create_maintenance_task(task_data)

        if self.on_save:
            self.on_save()
        self.destroy()
