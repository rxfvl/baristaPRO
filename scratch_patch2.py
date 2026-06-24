import re

file_path = r"c:\Users\minec\Desktop\baristaPRO\ui\dial_in_journal.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "Equipment" not in content:
    content = content.replace(
        "from db.models import Bean, BeanBatch, ExtractionLog",
        "from db.models import Bean, BeanBatch, ExtractionLog, Equipment"
    )

# Split the content to only replace inside ExtractionForm
parts = content.split("class ExtractionForm(ctk.CTkFrame):")
if len(parts) != 2:
    print("Could not find ExtractionForm!")
    exit(1)

extraction_form_code = parts[1]

# 2. _build and helpers
pattern = r"    def _build\(self\):.*?    def _on_flavor_select\(self, selected: list\):"

new_code = """    def _build(self):
        row = 0
        title_txt = "Nueva Extracción / New Shot" if self.mode == "new" else "Detalle de Extracción / Shot Detail"
        ctk.CTkLabel(self, text=title_txt, font=FONTS["heading"], text_color=COLORS["text_primary"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        with get_session() as db:
            from sqlalchemy.orm import joinedload
            batches = db.query(BeanBatch).options(joinedload(BeanBatch.bean)).filter_by(is_archived=False).all()
            bean_options = ["(Sin café / No bean)"] + [
                f"{b.id}: {b.bean.name} — {b.bean.roaster} (Tueste: {b.roast_date})" for b in batches
            ]
            equipments = db.query(Equipment).filter(Equipment.type == "Grinder").all()
            eq_options = ["(Sin equipo / No equip)"] + [f"{e.id}: {e.brand} {e.model}" for e in equipments]

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ctk.CTkLabel(top_frame, text="Café / Bean", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self._bean_combo = ctk.CTkComboBox(
            top_frame, values=bean_options, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_card"], width=300, command=self._on_bean_select
        )
        self._bean_combo.pack(fill="x", pady=(0, 4))
        
        self._history_hint_label = ctk.CTkLabel(
            top_frame, text="Selecciona un café para ver la última molienda usada", font=FONTS["caption"], text_color=COLORS["text_muted"]
        )
        self._history_hint_label.pack(anchor="w")

        # TABS
        self.tabs = ctk.CTkTabview(self, fg_color=COLORS["bg_secondary"], segmented_button_selected_color=COLORS["accent"], segmented_button_selected_hover_color=COLORS["accent_hover"])
        self.tabs.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        
        t_recipe = self.tabs.add("Receta")
        t_sensory = self.tabs.add("Sensorial")
        t_notes = self.tabs.add("Notas & IA")

        # RECIPE
        t_recipe.columnconfigure((0, 1), weight=1)
        r_row = 0
        for key, label, default, col in [("dose_in", "Dosis (g)", "0", 0), ("yield_out", "Rendimiento (g)", "0", 1)]:
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

        for key, label, default, col in [("extraction_time", "Tiempo (s)", "27", 0), ("water_temp", "Temperatura (°C)", "93", 1)]:
            self._label_entry(t_recipe, r_row, col, key, label, default)
        r_row += 1

        eq_frame = ctk.CTkFrame(t_recipe, fg_color="transparent")
        eq_frame.grid(row=r_row, column=0, sticky="ew", padx=(8, 8), pady=2)
        ctk.CTkLabel(eq_frame, text="Molino", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self._equipment_combo = ctk.CTkComboBox(eq_frame, values=eq_options, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self._equipment_combo.pack(fill="x")
        self._label_entry(t_recipe, r_row, 1, "grind_size", "Molida", "")
        r_row += 1

        for key, label, default, col in [("pressure", "Presión (bar)","9.0", 0), ("pre_infusion_time", "Pre-infusión (s)", "0", 1)]:
            self._label_entry(t_recipe, r_row, col, key, label, default)
        r_row += 1
        
        self._label_entry(t_recipe, r_row, 0, "timestamp", "Fecha (YYYY-MM-DD HH:MM:SS)", "")
        r_row += 1

        # SENSORY
        t_sensory.columnconfigure((0, 1), weight=1)
        s_row = 0
        sensory_labels = [("acidity", "Acidez"), ("sweetness", "Dulzor"), ("body", "Cuerpo"), ("bitterness","Amargor")]
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
        ctk.CTkCheckBox(t_sensory, text="★ Receta Óptima", variable=self._locked_var, font=FONTS["body"], text_color=COLORS["accent"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], checkmark_color="#000000").grid(row=s_row, column=0, columnspan=2, sticky="w", pady=(0, 12), padx=8)

        # NOTES
        t_notes.columnconfigure(0, weight=1)
        ctk.CTkLabel(t_notes, text="Notas adicionales", font=FONTS["label"], text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        self._entries["notes"] = ctk.CTkTextbox(t_notes, height=80, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self._entries["notes"].grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        # ACTION BUTTONS
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ctk.CTkButton(btn_row, text="Guardar / Save", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], text_color="#000000", corner_radius=CORNER_RADIUS["button"], command=self._save).pack(side="right", padx=(8, 0))
        if self.ext:
            ctk.CTkButton(btn_row, text="Duplicar / Duplicate", fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"], corner_radius=CORNER_RADIUS["button"], command=self._duplicate_shot).pack(side="right", padx=(8, 0))
            ctk.CTkButton(btn_row, text="✕ Eliminar / Delete", fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"], text_color=COLORS["danger"], corner_radius=CORNER_RADIUS["button"], command=self._delete).pack(side="right")

    def _duplicate_shot(self):
        self.ext = None
        self.mode = "new"
        self._entries["timestamp"].delete(0, "end")
        from tkinter import messagebox
        messagebox.showinfo("Duplicado", "La receta ha sido duplicada. Haz tus cambios y guarda para crear una nueva entrada.")

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

    def _on_flavor_select(self, selected: list):"""

extraction_form_code = re.sub(pattern, new_code, extraction_form_code, flags=re.DOTALL)

# 3. _populate additions
populate_pattern = r"        set_entry\(\"notes\",             ext\.notes\)"
populate_new = """        set_entry("notes",             ext.notes)
        set_entry("tds",               ext.tds)
        set_entry("ey",                ext.ey)
        if ext.timestamp:
            set_entry("timestamp", ext.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        
        if ext.equipment_id and hasattr(self, "_equipment_combo"):
            for opt in self._equipment_combo.cget("values"):
                if opt.startswith(f"{ext.equipment_id}:"):
                    self._equipment_combo.set(opt)
                    break
"""
extraction_form_code = extraction_form_code.replace(populate_pattern, populate_new)

content = parts[0] + "class ExtractionForm(ctk.CTkFrame):" + extraction_form_code

# We lost the earlier multi_replace_file_content changes for save, load_list and delete because we restored from history!
# So we must re-apply the fixes to _save, _delete and _load_list!

content = content.replace('''    def _load_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
        query_str = self._filter_var.get().lower() if hasattr(self, "_filter_var") else ""

        with get_session() as db:
            from sqlalchemy.orm import joinedload
            extractions = (
                db.query(ExtractionLog)
                .options(joinedload(ExtractionLog.bean_batch).joinedload(BeanBatch.bean))
                .order_by(ExtractionLog.timestamp.desc())
                .all()
            )

            for i, ext in enumerate(extractions):
                if ext.bean_batch and ext.bean_batch.bean:
                    bdate = ext.bean_batch.roast_date.strftime("%d/%m") if ext.bean_batch.roast_date else "—"
                    bean_name = f"{ext.bean_batch.bean.name} ({bdate})"
                else:
                    bean_name = "Sin café / No bean"
                
                if query_str and query_str not in bean_name.lower() and query_str not in (ext.flavor_notes or "").lower():
                    continue
                self._ext_list_card(i, ext, bean_name)''', '''    def _load_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
        query_str = self._filter_var.get().lower() if hasattr(self, "_filter_var") else ""

        with get_session() as db:
            from sqlalchemy.orm import joinedload
            extractions = (
                db.query(ExtractionLog)
                .options(joinedload(ExtractionLog.bean_batch).joinedload(BeanBatch.bean))
                .order_by(ExtractionLog.timestamp.desc())
                .limit(100)
                .all()
            )

            count = 0
            for i, ext in enumerate(extractions):
                if ext.bean_batch and ext.bean_batch.bean:
                    bdate = ext.bean_batch.roast_date.strftime("%d/%m") if ext.bean_batch.roast_date else "—"
                    bean_name = f"{ext.bean_batch.bean.name} ({bdate})"
                else:
                    bean_name = "Sin café / No bean"
                
                if query_str and query_str not in bean_name.lower() and query_str not in (ext.flavor_notes or "").lower():
                    continue
                self._ext_list_card(count, ext, bean_name)
                count += 1
            if count == 0:
                ctk.CTkLabel(self.list_scroll, text="No se encontraron extracciones", text_color=COLORS["text_muted"]).pack(pady=20)''')

content = content.replace('''        with get_session() as db:
            if self.ext:
                ext = db.get(ExtractionLog, self.ext.id)
            else:
                ext = ExtractionLog()
                db.add(ext)

            ext.bean_batch_id      = bean_id
            ext.dose_in            = dose
            ext.yield_out          = yld
            ext.extraction_time    = time_
            ext.water_temp         = temp
            ext.grind_size         = self._get("grind_size") or None
            ext.pressure           = press
            ext.pre_infusion_time  = pre
            ext.acidity            = int(self._get("acidity") or 5)
            ext.sweetness          = int(self._get("sweetness") or 5)
            ext.body               = int(self._get("body") or 5)
            ext.bitterness         = int(self._get("bitterness") or 5)
            ext.flavor_notes       = flavor_notes or None
            notes_w = self._entries.get("notes")
            ext.notes              = notes_w.get("1.0", "end").strip() if isinstance(notes_w, ctk.CTkTextbox) else None
            ext.score              = round(self._score_var.get(), 1)
            ext.is_locked          = self._locked_var.get()
            ext.timestamp          = datetime.now()

            # Decrement batch stock
            if bean_id:
                batch = db.get(BeanBatch, bean_id)
                if batch and dose > 0:
                    batch.stock_grams = max(batch.stock_grams - dose, 0)

            db.commit()''', '''        with get_session() as db:
            if self.ext:
                ext = db.get(ExtractionLog, self.ext.id)
                if ext.bean_batch_id != bean_id:
                    # Devuelve la dosis al batch anterior
                    if ext.bean_batch_id:
                        old_batch = db.get(BeanBatch, ext.bean_batch_id)
                        if old_batch:
                            old_batch.stock_grams += ext.dose_in
                    old_dose = 0.0
                else:
                    old_dose = ext.dose_in
            else:
                ext = ExtractionLog()
                db.add(ext)
                old_dose = 0.0

            ext.bean_batch_id      = bean_id
            ext.dose_in            = dose
            ext.yield_out          = yld
            ext.extraction_time    = time_
            ext.water_temp         = temp
            ext.grind_size         = self._get("grind_size") or None
            ext.pressure           = press
            ext.pre_infusion_time  = pre
            ext.acidity            = int(self._get("acidity") or 5)
            ext.sweetness          = int(self._get("sweetness") or 5)
            ext.body               = int(self._get("body") or 5)
            ext.bitterness         = int(self._get("bitterness") or 5)
            ext.flavor_notes       = flavor_notes or None
            notes_w = self._entries.get("notes")
            ext.notes              = notes_w.get("1.0", "end").strip() if isinstance(notes_w, ctk.CTkTextbox) else None
            ext.score              = round(self._score_var.get(), 1)
            ext.is_locked          = self._locked_var.get()
            
            # Additional advanced fields
            tds_val = self._get("tds")
            ext.tds = float(tds_val) if tds_val else None
            ey_val = self._get("ey")
            ext.ey = float(ey_val) if ey_val else None
            
            eq_selection = self._equipment_combo.get() if hasattr(self, "_equipment_combo") else ""
            if eq_selection and ":" in eq_selection:
                ext.equipment_id = int(eq_selection.split(":")[0])
            else:
                ext.equipment_id = None
            
            # Allow manual timestamp edit
            ts_str = self._get("timestamp")
            if ts_str:
                from datetime import datetime
                try:
                    ext.timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            elif not self.ext:
                from datetime import datetime
                ext.timestamp = datetime.now()

            # Adjust batch stock
            if bean_id:
                batch = db.get(BeanBatch, bean_id)
                if batch and dose > 0:
                    dose_diff = dose - old_dose
                    batch.stock_grams = max(batch.stock_grams - dose_diff, 0)

            db.commit()''')

content = content.replace('''    def _delete(self):
        if not self.ext:
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar esta extracción? / Delete this extraction?"):
            with get_session() as db:
                ext = db.get(ExtractionLog, self.ext.id)
                if ext:
                    db.delete(ext)
                    db.commit()
            if self.on_delete:
                self.on_delete()
            elif self.on_save:
                self.on_save()''', '''    def _delete(self):
        if not self.ext:
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar esta extracción? / Delete this extraction?"):
            with get_session() as db:
                ext = db.get(ExtractionLog, self.ext.id)
                if ext:
                    # Restore batch stock
                    if ext.bean_batch_id and ext.dose_in and ext.dose_in > 0:
                        batch = db.get(BeanBatch, ext.bean_batch_id)
                        if batch:
                            batch.stock_grams += ext.dose_in
                    db.delete(ext)
                    db.commit()
            if self.on_delete:
                self.on_delete()
            elif self.on_save:
                self.on_save()''')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patch 2 applied successfully")
