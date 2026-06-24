# logic/ai/flavor_predictor.py
# Feature #2 — Flavor Predictor: MLP neural network that predicts the sensory
# profile (acidity, sweetness, body, bitterness) of a coffee bean.
#
# Architecture v3 — Domain-feature encoding (replaces OrdinalEncoder):
# ─────────────────────────────────────────────────────────────────────
# The previous version used OrdinalEncoder, which assigned arbitrary integer
# codes to category labels (e.g. "Bourbon"→2, "Caturra"→4). This has two
# critical flaws:
#   1. Unseen varieties get code=-1 and produce identical, meaningless output.
#   2. The model learns "code 4 → X" instead of "this variety is acidic → X".
#
# This version uses feature engineering: every categorical input (variety,
# process, country) is converted into its domain-knowledge sensory deltas
# BEFORE entering the MLP. The MLP only sees continuous numbers:
#
#   variety_acid_boost   — e.g. Gesha=+1.5, Caturra=0.0, unknown=0.0
#   process_acid_delta   — e.g. Natural=-2.5, Washed=+1.5
#   process_sweet_delta
#   process_body_delta
#   process_bitter_delta
#   country_acid_delta   — e.g. Brazil=-2.0, Ethiopia=+1.8
#   country_sweet_delta
#   country_body_delta
#   country_bitter_delta
#   altitude_masl        — raw (StandardScaler normalises it)
#   days_since_roast     — raw
#
# Result: a totally new variety or country → sensible neutral fallback (0.0),
# not broken output. Blends → average of component deltas.

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "flavor_predictor.joblib"

SENSORY_TARGETS = ["acidity", "sweetness", "body", "bitterness"]
REAL_WEIGHT = 3.0

# ── Domain lookup tables (mirrors synthetic_data.py) ────────────────────────────
# These are the single source of truth for categorical → numeric conversion.
# They live here so prediction never depends on the training data module.

_PROCESS_PROFILE: dict[str, dict] = {
    "Lavado / Washed":        {"acidity": +1.5, "sweetness": -0.5, "body": -1.0, "bitterness": -0.5},
    "Washed":                 {"acidity": +1.5, "sweetness": -0.5, "body": -1.0, "bitterness": -0.5},
    "Natural":                {"acidity": -2.5, "sweetness": +2.5, "body": +1.8, "bitterness": +0.2},
    "Honey":                  {"acidity": +0.2, "sweetness": +1.2, "body": +0.8, "bitterness": -0.2},
    "Anaeróbico / Anaerobic": {"acidity": +0.3, "sweetness": +1.8, "body": +1.5, "bitterness": +0.3},
    "Anaerobic":              {"acidity": +0.3, "sweetness": +1.8, "body": +1.5, "bitterness": +0.3},
    "Experimental":           {"acidity": +0.8, "sweetness": +0.8, "body": +0.8, "bitterness": +0.5},
    "Carbónico / Carbonic":   {"acidity": +0.5, "sweetness": +2.0, "body": +1.2, "bitterness": +0.2},
}
_PROCESS_ZERO = {"acidity": 0.0, "sweetness": 0.0, "body": 0.0, "bitterness": 0.0}

_COUNTRY_PROFILE: dict[str, dict] = {
    "Ethiopia":    {"acidity": +1.8, "sweetness": +0.5, "body": -0.8, "bitterness": -0.5},
    "Kenya":       {"acidity": +2.0, "sweetness": +0.3, "body": -0.5, "bitterness": -0.3},
    "Yemen":       {"acidity": +0.8, "sweetness": +1.0, "body": +0.5, "bitterness": +0.3},
    "Colombia":    {"acidity": +0.8, "sweetness": +0.5, "body": +0.3, "bitterness": -0.2},
    "Guatemala":   {"acidity": +0.5, "sweetness": +0.3, "body": +0.5, "bitterness": +0.0},
    # Costa Rica: clean but warm — moderate acidity, high sweetness, medium body
    "Costa Rica":  {"acidity": +0.2, "sweetness": +0.9, "body": +0.5, "bitterness": -0.3},
    "Panama":      {"acidity": +0.8, "sweetness": +0.8, "body": +0.0, "bitterness": -0.3},
    "Honduras":    {"acidity": +0.3, "sweetness": +0.3, "body": +0.5, "bitterness": +0.0},
    "El Salvador": {"acidity": +0.2, "sweetness": +0.5, "body": +0.5, "bitterness": -0.1},
    "Brazil":      {"acidity": -2.0, "sweetness": +1.2, "body": +1.5, "bitterness": +0.5},
    "Brasil":      {"acidity": -2.0, "sweetness": +1.2, "body": +1.5, "bitterness": +0.5},
    "Peru":        {"acidity": +0.3, "sweetness": +0.5, "body": +0.5, "bitterness": -0.2},
    "Bolivia":     {"acidity": +0.8, "sweetness": +0.5, "body": +0.3, "bitterness": -0.2},
    "Nicaragua":   {"acidity": +0.4, "sweetness": +0.4, "body": +0.5, "bitterness": -0.1},
    "Mexico":      {"acidity": +0.2, "sweetness": +0.3, "body": +0.5, "bitterness": +0.0},
    "Indonesia":   {"acidity": -0.5, "sweetness": +0.3, "body": +1.8, "bitterness": +0.8},
    "Vietnam":     {"acidity": -1.0, "sweetness": +0.5, "body": +2.0, "bitterness": +1.0},
    "India":       {"acidity": -0.3, "sweetness": +0.3, "body": +1.2, "bitterness": +0.5},
}
_COUNTRY_ZERO = {"acidity": 0.0, "sweetness": 0.0, "body": 0.0, "bitterness": 0.0}

# Variety sensory profiles
_VARIETY_PROFILE: dict[str, dict] = {
    "Gesha / Geisha":   {"acidity": +1.5, "sweetness": +1.0, "body": -1.0, "bitterness": -0.5},
    "Geisha":           {"acidity": +1.5, "sweetness": +1.0, "body": -1.0, "bitterness": -0.5},
    "SL28":             {"acidity": +1.2, "sweetness": +0.5, "body": -0.5, "bitterness": +0.0},
    "SL34":             {"acidity": +1.0, "sweetness": +0.5, "body": +0.0, "bitterness": +0.0},
    "Heirloom":         {"acidity": +0.5, "sweetness": +0.8, "body": -0.2, "bitterness": -0.2},
    "Pacamara":         {"acidity": +0.8, "sweetness": +0.5, "body": +1.0, "bitterness": +0.0},
    "Bourbon":          {"acidity": +0.2, "sweetness": +1.0, "body": +0.5, "bitterness": -0.2},
    "Red Bourbon":      {"acidity": +0.2, "sweetness": +1.0, "body": +0.5, "bitterness": -0.2},
    "Typica":           {"acidity": +0.0, "sweetness": +0.5, "body": +0.0, "bitterness": +0.0},
    "Caturra":          {"acidity": +0.0, "sweetness": +0.5, "body": +0.2, "bitterness": +0.0},
    "Catuai":           {"acidity": -0.1, "sweetness": +0.8, "body": +0.5, "bitterness": +0.0},
    "Yellow Catuai":    {"acidity": -0.1, "sweetness": +1.0, "body": +0.8, "bitterness": -0.2},
    "Yellow Caturra":   {"acidity": -0.1, "sweetness": +0.8, "body": +0.5, "bitterness": -0.1},
    "Mundo Novo":       {"acidity": -0.3, "sweetness": +0.5, "body": +1.0, "bitterness": +0.5},
    "Maragogipe":       {"acidity": +0.3, "sweetness": +0.5, "body": +0.5, "bitterness": +0.0},
    "Icatu":            {"acidity": -0.2, "sweetness": +0.5, "body": +0.5, "bitterness": +0.2},
    "Catimor":          {"acidity": -0.2, "sweetness": +0.2, "body": +0.8, "bitterness": +0.5},
    "Sarchimor":        {"acidity": -0.1, "sweetness": +0.3, "body": +0.8, "bitterness": +0.3},
    "Castillo":         {"acidity": -0.1, "sweetness": +0.5, "body": +0.5, "bitterness": +0.2},
    "Tabi":             {"acidity": +0.2, "sweetness": +0.5, "body": +0.5, "bitterness": +0.0},
    "Sudan Rume":       {"acidity": +0.8, "sweetness": +0.8, "body": +0.2, "bitterness": -0.2},
    "74110":            {"acidity": +1.2, "sweetness": +0.8, "body": -0.5, "bitterness": -0.3},
    "74112":            {"acidity": +1.0, "sweetness": +0.8, "body": -0.5, "bitterness": -0.3},
}
_VARIETY_ZERO = {"acidity": 0.0, "sweetness": 0.0, "body": 0.0, "bitterness": 0.0}

# Blend separators
_BLEND_SEPS = (" y ", " and ", "/", "+", ",", "&", " & ")

# Altitude acidity gain: +0.5 per 500m above 1000m baseline
_ALT_ACID_PER_500M = 0.5

# Feature column names fed to the MLP (for documentation)
FEATURE_NAMES = [
    "variety_acid_boost",
    "process_acid", "process_sweet", "process_body", "process_bitter",
    "country_acid", "country_sweet", "country_body", "country_bitter",
    "altitude_masl", "days_since_roast",
]


def _fuzzy_lookup_variety(name: str) -> dict:
    """
    Return the sensory profile for a variety name, with fuzzy matching.
    Unknown varieties return 0s (neutral).
    """
    if not name or name in ("Unknown", "Otro / Other", "Other"):
        return _VARIETY_ZERO
    if name in _VARIETY_PROFILE:
        return _VARIETY_PROFILE[name]
    name_l = name.lower()
    best_score, best_val = 0, _VARIETY_ZERO
    for known, val in _VARIETY_PROFILE.items():
        k_l = known.lower()
        if name_l in k_l or k_l in name_l:
            score = len(set(name_l) & set(k_l))
            if score > best_score:
                best_score, best_val = score, val
    return best_val


def _resolve_variety_boost(raw: str) -> dict:
    """
    Handle blends (e.g. 'Caturra y Catuai') by averaging each component's
    sensory profile. Totally unknown → 0.0 (neutral, not broken).
    """
    if not raw:
        return _VARIETY_ZERO
    # Split into components
    components = [raw]
    for sep in _BLEND_SEPS:
        parts = []
        for c in components:
            parts.extend(c.split(sep))
        components = [p.strip() for p in parts if p.strip()]

    boosts = [_fuzzy_lookup_variety(c) for c in components]
    if not boosts:
        return _VARIETY_ZERO

    return {
        "acidity": float(np.mean([b["acidity"] for b in boosts])),
        "sweetness": float(np.mean([b["sweetness"] for b in boosts])),
        "body": float(np.mean([b["body"] for b in boosts])),
        "bitterness": float(np.mean([b["bitterness"] for b in boosts])),
    }


def _resolve_process(raw: str) -> dict:
    """Return process sensory delta dict; neutral 0s for unknown process."""
    if not raw:
        return _PROCESS_ZERO
    # Exact match
    if raw in _PROCESS_PROFILE:
        return _PROCESS_PROFILE[raw]
    # Substring fuzzy (e.g. "Honey Process" → "Honey")
    raw_l = raw.lower()
    for key, val in _PROCESS_PROFILE.items():
        if key.lower() in raw_l or raw_l in key.lower():
            return val
    return _PROCESS_ZERO  # unknown process → neutral


def _resolve_country(raw: str) -> dict:
    """Return country sensory delta dict; neutral 0s for unknown country."""
    if not raw:
        return _COUNTRY_ZERO
    if raw in _COUNTRY_PROFILE:
        return _COUNTRY_PROFILE[raw]
    raw_l = raw.lower()
    for key, val in _COUNTRY_PROFILE.items():
        if key.lower() in raw_l or raw_l in key.lower():
            return val
    return _COUNTRY_ZERO  # unknown country → neutral


def bean_to_features(variety: str, process: str, country: str,
                     altitude: float, days: float) -> list[float]:
    """
    Convert raw bean attributes into an 11-dimensional numeric feature vector.
    This function is the single source of truth used by both training and inference.
    """
    v       = _resolve_variety_boost(str(variety))
    p       = _resolve_process(str(process))
    c       = _resolve_country(str(country))
    alt_acid = max(0.0, (altitude - 1000) / 500) * _ALT_ACID_PER_500M

    return [
        v["acidity"] + alt_acid,     # variety_acid
        v["sweetness"],              # variety_sweet
        v["body"],                   # variety_body
        v["bitterness"],             # variety_bitter
        p["acidity"],                # process_acid
        p["sweetness"],              # process_sweet
        p["body"],                   # process_body
        p["bitterness"],             # process_bitter
        c["acidity"],                # country_acid
        c["sweetness"],              # country_sweet
        c["body"],                   # country_body
        c["bitterness"],             # country_bitter
        altitude,                    # altitude_masl
        days,                        # days_since_roast
    ]




class FlavorPredictor:
    """
    MLP-based sensory profile predictor for coffee beans.

    Uses domain-feature encoding instead of OrdinalEncoder so that:
    - Unseen varieties → neutral fallback (0.0 acidity boost), not -1 noise
    - Blends → averaged boost across components
    - New countries/processes → neutral fallback, not broken

    Input features: 11 continuous values derived from domain knowledge
    Output: acidity, sweetness, body, bitterness (1–10 each)
    """

    def __init__(self):
        self._model   = None   # sklearn Pipeline (StandardScaler + MLP)
        self._trained = False
        self._lock    = threading.Lock()

    # ── Persistence ─────────────────────────────────────────────────────────────
    def save(self):
        import joblib
        MODEL_PATH.parent.mkdir(exist_ok=True)
        with self._lock:
            joblib.dump(self._model, MODEL_PATH)

    def load(self) -> bool:
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
        Train on synthetic beans + (optionally) real user data.
        real_df must have columns: variety, process, origin_country,
        altitude_masl, days_since_roast, acidity, sweetness, body, bitterness.
        """
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.feature_extraction.text import TfidfVectorizer
        from logic.ai.synthetic_data import generate_beans
        import os

        # 1. Load Synthetic Data
        synth_df = generate_beans(300)
        frames, weights = [synth_df], [np.ones(len(synth_df))]

        # 2. Load Real CQI Dataset from archive
        cqi_path = Path(__file__).resolve().parents[2] / "archive" / "arabica_data_cleaned.csv"
        if cqi_path.exists():
            cqi_df = pd.read_csv(cqi_path)
            cqi_df = cqi_df.dropna(subset=['Country.of.Origin', 'Processing.Method', 'Variety', 'altitude_mean_meters', 'Acidity', 'Sweetness', 'Body'])
            # Map CQI to standard format
            cqi_mapped = pd.DataFrame()
            cqi_mapped["variety"] = cqi_df["Variety"]
            cqi_mapped["process"] = cqi_df["Processing.Method"]
            cqi_mapped["origin_country"] = cqi_df["Country.of.Origin"]
            cqi_mapped["altitude_masl"] = pd.to_numeric(cqi_df["altitude_mean_meters"], errors="coerce").fillna(1200)
            cqi_mapped["days_since_roast"] = 14.0
            cqi_mapped["notes"] = "" # No notes in CQI
            cqi_mapped["acidity"] = pd.to_numeric(cqi_df["Acidity"], errors="coerce")
            cqi_mapped["sweetness"] = pd.to_numeric(cqi_df["Sweetness"], errors="coerce")
            cqi_mapped["body"] = pd.to_numeric(cqi_df["Body"], errors="coerce")
            cqi_mapped["bitterness"] = pd.to_numeric(cqi_df["Balance"], errors="coerce") # Proxy for bitterness/balance
            cqi_mapped = cqi_mapped.dropna()
            if len(cqi_mapped) > 0:
                frames.append(cqi_mapped)
                weights.append(np.ones(len(cqi_mapped)))

        # 3. Load User Real Data
        if real_df is not None and len(real_df) >= 3:
            real_clean = real_df.dropna(subset=SENSORY_TARGETS)
            if len(real_clean) > 0:
                # Ensure notes column exists
                if "notes" not in real_clean.columns:
                    real_clean["notes"] = ""
                else:
                    real_clean["notes"] = real_clean["notes"].fillna("")
                frames.append(real_clean)
                weights.append(np.full(len(real_clean), REAL_WEIGHT))

        df_all = pd.concat(frames, ignore_index=True)
        df_all["altitude_masl"]   = pd.to_numeric(df_all["altitude_masl"],   errors="coerce").fillna(1200)
        df_all["days_since_roast"]= pd.to_numeric(df_all["days_since_roast"],errors="coerce").fillna(14)
        df_all["notes"]           = df_all["notes"].fillna("").astype(str)
        df_all = df_all.dropna(subset=SENSORY_TARGETS)
        w_all  = np.concatenate(weights)[: len(df_all)]

        # Build feature matrix (DataFrame) to pass to ColumnTransformer
        X_df = pd.DataFrame([
            bean_to_features(
                row["variety"], row["process"], row["origin_country"],
                float(row["altitude_masl"]), float(row["days_since_roast"])
            )
            for _, row in df_all.iterrows()
        ], columns=["v_acid", "v_sweet", "v_body", "v_bitter",
                    "p_acid", "p_sweet", "p_body", "p_bitter",
                    "c_acid", "c_sweet", "c_body", "c_bitter",
                    "alt", "days"])
        X_df["notes"] = df_all["notes"].values

        y = df_all[SENSORY_TARGETS].values.astype(float)

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), ["v_acid", "v_sweet", "v_body", "v_bitter", "p_acid", "p_sweet", "p_body", "p_bitter", "c_acid", "c_sweet", "c_body", "c_bitter", "alt", "days"]),
                ("text", TfidfVectorizer(max_features=100, ngram_range=(1, 2)), "notes")
            ]
        )

        model = Pipeline([
            ("preprocessor", preprocessor),
            ("mlp", MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                solver="adam",
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=30,
            )),
        ])
        model.fit(X_df, y, mlp__sample_weight=w_all)

        with self._lock:
            self._model   = model
            self._trained = True

        self.save()

    def train_in_background(self, real_df: Optional[pd.DataFrame] = None):
        t = threading.Thread(target=self.train, args=(real_df,), daemon=True)
        t.start()

    # ── Inference ───────────────────────────────────────────────────────────────────────
    def predict(self, bean) -> dict:
        """
        Predict sensory profile for a Bean ORM object or dict.
        Returns dict: {acidity, sweetness, body, bitterness, confidence}
        Works correctly for any variety/process/country, including unknown ones.
        If Bean.notes contains flavor descriptors (caramel, honey, hazelnut...)
        the prediction is further corrected using keyword matching rules.
        """
        if not self._trained or self._model is None:
            return {}

        variety, process, country, altitude, days, notes = self._extract_attrs(bean)
        features_list = bean_to_features(variety, process, country, altitude, days)

        cols = ["v_acid", "v_sweet", "v_body", "v_bitter", "p_acid", "p_sweet", "p_body", "p_bitter", "c_acid", "c_sweet", "c_body", "c_bitter", "alt", "days"]
        X_df = pd.DataFrame([features_list], columns=cols)
        X_df["notes"] = [notes]

        with self._lock:
            pred = self._model.predict(X_df)[0]

        result = {
            k: float(np.clip(round(v, 1), 1.0, 10.0))
            for k, v in zip(SENSORY_TARGETS, pred)
        }
        result["confidence"] = "low"

        return result

    # ── Helpers ──────────────────────────────────────────────────────────────────
    def _extract_attrs(self, bean) -> tuple:
        """Extract raw attributes from a Bean ORM object or dict."""
        if hasattr(bean, "__dict__"):
            variety  = getattr(bean, "variety",        None) or "Unknown"
            process  = getattr(bean, "process",        None) or "Unknown"
            country  = getattr(bean, "origin_country", None) or "Unknown"
            altitude = float(getattr(bean, "altitude_masl",    1200) or 1200)
            days     = float(getattr(bean, "days_since_roast",   14) or 14)
            notes    = getattr(bean, "notes", None) or ""
        else:
            variety  = bean.get("variety",        "Unknown")
            process  = bean.get("process",        "Unknown")
            country  = bean.get("origin_country", "Unknown")
            altitude = float(bean.get("altitude_masl",   1200) or 1200)
            days     = float(bean.get("days_since_roast",  14) or 14)
            notes    = bean.get("notes", "") or ""
        return str(variety), str(process), str(country), altitude, days, str(notes)


# Module-level singleton
flavor_predictor = FlavorPredictor()
