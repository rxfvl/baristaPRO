import customtkinter as ctk
from tkinter import messagebox
from utils.theme import COLORS, FONTS, CORNER_RADIUS, save_lang, ACTIVE_LANG

class SettingsView(ctk.CTkFrame):
    """View to manage application settings like Language."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        title = "Configuración" if ACTIVE_LANG == "es" else "Settings"
        ctk.CTkLabel(
            self, text=title,
            font=FONTS["display"], text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 20), padx=16)

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=CORNER_RADIUS["card"])
        card.grid(row=1, column=0, sticky="ew", padx=16)
        card.columnconfigure(1, weight=1)

        lbl = "Idioma (Reinicia para aplicar)" if ACTIVE_LANG == "es" else "Language (Restart to apply)"
        ctk.CTkLabel(
            card, text=lbl, font=FONTS["subhead"], text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", padx=16, pady=16)

        self._lang_var = ctk.StringVar(value=ACTIVE_LANG)
        lang_seg = ctk.CTkSegmentedButton(
            card, values=["es", "en"], variable=self._lang_var, command=self._on_lang_change,
            selected_color=COLORS["accent"], selected_hover_color=COLORS["accent_hover"],
            font=FONTS["body"]
        )
        lang_seg.grid(row=0, column=1, sticky="e", padx=16, pady=16)

    def _on_lang_change(self, choice):
        if choice != ACTIVE_LANG:
            save_lang(choice)
            msg = "Idioma cambiado a Español. Reinicia la aplicación para aplicar todos los cambios." if choice == "es" else "Language changed to English. Please restart the application to apply all changes."
            title = "Reinicio requerido" if choice == "es" else "Restart required"
            messagebox.showinfo(title, msg)
