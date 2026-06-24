import re

file_path = r"c:\Users\minec\Desktop\baristaPRO\ui\dial_in_journal.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add progress bar to _build
build_pattern = r"""        self._history_hint_label\.pack\(anchor="w"\)"""
build_replacement = """        self._history_hint_label.pack(anchor="w")

        # STOCK INDICATOR
        stock_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(4, 0))
        self._stock_bar = ctk.CTkProgressBar(stock_frame, progress_color=COLORS["accent"], height=8)
        self._stock_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._stock_bar.set(0)
        self._stock_label = ctk.CTkLabel(stock_frame, text="", font=FONTS["small"], text_color=COLORS["text_muted"])
        self._stock_label.pack(side="right")"""
content = content.replace(build_pattern, build_replacement)


# 2. Update _on_bean_select
bean_select_pattern = r"""    def _on_bean_select\(self, choice: str\):
        if not choice or ":" not in choice:
            self._history_hint_label.configure\(text="Sin historial disponible / No history available"\)
            return
            
        try:
            bean_id = int\(choice\.split\(":"\)\[0\]\)
        except ValueError:
            return
            
        from db\.database import get_session
        from db\.models import ExtractionLog
        with get_session\(\) as db:
            last_ext = \(
                db\.query\(ExtractionLog\)
                \.filter\(ExtractionLog\.bean_batch_id == bean_id\)
                \.order_by\(ExtractionLog\.timestamp\.desc\(\)\)
                \.first\(\)
            \)"""

bean_select_replacement = """    def _on_bean_select(self, choice: str):
        if not choice or ":" not in choice:
            self._history_hint_label.configure(text="Sin historial disponible / No history available")
            if hasattr(self, '_stock_bar'):
                self._stock_bar.set(0)
                self._stock_label.configure(text="")
            return
            
        try:
            bean_id = int(choice.split(":")[0])
        except ValueError:
            return
            
        from db.database import get_session
        from db.models import ExtractionLog, BeanBatch
        with get_session() as db:
            batch = db.get(BeanBatch, bean_id)
            if batch:
                extractions = db.query(ExtractionLog).filter(ExtractionLog.bean_batch_id == bean_id).all()
                consumed = sum(e.dose_in or 0 for e in extractions)
                stock = batch.stock_grams
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
            
            last_ext = (
                db.query(ExtractionLog)
                .filter(ExtractionLog.bean_batch_id == bean_id)
                .order_by(ExtractionLog.timestamp.desc())
                .first()
            )"""
content = re.sub(bean_select_pattern, bean_select_replacement, content, flags=re.MULTILINE)

# 3. Update _save
save_pattern = r"""            # Adjust batch stock
            if bean_id:
                batch = db\.get\(BeanBatch, bean_id\)
                if batch and dose > 0:
                    dose_diff = dose - old_dose
                    batch\.stock_grams = max\(batch\.stock_grams - dose_diff, 0\)

            db\.commit\(\)"""

save_replacement = """            # Adjust batch stock
            if bean_id:
                batch = db.get(BeanBatch, bean_id)
                if batch and dose > 0:
                    dose_diff = dose - old_dose
                    if dose_diff > batch.stock_grams:
                        db.rollback()
                        messagebox.showerror("Sin stock", f"No tienes suficiente café.\\nTe quedan {batch.stock_grams:.1f}g pero necesitas {dose_diff:.1f}g más para esta dosis.")
                        return
                    batch.stock_grams = max(batch.stock_grams - dose_diff, 0)

            db.commit()
            
            # Update progress bar UI
            self._on_bean_select(self._bean_combo.get())"""
content = re.sub(save_pattern, save_replacement, content, flags=re.MULTILINE)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patch 3 applied successfully")
