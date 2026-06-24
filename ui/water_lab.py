# ui/water_lab.py — Water Chemistry Laboratory module

import customtkinter as ctk
from tkinter import messagebox
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label
from logic.api_client import api
from logic.water_calc import (
    calculate_water_recipe, format_recipe_card,
    PRESET_PROFILES, SCA_GH_MIN, SCA_GH_MAX,
    SCA_KH_MIN, SCA_KH_MAX, SCA_TDS_MIN, SCA_TDS_MAX
)


class WaterLabView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._result = None
        self._build()

    def _build(self):
        self._build_header()
        self._build_calculator()
        self._build_saved_panel()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 0))
        ctk.CTkLabel(header, text=L("water_title"),
                     font=FONTS["display"], text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=L("water_sub"),
            font=FONTS["small"], text_color=COLORS["text_muted"]
        ).pack(anchor="w")

    def _build_calculator(self):
        self.calc_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12
        )
        self.calc_frame.grid(row=1, column=0, sticky="nsew", padx=(24, 8), pady=16)
        self.calc_frame.columnconfigure(0, weight=1)

        row = 0

        # Preset selector
        ctk.CTkLabel(self.calc_frame, text=L("base_prof"),
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=row, column=0, sticky="w", pady=(0, 8)
        )
        row += 1

        preset_names = list(PRESET_PROFILES.keys())
        self._preset_combo = ctk.CTkComboBox(
            self.calc_frame, values=preset_names,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_preset_select
        )
        self._preset_combo.set(preset_names[0])
        self._preset_combo.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        row += 1

        self._preset_desc = ctk.CTkLabel(
            self.calc_frame, text=PRESET_PROFILES[preset_names[0]]["description"],
            font=FONTS["caption"], text_color=COLORS["text_muted"], wraplength=300
        )
        self._preset_desc.grid(row=row, column=0, sticky="w", pady=(0, 16))
        row += 1

        # ── SCA Reference bar ─────────────────────────────────────────────────
        sca_card = ctk.CTkFrame(self.calc_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        sca_card.grid(row=row, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(sca_card, text="📋 SCA Ideal Ranges",
                     font=FONTS["label"], text_color=COLORS["accent"]).pack(anchor="w", padx=12, pady=(8, 2))
        sca_text = (
            f"GH: {SCA_GH_MIN}–{SCA_GH_MAX} ppm  •  "
            f"KH: {SCA_KH_MIN}–{SCA_KH_MAX} ppm  •  "
            f"TDS: {SCA_TDS_MIN}–{SCA_TDS_MAX} ppm"
        )
        ctk.CTkLabel(sca_card, text=sca_text, font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=12, pady=(0, 8))
        row += 1

        # ── Sliders ───────────────────────────────────────────────────────────
        ctk.CTkLabel(self.calc_frame, text=L("target_param"),
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=row, column=0, sticky="w", pady=(0, 8)
        )
        row += 1

        self._gh_var  = ctk.DoubleVar(value=68)
        self._kh_var  = ctk.DoubleVar(value=40)
        self._tds_var = ctk.IntVar(value=150)
        self._vol_var = ctk.DoubleVar(value=1.0)
        self._ca_var  = ctk.BooleanVar(value=False)

        row = self._param_slider(row, L("gh_hard"),
                                 self._gh_var, 10, 200, SCA_GH_MIN, SCA_GH_MAX)
        row = self._param_slider(row, L("kh_alk"),
                                 self._kh_var, 5, 120, SCA_KH_MIN, SCA_KH_MAX)
        row = self._param_slider(row, "TDS Total (ppm, referencia)",
                                 self._tds_var, 30, 300, SCA_TDS_MIN, SCA_TDS_MAX)

        # Volume
        vol_row = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        vol_row.grid(row=row, column=0, sticky="ew", pady=4)
        ctk.CTkLabel(vol_row, text=L("vol_prep"),
                     font=FONTS["label"], text_color=COLORS["text_muted"]).pack(side="left")
        self._vol_entry = ctk.CTkEntry(
            vol_row, width=60, fg_color=COLORS["bg_input"], border_color=COLORS["border"]
        )
        self._vol_entry.insert(0, "1.0")
        self._vol_entry.pack(side="left", padx=8)
        row += 1

        # Optional Ca toggle
        ctk.CTkCheckBox(
            self.calc_frame,
            text=L("inc_cacl2"),
            variable=self._ca_var, font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            checkmark_color="#000000",
            command=self._calculate
        ).grid(row=row, column=0, sticky="w", pady=8)
        row += 1

        # Calculate button
        ctk.CTkButton(
            self.calc_frame, text=L("calc_btn"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            font=FONTS["subhead"], height=40,
            command=self._calculate
        ).grid(row=row, column=0, sticky="ew", pady=(8, 16))
        row += 1

        # ── Result card ───────────────────────────────────────────────────────
        self._result_frame = ctk.CTkFrame(
            self.calc_frame, fg_color=COLORS["bg_card"], corner_radius=12
        )
        self._result_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(self._result_frame, text=L("result_lbl"),
                     font=FONTS["subhead"], text_color=COLORS["text_muted"]).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        self._result_inner = ctk.CTkFrame(self._result_frame, fg_color="transparent")
        self._result_inner.pack(fill="x", padx=16, pady=(0, 12))
        self._show_result_placeholder()
        row += 1

        # Save recipe button
        ctk.CTkButton(
            self.calc_frame, text=L("save_recipe"),
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._save_recipe
        ).grid(row=row, column=0, sticky="ew")

    def _param_slider(self, row, label, var, from_, to, sca_min, sca_max):
        frame = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=4)
        frame.columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=label, font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        val_label = ctk.CTkLabel(top, text=f"{var.get():.0f}",
                                 font=FONTS["body"], text_color=COLORS["accent"])
        val_label.pack(side="right")

        slider = ctk.CTkSlider(
            frame, from_=from_, to=to, variable=var,
            progress_color=COLORS["accent"], button_color=COLORS["accent"],
            command=lambda v, vl=val_label: (vl.configure(text=f"{v:.0f}"), self._calculate())
        )
        slider.pack(fill="x")

        sca_hint = ctk.CTkLabel(
            frame, text=f"SCA óptimo: {sca_min}–{sca_max} ppm",
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        )
        sca_hint.pack(anchor="e")
        return row + 1

    def _show_result_placeholder(self):
        for w in self._result_inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(self._result_inner,
                     text="Presiona 'Calcular' para ver la receta\nPress 'Calculate' to see recipe",
                     font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=12)

    def _on_preset_select(self, selection):
        profile = PRESET_PROFILES.get(selection, {})
        self._gh_var.set(profile.get("target_gh_ppm", 68))
        self._kh_var.set(profile.get("target_kh_ppm", 40))
        self._tds_var.set(profile.get("target_tds_ppm", 150))
        self._ca_var.set(profile.get("use_calcium", False))
        self._preset_desc.configure(text=profile.get("description", ""))
        self._calculate()

    def _calculate(self, *_):
        try:
            vol = float(self._vol_entry.get())
        except (ValueError, AttributeError):
            vol = 1.0

        result = calculate_water_recipe(
            target_gh_ppm  = self._gh_var.get(),
            target_kh_ppm  = self._kh_var.get(),
            target_tds_ppm = int(self._tds_var.get()),
            use_calcium    = self._ca_var.get(),
        )
        self._result = result
        card = format_recipe_card(result, volume_liters=vol)
        self._render_result(card, vol)

    def _render_result(self, card: dict, vol: float):
        for w in self._result_inner.winfo_children():
            w.destroy()

        # Mineral amounts (highlighted)
        minerals = [
            ("MgSO₄·7H₂O\n(Epsom Salt)", f"{card['epsom_g']:.3f} g", True),
            ("NaHCO₃\n(Bicarbonato)", f"{card['bicarb_g']:.3f} g", True),
            ("CaCl₂·2H₂O\n(Calcio)", f"{card['cacl2_g']:.3f} g", card['cacl2_g'] > 0),
        ]
        for col, (mineral, amount, show) in enumerate(minerals):
            if not show:
                continue
            m_card = ctk.CTkFrame(self._result_inner, fg_color=COLORS["bg_secondary"],
                                   corner_radius=8)
            m_card.grid(row=0, column=col, padx=4, pady=4, sticky="ew")
            self._result_inner.columnconfigure(col, weight=1)
            ctk.CTkLabel(m_card, text=amount, font=FONTS["heading"],
                         text_color=COLORS["accent"]).pack(pady=(8, 0))
            ctk.CTkLabel(m_card, text=f"por {vol:.1f}L destilada", font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack()
            ctk.CTkLabel(m_card, text=mineral, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(pady=(0, 8))

        # Resulting chemistry with SCA compliance indicators
        result_grid = ctk.CTkFrame(self._result_inner, fg_color="transparent")
        result_grid.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        result_grid.columnconfigure((0, 1, 2), weight=1)

        checks = [
            ("GH real",  f"{card['gh_ppm']:.1f} ppm", card['gh_ok']),
            ("KH real",  f"{card['kh_ppm']:.1f} ppm", card['kh_ok']),
            ("TDS est.", f"{card['tds_ppm']} ppm",     card['tds_ok']),
        ]
        for col, (lbl, val, ok) in enumerate(checks):
            color = COLORS["success"] if ok else COLORS["warning"]
            icon  = "✓" if ok else "⚠"
            frame = ctk.CTkFrame(result_grid, fg_color="transparent")
            frame.grid(row=0, column=col, padx=4)
            ctk.CTkLabel(frame, text=f"{icon} {lbl}", font=FONTS["caption"],
                         text_color=color).pack()
            ctk.CTkLabel(frame, text=val, font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack()

    def _build_saved_panel(self):
        self.saved_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12
        )
        self.saved_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=16)
        self.saved_frame.columnconfigure(0, weight=1)
        self.saved_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.saved_frame, text=L("saved_recipes"),
                     font=FONTS["subhead"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 8)
        )
        self._saved_scroll = ctk.CTkScrollableFrame(
            self.saved_frame, fg_color="transparent", corner_radius=0
        )
        self._saved_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self._saved_scroll.columnconfigure(0, weight=1)
        self._load_saved()

    def _load_saved(self):
        for w in self._saved_scroll.winfo_children():
            w.destroy()
        try:
            recipes = api.get_water_recipes()
            recipes.sort(key=lambda x: getattr(x, 'created_at', ''), reverse=True)
        except Exception as e:
            recipes = []
            print(f"Error fetching water recipes: {e}")

        if not recipes:
            ctk.CTkLabel(self._saved_scroll,
                         text="Aún no hay recetas guardadas\nNo saved recipes yet",
                         font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=24)
            return

        for i, recipe in enumerate(recipes):
            self._saved_card(i, recipe)

    def _saved_card(self, idx, recipe):
        card = ctk.CTkFrame(self._saved_scroll, fg_color=COLORS["bg_card"], corner_radius=8)
        card.grid(row=idx, column=0, sticky="ew", padx=8, pady=(0, 6))
        card.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        inner.columnconfigure(0, weight=1)

        ctk.CTkLabel(inner, text=recipe.name, font=FONTS["subhead"],
                     text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")

        info = (
            f"GH: {recipe.target_gh_ppm:.0f}ppm  "
            f"KH: {recipe.target_kh_ppm:.0f}ppm  "
            f"TDS: {recipe.target_tds_ppm}ppm"
        )
        ctk.CTkLabel(inner, text=info, font=FONTS["small"],
                     text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w")

        minerals = (
            f"Epsom: {recipe.mg_sulfate_g_per_l:.3f}g/L  "
            f"Bicarb: {recipe.sodium_bicarb_g_per_l:.3f}g/L"
        )
        if recipe.calcium_chloride_g_per_l:
            minerals += f"  CaCl₂: {recipe.calcium_chloride_g_per_l:.3f}g/L"
        ctk.CTkLabel(inner, text=minerals, font=FONTS["mono"],
                     text_color=COLORS["accent"]).grid(row=2, column=0, sticky="w", pady=(4, 0))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.grid(row=0, column=1, rowspan=3, sticky="e")
        ctk.CTkButton(
            btns, text="Cargar", width=60, height=26, font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, command=lambda r=recipe: self._load_recipe(r)
        ).pack(pady=2)
        ctk.CTkButton(
            btns, text="✕", width=28, height=26, font=FONTS["small"],
            fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"],
            text_color=COLORS["danger"], corner_radius=6,
            command=lambda r=recipe: self._delete_recipe(r.id)
        ).pack(pady=2)

    def _load_recipe(self, recipe):
        self._gh_var.set(recipe.target_gh_ppm)
        self._kh_var.set(recipe.target_kh_ppm)
        self._tds_var.set(recipe.target_tds_ppm)
        self._preset_combo.set(L("custom_preset"))
        self._calculate()

    def _delete_recipe(self, recipe_id: int):
        if messagebox.askyesno("Eliminar", L("del_recipe")):
            api.delete_water_recipe(recipe_id)
            self._load_saved()

    def _save_recipe(self):
        if not self._result:
            messagebox.showinfo("Calcula primero", "Presiona 'Calcular' primero.\nCalculate first.")
            return
        SaveWaterRecipeDialog(self, self._result, self._gh_var.get(),
                              self._kh_var.get(), int(self._tds_var.get()),
                              on_save=self._load_saved)


class SaveWaterRecipeDialog(ctk.CTkToplevel):
    def __init__(self, parent, result, gh, kh, tds, on_save):
        super().__init__(parent)
        self.result  = result
        self.gh      = gh
        self.kh      = kh
        self.tds     = tds
        self.on_save = on_save
        self.title("Guardar Receta de Agua")
        self.geometry("380x200")
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()

        ctk.CTkLabel(self, text=L("recipe_name"),
                     font=FONTS["label"], text_color=COLORS["text_muted"]).pack(padx=20, pady=(20, 4), anchor="w")
        self._name_entry = ctk.CTkEntry(self, fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"], width=340)
        self._name_entry.pack(padx=20)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=16)
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
        recipe_data = {
            "name": name,
            "target_gh_ppm": self.gh,
            "target_kh_ppm": self.kh,
            "target_tds_ppm": self.tds,
            "mg_sulfate_g_per_l": self.result['mg_sulfate_g_per_l'],
            "sodium_bicarb_g_per_l": self.result['sodium_bicarb_g_per_l'],
            "calcium_chloride_g_per_l": self.result['calcium_chloride_g_per_l'],
        }
        api.create_water_recipe(recipe_data)
        if self.on_save:
            self.on_save()
        self.destroy()
