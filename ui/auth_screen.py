import customtkinter as ctk
from logic.api_client import api
from utils.theme import COLORS, FONTS

class AuthScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BaristaPRO — Login")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Center the window
        self.eval('tk::PlaceWindow . center')
        
        self.configure(fg_color=COLORS["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Logo / Title
        ctk.CTkLabel(
            self, text="☕", font=("Segoe UI Emoji", 48), text_color=COLORS["accent"]
        ).grid(row=0, column=0, pady=(40, 10))
        
        ctk.CTkLabel(
            self, text="Welcome to BaristaPRO", font=FONTS["h2"], text_color=COLORS["text_primary"]
        ).grid(row=1, column=0, pady=(0, 20))
        
        # Frame
        frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=12)
        frame.grid(row=2, column=0, padx=40, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        self.email_entry = ctk.CTkEntry(
            frame, placeholder_text="Email", font=FONTS["body"], height=40
        )
        self.email_entry.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.password_entry = ctk.CTkEntry(
            frame, placeholder_text="Password", show="*", font=FONTS["body"], height=40
        )
        self.password_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.error_label = ctk.CTkLabel(
            frame, text="", text_color=COLORS["danger"], font=FONTS["caption"]
        )
        self.error_label.grid(row=2, column=0, padx=20, pady=(0, 10))
        
        self.login_btn = ctk.CTkButton(
            frame, text="Log In", font=FONTS["button"], height=40,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            command=self.handle_login
        )
        self.login_btn.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.register_btn = ctk.CTkButton(
            frame, text="Create Account", font=FONTS["button"], height=40,
            fg_color="transparent", text_color=COLORS["text_secondary"], hover_color=COLORS["surface"],
            command=self.handle_register
        )
        self.register_btn.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def handle_login(self):
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get()
        if not email or not pwd:
            self.error_label.configure(text="Please fill all fields", text_color=COLORS["danger"])
            return
            
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update()
        
        success, msg = api.login(email, pwd)
        if success:
            self.destroy()
        else:
            self.error_label.configure(text=msg, text_color=COLORS["danger"])
            self.login_btn.configure(state="normal", text="Log In")
            
    def handle_register(self):
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get()
        if not email or not pwd:
            self.error_label.configure(text="Please fill all fields", text_color=COLORS["danger"])
            return
            
        self.register_btn.configure(state="disabled", text="Registering...")
        self.update()
        
        success, msg = api.register(email, pwd)
        if success:
            self.error_label.configure(text=msg, text_color=COLORS["success"])
        else:
            self.error_label.configure(text=msg, text_color=COLORS["danger"])
        self.register_btn.configure(state="normal", text="Create Account")
        
    def on_closing(self):
        self.destroy()
