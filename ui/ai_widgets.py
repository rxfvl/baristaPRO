# ui/ai_widgets.py
# Reusable AI/ML UI widgets for baristaPRO.
#
# Provides:
#   ShotAdvisorCard   — shows shot adjustment suggestions (Feature #1)
#   FlavorPredictionCard — shows predicted sensory profile (Feature #2)
#   ClusterSection    — shows extraction clusters (Bonus K-Means)

import customtkinter as ctk
from utils.theme import COLORS, FONTS, CORNER_RADIUS, L


# ── Helpers ─────────────────────────────────────────────────────────────────────
def _mini_bar(parent, label_es: str, label_en: str, value: float, color: str, row: int):
    """Renders a compact labeled progress bar (1–10 scale)."""
    ctk.CTkLabel(
        parent,
        text=f"{label_es} / {label_en}",
        font=FONTS["caption"],
        text_color=COLORS["text_muted"],
        anchor="w",
    ).grid(row=row * 2, column=0, sticky="w", padx=(0, 8))

    val_label = ctk.CTkLabel(
        parent,
        text=f"{value:.1f}",
        font=FONTS["caption"],
        text_color=color,
        width=28,
        anchor="e",
    )
    val_label.grid(row=row * 2, column=1, sticky="e")

    bar = ctk.CTkProgressBar(
        parent,
        height=5,
        progress_color=color,
        fg_color=COLORS["bg_input"],
        corner_radius=3,
    )
    bar.grid(row=row * 2 + 1, column=0, columnspan=2, sticky="ew", pady=(1, 6))
    bar.set(max(0.0, min(value / 10.0, 1.0)))


# ── Feature #1 — Shot Advisor Card ──────────────────────────────────────────────
class ShotAdvisorCard(ctk.CTkFrame):
    """
    Displays the Shot Advisor suggestion after saving an extraction.
    Shows current predicted score and suggested parameter deltas.
    """

    def __init__(self, parent, extraction_params: dict, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=CORNER_RADIUS["card"],
            **kwargs,
        )
        self._params = extraction_params
        self._build()

    def _build(self):
        from logic.ai.shot_advisor import advisor

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(
            header,
            text=L("ai_analysis"),
            font=FONTS["label"],
            text_color=COLORS["accent"],
        ).pack(side="left")

        if not advisor._trained:
            ctk.CTkLabel(
                self,
                text=L("ai_training"),
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(padx=14, pady=(0, 12))
            return

        result = advisor.suggest(self._params)

        if not result:
            self._no_data_msg()
            return

        base_score = result.get("predicted_score", 0.0)
        sugg_score = result.get("suggested_score", base_score)
        deltas     = result.get("deltas", {})
        message    = result.get("message", "")
        diagnostic = result.get("diagnostic", "")
        suggested_params = result.get("suggested_params", {})

        # Score row
        score_frame = ctk.CTkFrame(self, fg_color="transparent")
        score_frame.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkLabel(
            score_frame,
            text=L("ai_curr_pred"),
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(side="left")
        ctk.CTkLabel(
            score_frame,
            text=f"⭐ {base_score:.1f}",
            font=FONTS["subhead"],
            text_color=COLORS["accent"],
        ).pack(side="left")

        # Diagnostic message based on sensory
        if diagnostic:
            diag_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=8)
            diag_frame.pack(fill="x", padx=14, pady=(4, 8))
            
            # Determine color and icon based on severity
            is_optimal = "Excelente balance" in diagnostic
            diag_color = COLORS["success"] if is_optimal else COLORS["warning"]
            icon = "✅" if is_optimal else "💡"
            
            ctk.CTkLabel(
                diag_frame,
                text=f"{icon} {L('ai_sensory_diag')}",
                font=FONTS["small"], text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(
                diag_frame,
                text=diagnostic,
                font=FONTS["body"], text_color=diag_color,
                wraplength=400, justify="left"
            ).pack(anchor="w", padx=10, pady=(0, 8))

        if message == "already_optimal" or (not deltas and base_score >= 7.0):
            ctk.CTkLabel(
                self,
                text=L("ai_no_adj"),
                font=FONTS["small"],
                text_color=COLORS["success"],
            ).pack(padx=14, pady=(0, 12))
            return
            
        if message == "need_drastic_change" or (not deltas and base_score < 7.0):
            ctk.CTkLabel(
                self,
                text="⚠ Puntaje muy bajo. Intenta un cambio drástico en molienda o ratio.\n/ Score is very low. Try drastic changes to grind or ratio.",
                font=FONTS["small"],
                text_color=COLORS["danger"],
            ).pack(padx=14, pady=(0, 12))
            return

        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=14, pady=4)

        hint = ctk.CTkLabel(
            self,
            text=L("ai_opt_recipe"),
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        hint.pack(anchor="w", padx=14, pady=(2, 4))

        delta_frame = ctk.CTkFrame(self, fg_color="transparent")
        delta_frame.pack(fill="x", padx=14, pady=(0, 8))

        DELTA_LABELS = {
            "dose_in":           ("Dosis",      "Dose",   "g",   "⚖️"),
            "yield_out":         ("Yield",      "Yield",  "g",   "💧"),
            "extraction_time":   ("Tiempo",     "Time",   "s",   "⏱️"),
            "water_temp":        ("Temp",       "Temp",   "°C",  "🌡️"),
            "pressure":          ("Presión",    "Press",  "bar", "⚙️"),
            "pre_infusion_time": ("Pre-inf",    "Pre-inf","s",   "⏳"),
        }

        row_idx = 0
        col_idx = 0
        for key, delta in deltas.items():
            label_es, label_en, unit, icon = DELTA_LABELS.get(key, (key, key, "", ""))
            sign   = "+" if delta > 0 else ""
            color  = COLORS["success"] if delta < 0 else COLORS["warning"]
            suggested_val = suggested_params.get(key, 0)
            
            item_frame = ctk.CTkFrame(delta_frame, fg_color="transparent")
            item_frame.grid(row=row_idx, column=col_idx, sticky="w", padx=(0, 20), pady=4)
            
            ctk.CTkLabel(item_frame, text=f"{icon} {label_es}:", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(side="left")
            ctk.CTkLabel(item_frame, text=f" {suggested_val:.1f}{unit} ", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(side="left")
            ctk.CTkLabel(item_frame, text=f"({sign}{delta}{unit})", font=FONTS["small"], text_color=color).pack(side="left")
            
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        # Predicted improvement
        gain_frame = ctk.CTkFrame(self, fg_color=COLORS["success_dim"], corner_radius=8)
        gain_frame.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(
            gain_frame,
            text=f"{L('ai_est_score')}: ⭐ {sugg_score:.1f} (+{sugg_score - base_score:.1f})",
            font=FONTS["body"],
            text_color=COLORS["success"],
        ).pack(padx=10, pady=6)

    def _no_data_msg(self):
        ctk.CTkLabel(
            self,
            text="Necesitas más datos para sugerencias precisas.\nNeed more data for accurate suggestions.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(padx=14, pady=(0, 12))


# ── Feature #2 — Flavor Prediction Card ─────────────────────────────────────────
class FlavorPredictionCard(ctk.CTkFrame):
    """
    Shows the MLP-predicted sensory profile for a coffee bean.
    Displayed as 4 mini progress bars (acidity, sweetness, body, bitterness).
    """

    SENSORY_CONFIG = [
        ("acidity",    "Acidez",   "Acidity",    "#A8D048"),
        ("sweetness",  "Dulzor",   "Sweetness",  "#E8703A"),
        ("body",       "Cuerpo",   "Body",       "#A0784C"),
        ("bitterness", "Amargor",  "Bitterness", "#688C50"),
    ]

    def __init__(self, parent, bean, on_save=None, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=CORNER_RADIUS["card"],
            **kwargs,
        )
        self._bean = bean
        self._on_save = on_save
        self._prediction = None
        self._build()

    def _build(self):
        from logic.ai.flavor_predictor import flavor_predictor

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            header,
            text=L("ai_flavor_pred"),
            font=FONTS["label"],
            text_color=COLORS["accent"],
        ).pack(side="left")

        if not flavor_predictor._trained:
            ctk.CTkLabel(
                self,
                text=L("ai_training"),
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(padx=14, pady=(0, 10))
            return

        prediction = flavor_predictor.predict(self._bean)
        self._prediction = prediction

        if not prediction:
            ctk.CTkLabel(
                self,
                text=L("ai_no_pred"),
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(padx=14, pady=(0, 10))
            return

        bars_frame = ctk.CTkFrame(self, fg_color="transparent")
        bars_frame.pack(fill="x", padx=14, pady=(0, 6))
        bars_frame.columnconfigure((0, 1), weight=1)

        for i, (key, es, en, color) in enumerate(self.SENSORY_CONFIG):
            value = prediction.get(key, 5.0)
            _mini_bar(bars_frame, es, en, value, color, i)

        # Disclaimer
        ctk.CTkLabel(
            self,
            text=L("ai_estimate_hint"),
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
            wraplength=340,
        ).pack(padx=14, pady=(0, 10))
        
        if self._on_save and self._prediction:
            ctk.CTkButton(
                self, text=L("ai_save_cat"),
                font=FONTS["small"], height=28,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color="#000000", corner_radius=6,
                command=self._save_prediction
            ).pack(pady=(4, 10))

    def _save_prediction(self):
        if not self._prediction: return
        from logic.api_client import api
        bean_id = getattr(self._bean, 'id', None) or self._bean.get("id")
        if bean_id:
            update_data = {
                "expected_acidity": self._prediction.get("acidity"),
                "expected_sweetness": self._prediction.get("sweetness"),
                "expected_body": self._prediction.get("body"),
                "expected_bitterness": self._prediction.get("bitterness")
            }
            api.update_bean(bean_id, update_data)
            
        if self._on_save:
            self._on_save()



# ── Bonus — Cluster Section ──────────────────────────────────────────────────────
class ClusterSection(ctk.CTkFrame):
    """
    Renders the K-Means extraction cluster cards for the Dashboard.
    Each cluster shows: icon, name, count, and key averages.
    """

    CLUSTER_COLORS = [
        COLORS["accent"],
        COLORS["info"],
        COLORS["success"],
    ]

    AVERAGE_LABELS = {
        "score":           ("Score",    "Score"),
        "ratio":           ("Ratio",    "Ratio"),
        "extraction_time": ("Tiempo",   "Time"),
        "acidity":         ("Acidez",   "Acidity"),
        "sweetness":       ("Dulzor",   "Sweetness"),
        "bitterness":      ("Amargor",  "Bitterness"),
    }

    def __init__(self, parent, clusters: list, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columnconfigure((0, 1, 2), weight=1)
        self._clusters = clusters
        self._build()

    def _build(self):
        if not self._clusters:
            ctk.CTkLabel(
                self,
                text=L("ai_not_enough_data"),
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, columnspan=3, pady=8, padx=24, sticky="w")
            return

        for col, cluster in enumerate(self._clusters[:3]):
            self._cluster_card(col, cluster)

    def _cluster_card(self, col: int, cluster: dict):
        color = self.CLUSTER_COLORS[col % len(self.CLUSTER_COLORS)]
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=CORNER_RADIUS["card"],
        )
        card.grid(
            row=0, column=col, sticky="nsew",
            padx=(0, 8) if col < 2 else 0, pady=0,
        )
        card.columnconfigure(0, weight=1)

        # Top color stripe
        stripe = ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=2)
        stripe.pack(fill="x")
        stripe.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        inner.columnconfigure(0, weight=1)

        # Icon + Label
        ctk.CTkLabel(
            inner,
            text=f"{cluster['icon']}  {L(cluster['label_en'].lower().replace(' ', '_'))}",
            font=FONTS["subhead"],
            text_color=color,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text=f"{cluster['count']} shot{'s' if cluster['count'] != 1 else ''}",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(fill="x", pady=(2, 6))

        # Key averages
        avgs = cluster.get("averages", {})
        display_keys = ["score", "ratio", "extraction_time", "acidity", "sweetness"]
        for key in display_keys:
            if key not in avgs:
                continue
            es, en = self.AVERAGE_LABELS.get(key, (key, key))
            val    = avgs[key]
            unit   = "s" if key == "extraction_time" else ""
            row_f  = ctk.CTkFrame(inner, fg_color="transparent")
            row_f.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row_f,
                text=f"{es}/{en}:",
                font=FONTS["caption"],
                text_color=COLORS["text_muted"],
            ).pack(side="left")
            ctk.CTkLabel(
                row_f,
                text=f"{val:.1f}{unit}",
                font=FONTS["caption"],
                text_color=COLORS["text_primary"],
            ).pack(side="right")
