# ui/app.py — Main application window with sidebar navigation

import threading
import customtkinter as ctk
from utils.theme import COLORS, FONTS, SIDEBAR_WIDTH, L, get_label


class EspressoLabApp(ctk.CTk):
    """Root window — sidebar nav + content frame switcher."""

    def __init__(self):
        super().__init__()

        # --- Window config ---
        self.title("BaristaPRO — Professional Coffee Tracking")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.after(100, lambda: self.state('zoomed'))
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color=COLORS["bg_primary"])

        self._current_view = None
        self._nav_buttons  = {}

        self._build_layout()
        self._build_sidebar()
        self._build_content_area()

        # Navigate to dashboard by default
        self.show_view("dashboard")

        # Initialise AI models in background (non-blocking)
        threading.Thread(target=self._init_ai_models, daemon=True).start()

    # ── Layout ─────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=COLORS["sidebar_bg"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo / brand
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 8))
        logo_frame.grid_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="☕",
            font=("Segoe UI Emoji", 28),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=(0, 8))

        name_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        name_frame.pack(side="left")
        ctk.CTkLabel(
            name_frame, text="EspressoLab",
            font=FONTS["subhead"], text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            name_frame, text="Coffee Tracker",
            font=FONTS["caption"], text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).grid(
            row=1, column=0, sticky="ew", padx=12, pady=4
        )

        # Nav items: (view_key, icon, label_key)
        nav_items = [
            ("dashboard", "⬛", "nav_dashboard"),
            ("beans",     "🌱", "nav_beans"),
            ("journal",   "📓", "nav_journal"),
            ("water",     "💧", "nav_water"),
            ("equipment", "⚙️",  "nav_equipment"),
            ("settings",  "⚙️",  "Configuración" if get_label("nav_dashboard") == "Dashboard" else "Settings"), # fallback
        ]
        for i, (view_key, icon, lbl_key) in enumerate(nav_items):
            if lbl_key.startswith("nav_"):
                text = f"  {icon}  {get_label(lbl_key)}"
            else:
                text = f"  {icon}  {get_label('settings')}"

            btn = self._make_nav_button(text, view_key)
            btn.grid(row=i + 2, column=0, sticky="ew", padx=8, pady=2)
            self._nav_buttons[view_key] = btn

        # Bottom: User Profile Widget
        self.profile_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["bg_card"], corner_radius=8, cursor="hand2", width=236, height=60)
        self.profile_frame.grid(row=21, column=0, padx=12, pady=12)
        self.profile_frame.grid_propagate(False)
        
        self.profile_frame.columnconfigure(1, weight=1)
        self.profile_frame.rowconfigure(0, weight=1)
        
        def _on_enter(e):
            self.profile_frame.configure(fg_color=COLORS["bg_input"])
        def _on_leave(e):
            self.profile_frame.configure(fg_color=COLORS["bg_card"])
            
        self.profile_frame.bind("<Enter>", _on_enter)
        self.profile_frame.bind("<Leave>", _on_leave)
        self.profile_frame.bind("<Button-1>", lambda e: self._open_profile())
        
        # Profile Picture
        self.profile_avatar = ctk.CTkLabel(self.profile_frame, text="👤", font=("Segoe UI Emoji", 24), width=40, height=40, fg_color=COLORS["bg_input"], corner_radius=20)
        self.profile_avatar.grid(row=0, column=0, padx=(8, 8), pady=10)
        self.profile_avatar.bind("<Button-1>", lambda e: self._open_profile())
        self.profile_avatar.bind("<Enter>", _on_enter)

        # Profile details
        details = ctk.CTkFrame(self.profile_frame, fg_color="transparent", width=160, height=45)
        details.grid(row=0, column=1, sticky="ew")
        details.grid_propagate(False)
        details.pack_propagate(False)
        details.bind("<Button-1>", lambda e: self._open_profile())
        details.bind("<Enter>", _on_enter)

        self.profile_name_lbl = ctk.CTkLabel(details, text="Cargando...", font=FONTS["body"], text_color=COLORS["text_primary"], anchor="w")
        self.profile_name_lbl.pack(fill="x", anchor="w")
        self.profile_name_lbl.bind("<Button-1>", lambda e: self._open_profile())
        self.profile_name_lbl.bind("<Enter>", _on_enter)

        self.profile_email_lbl = ctk.CTkLabel(details, text="...", font=FONTS["caption"], text_color=COLORS["text_muted"], anchor="w")
        self.profile_email_lbl.pack(fill="x", anchor="w")
        self.profile_email_lbl.bind("<Button-1>", lambda e: self._open_profile())
        self.profile_email_lbl.bind("<Enter>", _on_enter)

        # Fetch profile
        self.after(500, self.refresh_profile_widget)

    def refresh_profile_widget(self):
        from logic.api_client import api
        try:
            me = api.get_me()
            if me:
                name = getattr(me, 'nickname', None) or "Barista"
                email = getattr(me, 'email', "")
                
                # Truncate to prevent overflowing the card
                if len(name) > 16:
                    name = name[:14] + "..."
                if len(email) > 23:
                    email = email[:21] + "..."
                    
                self.profile_name_lbl.configure(text=name)
                self.profile_email_lbl.configure(text=email)
                
                # If we have an avatar, load it
                avatar_url = getattr(me, 'profile_picture_url', None)
                if avatar_url:
                    from logic.api_client import BASE_URL
                    import requests
                    from PIL import Image
                    from io import BytesIO
                    import customtkinter as ctk
                    
                    try:
                        url = BASE_URL.replace("/api", "") + avatar_url
                        resp = requests.get(url, timeout=3)
                        if resp.status_code == 200:
                            img = Image.open(BytesIO(resp.content))
                            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
                            self.profile_avatar.configure(image=ctk_img, text="")
                    except Exception as e:
                        print("Failed to load avatar:", e)
        except Exception as e:
            print("Failed to fetch user:", e)

    def _open_profile(self):
        from ui.profile_dialog import ProfileDialog
        ProfileDialog(self, on_save=self.refresh_profile_widget)

    def _make_nav_button(self, text, view_key):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            height=42,
            corner_radius=8,
            font=FONTS["body"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["sidebar_hover"],
            command=lambda k=view_key: self.show_view(k),
        )
        return btn

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_primary"],
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    # ── Navigation ─────────────────────────────────────────────────────────────
    def show_view(self, view_key: str):
        if self._current_view:
            self._current_view.grid_forget()

        # Update nav button highlights
        for key, btn in self._nav_buttons.items():
            if key == view_key:
                btn.configure(
                    fg_color=COLORS["accent_dark"],
                    text_color=COLORS["accent"],
                    font=FONTS["subhead"] if "bold" not in str(FONTS["subhead"]) else FONTS["subhead"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    font=FONTS["body"],
                )

        # Lazy-import and instantiate views
        view = self._get_view(view_key)
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

    def _get_view(self, view_key: str):
        """Lazy-load view frames (create once, cache after)."""
        cache_attr = f"_view_{view_key}"
        if not hasattr(self, cache_attr):
            if view_key == "dashboard":
                from ui.dashboard import DashboardView
                view = DashboardView(self.content_frame, self)
            elif view_key == "beans":
                from ui.bean_stash import BeanStashView
                view = BeanStashView(self.content_frame, self)
            elif view_key == "journal":
                from ui.dial_in_journal import DialInJournalView
                view = DialInJournalView(self.content_frame, self)
            elif view_key == "water":
                from ui.water_lab import WaterLabView
                view = WaterLabView(self.content_frame, self)
            elif view_key == "equipment":
                from ui.equipment import EquipmentView
                view = EquipmentView(self.content_frame, self)
            elif view_key == "settings":
                from ui.settings import SettingsView
                view = SettingsView(self.content_frame, self)
            else:
                view = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_primary"])
            setattr(self, cache_attr, view)
        return getattr(self, cache_attr)

    def refresh_view(self, view_key: str):
        """Destroy cached view to force re-render on next navigation."""
        cache_attr = f"_view_{view_key}"
        if hasattr(self, cache_attr):
            getattr(self, cache_attr).destroy()
            delattr(self, cache_attr)
        if self._current_view and not self._current_view.winfo_exists():
            self._current_view = None
            self.show_view(view_key)

    # ── AI initialisation ───────────────────────────────────────────────────────
    def _init_ai_models(self):
        """Load persisted models or train from scratch. Runs in a daemon thread."""
        try:
            import pandas as pd
            from db.database import get_session
            from db.models import Bean, ExtractionLog
            from logic.ai.shot_advisor import advisor
            from logic.ai.flavor_predictor import flavor_predictor

            # Build real DataFrames from DB
            with get_session() as db:
                extractions = db.query(ExtractionLog).all()
                beans       = db.query(Bean).all()

            # --- Shot Advisor ---
            if not advisor.load():
                real_ext_df = None
                if extractions:
                    real_ext_df = pd.DataFrame([{
                        "dose_in":           e.dose_in,
                        "yield_out":         e.yield_out,
                        "extraction_time":   e.extraction_time,
                        "water_temp":        e.water_temp,
                        "pressure":          e.pressure,
                        "pre_infusion_time": e.pre_infusion_time,
                        "score":             e.score,
                    } for e in extractions])
                advisor.train(real_ext_df)

            # --- Flavor Predictor ---
            if not flavor_predictor.load():
                real_bean_df = None
                if beans and extractions:
                    # Aggregate sensory averages per bean from extractions
                    bean_sensory = {}
                    for e in extractions:
                        # ExtractionLog links to BeanBatch, not Bean directly
                        bid = e.bean_batch.bean_id if e.bean_batch else None
                        if bid is None:
                            continue
                        if bid not in bean_sensory:
                            bean_sensory[bid] = []
                        bean_sensory[bid].append({
                            "acidity":    e.acidity,
                            "sweetness":  e.sweetness,
                            "body":       e.body,
                            "bitterness": e.bitterness,
                        })
                    rows = []
                    for b in beans:
                        sensory_rows = bean_sensory.get(b.id, [])
                        if not sensory_rows:
                            continue
                        avg = {
                            k: sum(r[k] for r in sensory_rows) / len(sensory_rows)
                            for k in ["acidity", "sweetness", "body", "bitterness"]
                        }
                        rows.append({
                            "variety":         b.variety or "Unknown",
                            "process":         b.process or "Unknown",
                            "origin_country":  b.origin_country or "Unknown",
                            "altitude_masl":   b.altitude_masl or 1200,
                            "days_since_roast":b.days_since_roast or 14,
                            **avg,
                        })
                    if rows:
                        real_bean_df = pd.DataFrame(rows)
                flavor_predictor.train(real_bean_df)
        except Exception as e:
            print(f"[AI init] Error: {e}")
