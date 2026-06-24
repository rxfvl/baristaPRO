# logic/ai/shot_advisor.py
# Feature #1 — Shot Advisor: RandomForest model that predicts extraction score
# and suggests parameter adjustments to improve the next shot.

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "shot_advisor.joblib"

# Feature columns (must match generate_extractions output)
FEATURES = [
    "dose_in", "yield_out", "ratio",
    "extraction_time", "water_temp",
    "pressure", "pre_infusion_time",
]

# Real data weight multiplier vs synthetic
REAL_WEIGHT = 3.0


class ShotAdvisor:
    """
    RandomForest-based score predictor for espresso extractions.
    Trained on a mix of synthetic + real user data.
    Suggests small parameter tweaks to improve predicted score.
    """

    def __init__(self):
        self._model   = None
        self._trained = False
        self._lock    = threading.Lock()

    # ── Persistence ─────────────────────────────────────────────────────────────
    def save(self):
        import joblib
        MODEL_PATH.parent.mkdir(exist_ok=True)
        with self._lock:
            joblib.dump(self._model, MODEL_PATH)

    def load(self) -> bool:
        """Returns True if model was loaded successfully."""
        import joblib
        if MODEL_PATH.exists():
            with self._lock:
                self._model   = joblib.load(MODEL_PATH)
                self._trained = True
            return True
        return False

    # ── Training ─────────────────────────────────────────────────────────────────
    def train(self, real_df: Optional[pd.DataFrame] = None):
        """
        Train on synthetic data + real user data.
        real_df must have columns: FEATURES + ['score']
        """
        from sklearn.ensemble import RandomForestRegressor
        from logic.ai.synthetic_data import generate_extractions

        synth_df = generate_extractions(250)

        frames, weights = [synth_df], [np.ones(len(synth_df))]

        if real_df is not None and len(real_df) >= 1:
            real_clean = real_df.copy()
            real_clean["ratio"] = real_clean["yield_out"] / real_clean["dose_in"].replace(0, np.nan)
            real_clean = real_clean.dropna(subset=FEATURES + ["score"])
            if len(real_clean) > 0:
                # Make the user's real data heavily outweigh the synthetic data
                # Total real weight = 500 (vs 250 for synthetic) -> forces the model to respect the user's scores
                dynamic_weight = 500.0 / len(real_clean)
                frames.append(real_clean[FEATURES + ["score", "is_synthetic"] if "is_synthetic" in real_clean.columns else FEATURES + ["score"]])
                weights.append(np.full(len(real_clean), dynamic_weight))

        df_all = pd.concat(frames, ignore_index=True)
        # Add ratio col to synthetic rows if missing
        if "ratio" not in df_all.columns:
            df_all["ratio"] = df_all["yield_out"] / df_all["dose_in"].replace(0, np.nan)

        df_all = df_all.dropna(subset=FEATURES + ["score"])
        w_all  = np.concatenate(weights)

        X = df_all[FEATURES].values
        y = df_all["score"].values

        model = RandomForestRegressor(
            n_estimators=120,
            max_depth=10,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X, y, sample_weight=w_all)

        with self._lock:
            self._model   = model
            self._trained = True

        self.save()

    def train_in_background(self, real_df: Optional[pd.DataFrame] = None):
        """Launch training in a daemon thread so UI isn't blocked."""
        t = threading.Thread(target=self.train, args=(real_df,), daemon=True)
        t.start()

    # ── Inference ────────────────────────────────────────────────────────────────
    def predict_score(self, params: dict) -> float:
        """Predict score for a given parameter dict."""
        if not self._trained or self._model is None:
            return 0.0
        row = self._params_to_row(params)
        with self._lock:
            return float(self._model.predict([row])[0])

    def suggest(self, params: dict) -> dict:
        """
        Given current shot parameters, return a dict with:
            - predicted_score: float
            - suggested_params: dict  (best variation found)
            - deltas: dict  (human-readable diff)
            - suggested_score: float
        Returns empty dict if model isn't trained.
        """
        if not self._trained or self._model is None:
            return {}

        base_score = self.predict_score(params)

        diagnostic_message, state = self._generate_diagnostics(params)

        # Search space: small nudges around current values
        search_grid = self._build_search_grid(params, state)

        if not search_grid:
            return {"predicted_score": round(base_score, 1), "deltas": {}, "suggested_score": round(base_score, 1), "diagnostic": diagnostic_message}

        rows   = np.array([self._params_to_row(p) for p in search_grid])
        with self._lock:
            scores = self._model.predict(rows)

        best_idx   = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score <= base_score + 0.1:
            return {
                "predicted_score":  round(base_score, 1),
                "deltas":           {},
                "suggested_score":  round(base_score, 1),
                "diagnostic":       diagnostic_message,
                "message":          "already_optimal" if base_score >= 7.0 else "need_drastic_change",
            }

        best_params = search_grid[best_idx]
        deltas = {}
        for k in ["dose_in", "yield_out", "extraction_time"]:
            diff = best_params[k] - params.get(k, 0)
            if abs(diff) > 0.05:
                if k == "extraction_time":
                    direction = "Más fina" if diff > 0 else "Más gruesa"
                    deltas["Molienda"] = f"{direction} (objetivo {diff:+.1f}s)"
                else:
                    deltas[k] = round(diff, 2)

        return {
            "predicted_score":  round(base_score, 1),
            "suggested_params": best_params,
            "deltas":           deltas,
            "suggested_score":  round(best_score, 1),
            "diagnostic":       diagnostic_message,
        }

    def _generate_diagnostics(self, params: dict) -> tuple[str, str]:
        """
        Generate qualitative text-based diagnostic reasoning based on sensory inputs.
        Returns (message, state).
        States: 'under', 'over', 'watery', 'intense_bitter', 'balanced'
        """
        acidity = params.get("acidity", 5)
        sweetness = params.get("sweetness", 5)
        body = params.get("body", 5)
        bitterness = params.get("bitterness", 5)

        state = "balanced"
        issues = []

        if acidity >= 8 and sweetness <= 4:
            state = "under"
            issues.append("El café está sub-extraído (muy ácido/agrio y sin dulzor). Intenta afinar un poco la molienda o alargar el ratio (más yield).")
        elif bitterness >= 8 and sweetness <= 4:
            state = "over"
            issues.append("El café está sobre-extraído (muy amargo y seco). Intenta engrosar un poco la molienda o acortar el ratio (menos yield).")
        elif acidity <= 3 and bitterness <= 3 and body <= 4:
            state = "watery"
            issues.append("El shot está aguado o falto de intensidad. Intenta usar un ratio más corto (ej. 1:1.5) o aumentar la dosis.")
        elif body >= 8 and bitterness >= 7:
            state = "intense_bitter"
            issues.append("El shot es muy intenso y denso, pero se está volviendo amargo. Prueba alargar un poco el ratio (ej. 1:2.5) para diluir y suavizar.")
        
        if not issues:
            if sweetness >= 7 and acidity >= 5 and bitterness <= 4:
                return "Excelente balance. Los sabores están en su punto dulce.", "balanced"
            return "El balance es decente, pero puedes realizar pequeños micro-ajustes en la molienda o la dosis para buscar el 'sweet spot'.", "balanced"
        
        return " ".join(issues), state

    # ── Helpers ──────────────────────────────────────────────────────────────────
    def _params_to_row(self, params: dict) -> list:
        dose  = params.get("dose_in", 18.0)
        yield_ = params.get("yield_out", 36.0)
        ratio = yield_ / dose if dose > 0 else 2.0
        return [
            dose,
            yield_,
            ratio,
            params.get("extraction_time", 27.0),
            params.get("water_temp", 93.0),
            params.get("pressure", 9.0),
            params.get("pre_infusion_time", 0.0),
        ]

    def _build_search_grid(self, params: dict, state: str) -> list[dict]:
        """Generate candidate parameter combinations, restricted by extraction state."""
        candidates = []
        dose  = params.get("dose_in", 18.0)
        yield_ = params.get("yield_out", 36.0)
        time_  = params.get("extraction_time", 27.0)
        temp   = params.get("water_temp", 93.0)
        press  = params.get("pressure", 9.0)
        pre    = params.get("pre_infusion_time", 0.0)

        # Allowable deltas based on state
        d_dose_opts = [-0.5, 0.0, 0.5]
        d_yield_opts = [-2.0, 0.0, 2.0]
        d_time_opts = [-2.0, 0.0, 2.0] # Representa Molienda: -2s = Gruesa, +2s = Fina

        if state == "under":
            # Si sub-extraído: Prohibido bajar yield, prohibido bajar tiempo (engrosar molienda)
            d_yield_opts = [0.0, 2.0, 4.0]
            d_time_opts = [0.0, 2.0]
        elif state == "over":
            # Si sobre-extraído: Prohibido subir yield, prohibido subir tiempo (afinar molienda)
            d_yield_opts = [-4.0, -2.0, 0.0]
            d_time_opts = [-2.0, 0.0]
        elif state == "watery":
            # Si aguado: Subir dosis o bajar yield. Prohibido subir yield.
            d_dose_opts = [0.0, 0.5, 1.0]
            d_yield_opts = [-2.0, 0.0]
        elif state == "intense_bitter":
            # Si muy intenso y amargo: Subir yield o bajar dosis.
            d_dose_opts = [-0.5, 0.0]
            d_yield_opts = [0.0, 2.0, 4.0]

        for d_dose in d_dose_opts:
            for d_yield in d_yield_opts:
                for d_time in d_time_opts:
                    if d_dose == 0 and d_yield == 0 and d_time == 0:
                        continue
                    new_dose  = max(dose  + d_dose,  10.0)
                    new_yield = max(yield_+ d_yield, 15.0)
                    candidates.append({
                        "dose_in":           new_dose,
                        "yield_out":         new_yield,
                        "extraction_time":   max(time_ + d_time, 15.0),
                        "water_temp":        temp,   # Fijo
                        "pressure":          press,  # Fijo
                        "pre_infusion_time": pre,    # Fijo
                    })
        return candidates


# Module-level singleton
advisor = ShotAdvisor()
