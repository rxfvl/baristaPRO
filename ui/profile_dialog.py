import customtkinter as ctk
from tkinter import messagebox, filedialog
from logic.api_client import api
from utils.theme import COLORS, FONTS, CORNER_RADIUS, get_label

class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Mi Perfil")
        self.geometry("450x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save
        self.app = parent.winfo_toplevel()
        
        self.configure(fg_color=COLORS["bg_primary"])
        self.me = None
        
        self._build()
        self._load_data()

    def _build(self):
        # Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- Avatar Section ---
        self.avatar_lbl = ctk.CTkLabel(self.container, text="👤", font=("Segoe UI Emoji", 48), width=100, height=100, fg_color=COLORS["bg_input"], corner_radius=50)
        self.avatar_lbl.pack(pady=(0, 10))
        
        ctk.CTkButton(
            self.container, text="Cambiar foto", font=FONTS["body"], 
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"], hover_color=COLORS["bg_input"],
            command=self._on_change_avatar
        ).pack(pady=(0, 20))

        # --- Nickname ---
        ctk.CTkLabel(self.container, text="Apodo", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self.nickname_entry = ctk.CTkEntry(self.container, font=FONTS["body"], fg_color=COLORS["bg_input"], border_width=0, corner_radius=CORNER_RADIUS["input"])
        self.nickname_entry.pack(fill="x", pady=(0, 10))
        
        # Email (Readonly)
        ctk.CTkLabel(self.container, text="Email", font=FONTS["label"], text_color=COLORS["text_muted"]).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(self.container, font=FONTS["body"], fg_color=COLORS["bg_card"], border_width=0, corner_radius=CORNER_RADIUS["input"], text_color=COLORS["text_muted"])
        self.email_entry.pack(fill="x", pady=(0, 20))
        self.email_entry.configure(state="disabled")

        # Save profile button
        ctk.CTkButton(
            self.container, text="Guardar Perfil", font=FONTS["button"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._on_save_profile
        ).pack(fill="x", pady=(0, 30))

        # --- Security Section ---
        ctk.CTkLabel(self.container, text="Seguridad", font=FONTS["subhead"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))
        
        self.old_pass_entry = ctk.CTkEntry(self.container, placeholder_text="Contraseña actual", show="*", font=FONTS["body"], fg_color=COLORS["bg_input"], border_width=0)
        self.old_pass_entry.pack(fill="x", pady=(0, 10))
        
        self.new_pass_entry = ctk.CTkEntry(self.container, placeholder_text="Nueva contraseña", show="*", font=FONTS["body"], fg_color=COLORS["bg_input"], border_width=0)
        self.new_pass_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            self.container, text="Actualizar Contraseña", font=FONTS["button"],
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"], hover_color=COLORS["bg_input"],
            command=self._on_update_password
        ).pack(fill="x", pady=(0, 30))

        # --- Logout Section ---
        ctk.CTkButton(
            self.container, text="Cerrar Sesión", font=FONTS["button"],
            fg_color="#D32F2F", hover_color="#B71C1C", text_color="white",
            command=self._on_logout
        ).pack(fill="x", pady=(10, 0))

    def _load_data(self):
        try:
            self.me = api.get_me()
            if self.me:
                if getattr(self.me, 'nickname', None):
                    self.nickname_entry.insert(0, self.me.nickname)
                self.email_entry.configure(state="normal")
                self.email_entry.insert(0, self.me.email)
                self.email_entry.configure(state="disabled")
                
                # Load avatar
                avatar_url = getattr(self.me, 'profile_picture_url', None)
                if avatar_url:
                    from logic.api_client import BASE_URL
                    import requests
                    from PIL import Image
                    from io import BytesIO
                    
                    try:
                        url = BASE_URL.replace("/api", "") + avatar_url
                        resp = requests.get(url, timeout=3)
                        if resp.status_code == 200:
                            img = Image.open(BytesIO(resp.content))
                            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                            self.avatar_lbl.configure(image=ctk_img, text="")
                    except Exception as e:
                        print("Failed to load avatar:", e)
                        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el perfil: {e}")

    def _on_change_avatar(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto de perfil",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            try:
                updated_user = api.upload_avatar(file_path)
                if updated_user:
                    self.me = updated_user
                    # Refresh visual
                    self._load_data()
                    messagebox.showinfo("Éxito", "Foto de perfil actualizada")
                    if self.on_save:
                        self.on_save()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al subir avatar: {e}")

    def _on_save_profile(self):
        nickname = self.nickname_entry.get().strip()
        try:
            res = api.update_profile(nickname)
            if res:
                messagebox.showinfo("Éxito", "Perfil actualizado")
                if self.on_save:
                    self.on_save()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def _on_update_password(self):
        old_p = self.old_pass_entry.get()
        new_p = self.new_pass_entry.get()
        if not old_p or not new_p:
            messagebox.showwarning("Atención", "Rellena ambos campos de contraseña.")
            return
            
        try:
            success, msg = api.update_password(old_p, new_p)
            if success:
                messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
                self.old_pass_entry.delete(0, 'end')
                self.new_pass_entry.delete(0, 'end')
            else:
                messagebox.showerror("Error", f"No se pudo cambiar: {msg}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar: {e}")

    def _on_logout(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que quieres cerrar sesión?"):
            api.logout()
            self.destroy()
            
            # Restart app
            import subprocess
            import sys
            self.app.destroy()
            subprocess.Popen([sys.executable, "main.py"])
