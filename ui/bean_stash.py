# ui/bean_stash.py — Bean Inventory Module

import customtkinter as ctk
from datetime import date, datetime
from tkinter import messagebox
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label
from logic.api_client import api
from logic.degassing import (
    get_rest_window, degassing_info,
    STATUS_COLORS, STATUS_LABELS
)

PROCESSES = [
    L("proc_washed"), L("proc_natural"), L("proc_honey"), L("proc_anaerobic"),
    L("proc_carbonic"), L("proc_experimental"), L("proc_other")
]

VARIETIES = [
    "Bourbon", "Caturra", "Catuai", L("var_gesha"), "Typica",
    "Pacamara", "Heirloom", "SL28", "SL34",
    "Yellow Catuai", "Yellow Caturra", "Red Bourbon", "Mundo Novo",
    "Caturra y Catuai", "Bourbon y Caturra", "Typica y Bourbon",
    L("proc_other")
]


class BeanStashView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        self._build_header()
        self._build_list()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        header.columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text=L("nav_beans"),
                     font=FONTS["display"], text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(left, text=L("cat_coffee"),
                     font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(
            right, text=f"+ {get_label('add_new')}",
            font=FONTS["body"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            command=self._open_add_dialog,
        ).pack(side="right")

    def _build_list(self):
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.list_frame.columnconfigure(0, weight=1)
        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        try:
            beans = api.get_beans()
        except Exception as e:
            beans = []
            print(f"Error loading beans: {e}")

        if not beans:
            ctk.CTkLabel(
                self.list_frame,
                text=L("no_beans_yet"),
                font=FONTS["body"], text_color=COLORS["text_muted"]
            ).grid(row=0, column=0, pady=40)
            return

        # Column headers
        headers = [L("bean"), L("bean_roaster"), L("bean_country"), L("bean_process"), L("bean_stock"), L("actions")]
        header_row = ctk.CTkFrame(self.list_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        weights = [3, 2, 2, 2, 1, 3]
        for i, (h, w) in enumerate(zip(headers, weights)):
            header_row.columnconfigure(i, weight=w)
            ctk.CTkLabel(header_row, text=h, font=FONTS["label"],
                         text_color=COLORS["text_muted"]).grid(
                row=0, column=i, padx=12, pady=8, sticky="w"
            )

        for idx, bean in enumerate(beans):
            total_stock = sum(getattr(b, 'stock_grams', 0) for b in getattr(bean, 'batches', []) if not getattr(b, 'is_archived', False))
            self._bean_row(idx + 1, bean, total_stock)

    def _bean_row(self, row_idx, bean, total_stock):
        card = ctk.CTkFrame(
            self.list_frame, fg_color=COLORS["bg_card"],
            corner_radius=8
        )
        card.grid(row=row_idx, column=0, sticky="ew", pady=(0, 4))
        weights = [3, 2, 2, 2, 1, 3]
        for i, w in enumerate(weights):
            card.columnconfigure(i, weight=w)

        # Data cells
        ctk.CTkLabel(card, text=bean.name, font=FONTS["body"],
                     text_color=COLORS["text_primary"], anchor="w").grid(
            row=0, column=0, padx=16, pady=10, sticky="ew"
        )
        ctk.CTkLabel(card, text=bean.roaster or "—", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).grid(row=0, column=1, padx=8, sticky="w")
        ctk.CTkLabel(card, text=bean.origin_country or "—", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).grid(row=0, column=2, padx=8, sticky="w")
        ctk.CTkLabel(card, text=bean.process or "—", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).grid(row=0, column=3, padx=8, sticky="w")

        ctk.CTkLabel(card, text=f"{total_stock:.0f}g",
                     font=FONTS["body"], text_color=COLORS["text_primary"]).grid(
            row=0, column=4, padx=8, sticky="w"
        )

        # Action buttons
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=5, padx=8, pady=6, sticky="e")
        ctk.CTkButton(
            actions, text="Lotes", width=56, height=28, font=FONTS["small"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=6,
            command=lambda b=bean.id: self._open_batches_dialog(b)
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            actions, text=L("edit"), width=56, height=28, font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, command=lambda b=bean.id: self._open_edit_dialog(b)
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            actions, text="✨ IA", width=44, height=28, font=FONTS["small"],
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
            text_color=COLORS["accent"], corner_radius=6,
            command=lambda b=bean.id: self._open_flavor_prediction(b)
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            actions, text="✕", width=28, height=28, font=FONTS["small"],
            fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"],
            text_color=COLORS["danger"], corner_radius=6,
            command=lambda b=bean.id: self._delete_bean(b)
        ).pack(side="left")

        # Display AI predicted profile if it exists
        if bean.expected_acidity is not None:
            ai_text = f"✨ {L('dash_clusters').split()[0]} {L('profile')}: {L('ext_acidity')} {bean.expected_acidity:.1f} | {L('ext_sweetness')} {bean.expected_sweetness:.1f} | {L('ext_body')} {bean.expected_body:.1f} | {L('ext_bitterness')} {bean.expected_bitterness:.1f}"
            ctk.CTkLabel(card, text=ai_text, font=FONTS["caption"], text_color=COLORS["accent"]).grid(
                row=1, column=0, columnspan=5, padx=16, pady=(0, 10), sticky="w"
            )

    # ── Dialogs ─────────────────────────────────────────────────────────────────
    def _on_data_changed(self):
        """Refreshes current view and clears cache for other tabs so they update."""
        self._refresh_list()
        self.app.refresh_view("dashboard")
        self.app.refresh_view("journal")

    def _open_add_dialog(self):
        BeanDialog(self, mode="add", on_save=self._on_data_changed)

    def _open_edit_dialog(self, bean_id: int):
        try:
            # For simplicity, we just fetch all and filter since we don't have get_bean(id) yet
            beans = api.get_beans()
            bean = next((b for b in beans if getattr(b, 'id', None) == bean_id), None)
            if bean:
                BeanDialog(self, mode="edit", bean=bean, on_save=self._on_data_changed)
        except Exception as e:
            print(f"Error fetching bean: {e}")

    def _open_batches_dialog(self, bean_id: int):
        BatchesDialog(self, bean_id, on_save=self._on_data_changed)

    def _delete_bean(self, bean_id: int):
        from logic.api_client import api
        if messagebox.askyesno("Eliminar", L("del_bean")):
            if api.delete_bean(bean_id):
                self._refresh_list()
                self.app.refresh_view("dashboard")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el grano")

    def _open_flavor_prediction(self, bean_id: int):
        import customtkinter as ctk
        from ui.ai_widgets import FlavorPredictionCard

        try:
            beans = api.get_beans()
            bean = next((b for b in beans if getattr(b, 'id', None) == bean_id), None)
            if not bean:
                return
            bean_data = {
                "id": bean.id,
                "name": bean.name,
                "variety": getattr(bean, 'variety', None),
                "process": getattr(bean, 'process', None),
                "origin_country": getattr(bean, 'origin_country', None),
                "altitude_masl": getattr(bean, 'altitude_masl', None),
                "notes": getattr(bean, 'notes', None)
            }
        except Exception:
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"✨ IA: {bean_data['name']}")
        popup.geometry("400x320")
        popup.resizable(False, False)
        popup.configure(fg_color=COLORS["bg_secondary"])
        popup.grab_set()

        card = FlavorPredictionCard(popup, bean_data, on_save=self._on_data_changed)
        card.pack(fill="both", expand=True, padx=16, pady=16)


class BatchesDialog(ctk.CTkToplevel):
    """Dialog to list and add batches for a specific bean."""
    def __init__(self, parent, bean_id: int, on_save=None):
        super().__init__(parent)
        self.bean_id = bean_id
        self.on_save = on_save
        
        try:
            beans = api.get_beans()
            bean = next((b for b in beans if getattr(b, 'id', None) == bean_id), None)
            self.bean_name = bean.name if bean else "Unknown"
            self.process = bean.process if bean else None
        except Exception:
            self.bean_name = "Unknown"
            self.process = None

        self.title(f"{L('batches')} - {self.bean_name}")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Add batch form
        self.form_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        self.form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self._build_form()
        
        # List of batches
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.list_frame.columnconfigure(0, weight=1)
        self._refresh_list()

    def _build_form(self):
        from logic.degassing import PREP_METHOD_REST_DEFAULTS
        
        ctk.CTkLabel(self.form_frame, text=L("add_batch"), font=FONTS["heading"], text_color=COLORS["text_primary"]).grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 4))
        
        # Labels for fields
        ctk.CTkLabel(self.form_frame, text="Fecha Tueste", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", padx=(16, 8))
        ctk.CTkLabel(self.form_frame, text="Stock (g)", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=1, column=1, sticky="w", padx=8)
        ctk.CTkLabel(self.form_frame, text="Método Principal", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=1, column=2, sticky="w", padx=8)
        
        self.e_date = ctk.CTkEntry(self.form_frame, placeholder_text="YYYY-MM-DD", width=140, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.e_date.grid(row=2, column=0, padx=(16, 8), pady=(0, 16), sticky="w")
        
        self.e_stock = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. 250", width=80, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.e_stock.grid(row=2, column=1, padx=8, pady=(0, 16), sticky="w")
        
        methods = list(PREP_METHOD_REST_DEFAULTS.keys())
        self.c_prep = ctk.CTkComboBox(self.form_frame, values=methods, width=160, fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.c_prep.grid(row=2, column=2, padx=8, pady=(0, 16), sticky="w")
        
        ctk.CTkButton(self.form_frame, text="+ Añadir", width=80, font=FONTS["body"], fg_color=COLORS["accent"], text_color="#000", hover_color=COLORS["accent_hover"], command=self._add_batch).grid(row=2, column=3, padx=(8, 16), pady=(0, 16), sticky="e")

        # Auto-fill defaults
        self.e_date.insert(0, date.today().isoformat())
        self.c_prep.set("Espresso")

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
            
        try:
            batches = api.get_bean_batches(self.bean_id)
            # Filter unarchived and sort desc
            batches = sorted([b for b in batches if not getattr(b, 'is_archived', False)], key=lambda x: getattr(x, 'roast_date', ''), reverse=True)
        except Exception as e:
            batches = []
            print(f"Error fetching batches: {e}")
            
            if not batches:
                ctk.CTkLabel(self.list_frame, text="No hay lotes activos.", font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=20)
                return
                
            for b in batches:
                card = ctk.CTkFrame(self.list_frame, fg_color=COLORS["bg_card"], corner_radius=8)
                card.pack(fill="x", pady=6, padx=4)
                
                status = b.degassing_status
                s_color = STATUS_COLORS.get(status, COLORS["text_muted"])
                
                # Header row
                header = ctk.CTkFrame(card, fg_color="transparent")
                header.pack(fill="x", padx=12, pady=(10, 4))
                
                badge = ctk.CTkLabel(header, text=f" {STATUS_LABELS.get(status, status)} ", font=FONTS["caption"], text_color=s_color, fg_color=COLORS["bg_primary"], corner_radius=10)
                badge.pack(side="left")
                
                # Identify if prep method is known
                from logic.degassing import PREP_METHOD_REST_DEFAULTS
                prep_name = "Personalizado"
                for name, (vmin, vmax) in PREP_METHOD_REST_DEFAULTS.items():
                    if b.rest_days_min == vmin and b.rest_days_max == vmax:
                        prep_name = name
                        break
                        
                ctk.CTkLabel(header, text=f" • {prep_name} • ", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(side="left", padx=8)
                
                ctk.CTkButton(header, text="✕", width=28, height=28, font=FONTS["small"], fg_color=COLORS["danger_dim"], hover_color=COLORS["danger"], text_color=COLORS["danger"], corner_radius=6, command=lambda bid=b.id: self._archive_batch(bid)).pack(side="right")
                
                # Details row
                details = ctk.CTkFrame(card, fg_color="transparent")
                details.pack(fill="x", padx=12, pady=(0, 8))
                
                ctk.CTkLabel(details, text=f"🗓 Tueste: {b.roast_date}  |  📦 Stock: {b.stock_grams:.0f}g", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(side="left")
                
                from datetime import timedelta
                if b.roast_date:
                    p_start = b.roast_date + timedelta(days=b.rest_days_min)
                    p_end = b.roast_date + timedelta(days=b.rest_days_max)
                    ctk.CTkLabel(details, text=f"Óptimo: {p_start.strftime('%d/%m')} - {p_end.strftime('%d/%m')}", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(side="right")
                
                # Progress bar
                progress_bar = ctk.CTkProgressBar(card, height=4, progress_color=s_color, fg_color=COLORS["bg_input"], corner_radius=2)
                progress_bar.pack(fill="x", padx=12, pady=(0, 12))
                progress_bar.set(b.degassing_progress)

    def _add_batch(self):
        from logic.degassing import PREP_METHOD_REST_DEFAULTS
        date_str = self.e_date.get()
        try:
            r_date = date.fromisoformat(date_str)
        except ValueError:
            messagebox.showerror("Error", L("err_date"))
            return
            
        try:
            stock = float(self.e_stock.get() or 0)
        except ValueError:
            messagebox.showerror("Error", L("err_num_batch"))
            return
            
        prep = self.c_prep.get()
        r_min, r_max = PREP_METHOD_REST_DEFAULTS.get(prep, (7, 14))
            
        batch_data = {
            "bean_id": self.bean_id,
            "roast_date": r_date.isoformat(),
            "stock_grams": stock,
            "rest_days_min": r_min,
            "rest_days_max": r_max,
            "is_archived": False
        }
        api.create_bean_batch(self.bean_id, batch_data)
            
        self.e_stock.delete(0, 'end')
        self._refresh_list()
        if self.on_save:
            self.on_save()
            
    def _archive_batch(self, batch_id):
        if messagebox.askyesno("Archivar", L("archive_batch")):
            # TODO: add archive_bean_batch endpoint
            api.archive_bean_batch(self.bean_id, batch_id)
            self._refresh_list()
            if self.on_save:
                self.on_save()


class BeanDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing a Bean Catalog item."""

    def __init__(self, parent, mode="add", bean=None, on_save=None):
        super().__init__(parent)
        self.mode    = mode
        self.bean    = bean
        self.on_save = on_save

        title = L("add_new") if mode == "add" else L("edit")
        self.title(title)
        self.geometry("600x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_secondary"])
        self.grab_set()

        self._entries = {}
        self._build()
        if bean:
            self._populate(bean)

    def _build(self):
        try:
            # We would need catalog options from api, but for now we'll just extract from existing beans
            beans = api.get_beans()
            roasters = list(set([b.roaster for b in beans if getattr(b, 'roaster', None)]))
            countries = list(set([b.origin_country for b in beans if getattr(b, 'origin_country', None)]))
            regions = list(set([b.origin_region for b in beans if getattr(b, 'origin_region', None)]))
            farms = list(set([b.origin_farm for b in beans if getattr(b, 'origin_farm', None)]))
            db_varieties = list(set([b.variety for b in beans if getattr(b, 'variety', None)]))
            db_processes = list(set([b.process for b in beans if getattr(b, 'process', None)]))
        except Exception:
            roasters, countries, regions, farms, db_varieties, db_processes = [], [], [], [], [], []

        all_roasters = sorted(list(set(roasters)))
        all_countries = sorted(list(set(countries)))
        all_regions = sorted(list(set(regions)))
        all_farms = sorted(list(set(farms)))
        all_varieties = sorted(list(set(VARIETIES + db_varieties)))
        all_processes = sorted(list(set(PROCESSES + db_processes)))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            scroll,
            text=L("cat_coffee") if self.mode == "add" else L("edit"),
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        fields_left = [
            ("roaster",        L("bean_roaster"),          "combo", all_roasters if all_roasters else [""]),
            ("name",           L("bean_name"),             "text"),
            ("origin_country", L("bean_country"),          "combo", all_countries if all_countries else [""]),
            ("origin_region",  L("bean_region"),           "combo", all_regions if all_regions else [""]),
        ]
        fields_right = [
            ("origin_farm",    L("bean_farm"),                  "combo", all_farms if all_farms else [""]),
            ("variety",        L("bean_variety"),               "combo", all_varieties),
            ("process",        L("bean_process"),               "combo", all_processes),
            ("altitude_masl",  L("bean_altitude"),              "text"),
        ]

        for row_i, (key, label, ftype, *opts) in enumerate(fields_left):
            self._field(scroll, row_i + 1, 0, key, label, ftype, opts)
        for row_i, (key, label, ftype, *opts) in enumerate(fields_right):
            self._field(scroll, row_i + 1, 1, key, label, ftype, opts)

        # Notes
        ctk.CTkLabel(scroll, text=L("ext_notes"), font=FONTS["label"],
                     text_color=COLORS["text_muted"]).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(12, 2)
        )
        self._entries["notes"] = ctk.CTkTextbox(
            scroll, height=80, fg_color=COLORS["bg_input"], border_color=COLORS["border"]
        )
        self._entries["notes"].grid(row=10, column=0, columnspan=2, sticky="ew")

        # Buttons
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ctk.CTkButton(
            btn_row, text=L("save"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=CORNER_RADIUS["button"],
            command=self._save
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btn_row, text=L("cancel"),
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=CORNER_RADIUS["button"],
            command=self.destroy
        ).pack(side="right")

    def _field(self, parent, row, col, key, label, ftype, opts=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=(0, 8) if col == 0 else (8, 0), pady=4)
        frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        if ftype == "combo" and opts:
            widget = ctk.CTkComboBox(
                frame, values=opts[0] if opts else [],
                fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                dropdown_fg_color=COLORS["bg_card"],
            )
        else:
            widget = ctk.CTkEntry(
                frame, fg_color=COLORS["bg_input"], border_color=COLORS["border"]
            )
        widget.pack(fill="x")
        self._entries[key] = widget

    def _populate(self, bean):
        def set_val(key, val):
            widget = self._entries.get(key)
            if widget is None or val is None:
                return
            if isinstance(widget, ctk.CTkEntry):
                widget.insert(0, str(val))
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(str(val))
            elif isinstance(widget, ctk.CTkTextbox):
                widget.insert("1.0", str(val))

        set_val("roaster", bean.roaster)
        set_val("name", bean.name)
        set_val("origin_country", bean.origin_country)
        set_val("origin_region", bean.origin_region)
        set_val("origin_farm", bean.origin_farm)
        set_val("variety", bean.variety)
        set_val("process", bean.process)
        set_val("altitude_masl", bean.altitude_masl)
        set_val("notes", bean.notes)

    def _get(self, key, default=""):
        widget = self._entries.get(key)
        if widget is None:
            return default
        if isinstance(widget, ctk.CTkEntry):
            return widget.get().strip()
        if isinstance(widget, ctk.CTkComboBox):
            return widget.get().strip()
        if isinstance(widget, ctk.CTkTextbox):
            return widget.get("1.0", "end").strip()
        return default

    def _save(self):
        roaster = self._get("roaster")
        name    = self._get("name")
        if not roaster or not name:
            messagebox.showerror("Error", L("err_roaster_name"))
            return

        process = self._get("process")
        country = self._get("origin_country") or None
        region  = self._get("origin_region") or None
        farm    = self._get("origin_farm") or None
        variety = self._get("variety") or None

        alt_val = self._get("altitude_masl")
        
        bean_data = {
            "roaster": roaster,
            "name": name,
            "origin_country": country,
            "origin_region": region,
            "origin_farm": farm,
            "variety": variety,
            "process": process,
            "altitude_masl": int(alt_val) if alt_val.isdigit() else None,
            "notes": self._get("notes") or None
        }

        if self.mode == "add":
            api.create_bean(bean_data)
        else:
            # TODO: Add update_bean to api_client
            pass
            # api.update_bean(self.bean.id, bean_data)

        if self.on_save:
            self.on_save()
        self.destroy()
