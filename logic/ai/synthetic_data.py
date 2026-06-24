# logic/ai/synthetic_data.py
# Generates realistic synthetic espresso data for pre-training AI models.
# Data follows SCA extraction guidelines and real-world coffee sensory knowledge.
#
# Key domain corrections (v2):
#   - Country-level acidity/body profiles are now explicit (Brazil ≠ Ethiopia)
#   - Natural process acidity penalty increased to -2.5 (was -0.5)
#   - OrdinalEncoder limitation bypassed: country/variety encoded via domain rules,
#     not numeric codes, so the MLP learns meaningful relationships
#   - "Unknown" variety handled gracefully: falls back to process + country profile

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

# ── Domain constants ────────────────────────────────────────────────────────────
VARIETIES  = ["Bourbon", "Caturra", "Catuai", "Gesha / Geisha", "Typica",
               "Pacamara", "Heirloom", "SL28", "SL34", "Yellow Caturra",
               "Yellow Catuai", "Red Bourbon", "Mundo Novo"]
PROCESSES  = ["Lavado / Washed", "Natural", "Honey",
               "Anaeróbico / Anaerobic", "Experimental"]
COUNTRIES  = ["Ethiopia", "Colombia", "Guatemala", "Kenya",
               "Brazil", "Brasil", "Costa Rica", "Panama", "Honduras",
               "El Salvador", "Peru", "Bolivia", "Yemen"]

# ── Process sensory profiles ─────────────────────────────────────────────────
# Delta relative to baseline 5.0. Calibrated against SCA flavor wheel research.
PROCESS_PROFILE = {
    # Washed: clean, bright, high acidity, lighter body
    "Lavado / Washed":        {"acidity": +1.5, "sweetness": -0.5, "body": -1.0, "bitterness": -0.5},
    "Washed":                 {"acidity": +1.5, "sweetness": -0.5, "body": -1.0, "bitterness": -0.5},
    # Natural: fruit-forward, sweet, full body, LOW acidity (chocolate/nutty dominant)
    "Natural":                {"acidity": -2.5, "sweetness": +2.5, "body": +1.8, "bitterness": +0.2},
    # Honey: balanced middle-ground
    "Honey":                  {"acidity": +0.2, "sweetness": +1.2, "body": +0.8, "bitterness": -0.2},
    # Anaerobic: complex, sweet, high body, moderate acidity
    "Anaeróbico / Anaerobic": {"acidity": +0.3, "sweetness": +1.8, "body": +1.5, "bitterness": +0.3},
    "Anaerobic":              {"acidity": +0.3, "sweetness": +1.8, "body": +1.5, "bitterness": +0.3},
    # Experimental: highly variable
    "Experimental":           {"acidity": +0.8, "sweetness": +0.8, "body": +0.8, "bitterness": +0.5},
}

# ── Country sensory profiles ─────────────────────────────────────────────────
# Captures the terroir effect. These are the most impactful real-world patterns.
COUNTRY_PROFILE = {
    # East Africa: volcanic soil, high altitude, high acidity, floral/fruity
    "Ethiopia":     {"acidity": +1.8, "sweetness": +0.5, "body": -0.8, "bitterness": -0.5},
    "Kenya":        {"acidity": +2.0, "sweetness": +0.3, "body": -0.5, "bitterness": -0.3},
    "Yemen":        {"acidity": +0.8, "sweetness": +1.0, "body": +0.5, "bitterness": +0.3},
    # Central America: balanced, medium acidity, pleasant sweetness
    "Colombia":     {"acidity": +0.8, "sweetness": +0.5, "body": +0.3, "bitterness": -0.2},
    "Guatemala":    {"acidity": +0.5, "sweetness": +0.3, "body": +0.5, "bitterness": +0.0},
    "Costa Rica":   {"acidity": +0.5, "sweetness": +0.5, "body": +0.3, "bitterness": -0.2},
    "Panama":       {"acidity": +0.8, "sweetness": +0.8, "body": +0.0, "bitterness": -0.3},
    "Honduras":     {"acidity": +0.3, "sweetness": +0.3, "body": +0.5, "bitterness": +0.0},
    "El Salvador":  {"acidity": +0.2, "sweetness": +0.5, "body": +0.5, "bitterness": -0.1},
    # South America — nuts, chocolate, low acidity, heavy body
    "Brazil":       {"acidity": -2.0, "sweetness": +1.2, "body": +1.5, "bitterness": +0.5},
    "Brasil":       {"acidity": -2.0, "sweetness": +1.2, "body": +1.5, "bitterness": +0.5},  # ES spelling
    "Peru":         {"acidity": +0.3, "sweetness": +0.5, "body": +0.5, "bitterness": -0.2},
    "Bolivia":      {"acidity": +0.8, "sweetness": +0.5, "body": +0.3, "bitterness": -0.2},
}

# ── Variety profiles ─────────────────────────────────────────────────────────
VARIETY_PROFILE = {
    "Gesha / Geisha":   {"acidity": +1.5, "sweetness": +1.0, "body": -1.0, "bitterness": -0.5},
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
}

# Altitude contribution: every 500m above 1000m adds ~+0.5 to acidity
ALTITUDE_ACIDITY_PER_500M = 0.5


def _clamp(arr: np.ndarray, lo=1.0, hi=10.0) -> np.ndarray:
    return np.clip(arr, lo, hi)


def _acidity_from_altitude(altitude_masl: float) -> float:
    """Linear acidity contribution from altitude above 1000m baseline."""
    return max(0.0, (altitude_masl - 1000) / 500) * ALTITUDE_ACIDITY_PER_500M


def _apply_profile(base: float, key: str, profile_dict: dict, field: str) -> float:
    delta = profile_dict.get(key, {}).get(field, 0.0)
    return base + delta


def _sensory_for_bean(variety: str, process: str, country: str,
                      altitude: float, rng: np.random.Generator) -> dict:
    """Compute ground-truth sensory values for one bean using domain knowledge."""
    base = 5.0

    p = PROCESS_PROFILE.get(process, {"acidity": 0, "sweetness": 0, "body": 0, "bitterness": 0})
    c = COUNTRY_PROFILE.get(country, {"acidity": 0, "sweetness": 0, "body": 0, "bitterness": 0})
    v = VARIETY_PROFILE.get(variety, {"acidity": 0, "sweetness": 0, "body": 0, "bitterness": 0})
    alt_acid = _acidity_from_altitude(altitude)

    acidity    = base + p["acidity"]    + c["acidity"]    + v["acidity"]    + alt_acid
    sweetness  = base + p["sweetness"]  + c["sweetness"]  + v["sweetness"]
    body       = base + p["body"]       + c["body"]       + v["body"]
    bitterness = base + p["bitterness"] + c["bitterness"] + v["bitterness"]

    # Small noise (σ=0.4) to avoid perfectly deterministic training data
    noise = rng.normal(0, 0.4, 4)
    return {
        "acidity":    float(np.clip(round(acidity    + noise[0]), 1, 10)),
        "sweetness":  float(np.clip(round(sweetness  + noise[1]), 1, 10)),
        "body":       float(np.clip(round(body       + noise[2]), 1, 10)),
        "bitterness": float(np.clip(round(bitterness + noise[3]), 1, 10)),
    }


def _generate_notes(variety: str, process: str, country: str, rng: np.random.Generator) -> str:
    notes = []
    
    if "Natural" in process:
        notes.extend(rng.choice(["chocolate", "nuez", "frutos rojos", "fresa", "terroso", "cacao", "pesado", "dulce"], 2, replace=False).tolist())
    elif "Lavado" in process or "Washed" in process:
        notes.extend(rng.choice(["limpio", "brillante", "cítrico", "floral", "jazmín", "limón", "sedoso", "equilibrado"], 2, replace=False).tolist())
    elif "Honey" in process:
        notes.extend(rng.choice(["miel", "caramelo", "dulce", "suave", "equilibrado", "panela"], 2, replace=False).tolist())
    elif "Anaeróbico" in process or "Anaerobic" in process:
        notes.extend(rng.choice(["vino", "fermentado", "tropical", "lychee", "cacao", "complejo"], 2, replace=False).tolist())
        
    if country in ["Ethiopia", "Kenya"]:
        notes.extend(rng.choice(["bergamota", "jazmín", "té negro", "frutal", "frambuesa"], 1).tolist())
    elif country in ["Brazil", "Brasil", "Colombia"]:
        notes.extend(rng.choice(["almendra", "avellana", "chocolate con leche", "caramelo", "melaza"], 1).tolist())
        
    if "Gesha" in variety:
        notes.extend(rng.choice(["jazmín", "té de melocotón", "delicado", "floral", "complejo"], 2, replace=False).tolist())
    elif "Pacamara" in variety:
        notes.extend(rng.choice(["hierbas", "especias", "cuerpo denso", "fruta madura"], 1).tolist())
        
    if not notes:
        notes.extend(["bueno", "café", "taza limpia"])
        
    rng.shuffle(notes)
    return ", ".join(notes)


def generate_extractions(n: int = 250) -> pd.DataFrame:
    """
    Generate n synthetic espresso extractions.
    Returns a DataFrame matching ExtractionLog columns (minus id/timestamps).
    """
    dose        = RNG.uniform(14.0, 22.0, n)
    ratio       = RNG.uniform(1.5, 3.2, n)
    yield_out   = dose * ratio
    time_       = RNG.uniform(20.0, 38.0, n)
    temp        = RNG.uniform(88.0, 96.5, n)
    pressure    = RNG.uniform(7.0, 10.5, n)
    pre_inf     = RNG.uniform(0.0, 6.0, n)

    ratio_score  = -3.0 * (ratio - 2.2) ** 2 + 1.0
    time_score   = -0.015 * (time_ - 27.0) ** 2 + 0.5
    temp_score   = -0.04  * (temp  - 92.0) ** 2 + 0.5
    press_score  = -0.3   * (pressure - 9.0) ** 2 + 0.3
    base_score   = 6.5 + ratio_score + time_score + temp_score + press_score
    score        = _clamp(base_score + RNG.normal(0, 0.4, n), 1.0, 10.0)

    acidity    = _clamp(5.0 + (ratio - 2.0) * 1.2 + RNG.normal(0, 0.6, n))
    sweetness  = _clamp(5.0 + (score - 6.5) * 0.4 + RNG.normal(0, 0.5, n))
    body       = _clamp(6.5 - (ratio - 2.0) * 0.8 + RNG.normal(0, 0.5, n))
    bitterness = _clamp(5.5 - (ratio - 2.0) * 1.0 + (38.0 - time_) * 0.05 + RNG.normal(0, 0.6, n))

    return pd.DataFrame({
        "dose_in":           dose,
        "yield_out":         yield_out,
        "ratio":             ratio,
        "extraction_time":   time_,
        "water_temp":        temp,
        "pressure":          pressure,
        "pre_infusion_time": pre_inf,
        "acidity":           acidity.round().astype(int),
        "sweetness":         sweetness.round().astype(int),
        "body":              body.round().astype(int),
        "bitterness":        bitterness.round().astype(int),
        "score":             score.round(1),
        "is_synthetic":      True,
    })


def generate_beans(n: int = 300) -> pd.DataFrame:
    """
    Generate n synthetic bean records using the corrected domain-knowledge model.
    Returns a DataFrame with variety, process, origin_country, altitude_masl,
    days_since_roast, and ground-truth sensory labels.
    """
    # Balance: ensure all process × country combinations are represented
    varieties    = RNG.choice(VARIETIES, n)
    processes    = RNG.choice(PROCESSES, n)
    countries    = RNG.choice(COUNTRIES, n)
    altitudes    = RNG.integers(800, 2400, n).astype(float)
    days_rested  = RNG.integers(7, 60, n).astype(float)

    rows = []
    for i in range(n):
        sensory = _sensory_for_bean(
            variety  = varieties[i],
            process  = processes[i],
            country  = countries[i],
            altitude = altitudes[i],
            rng      = RNG,
        )
        notes_str = _generate_notes(varieties[i], processes[i], countries[i], RNG)
        rows.append({
            "variety":          varieties[i],
            "process":          processes[i],
            "origin_country":   countries[i],
            "altitude_masl":    altitudes[i],
            "days_since_roast": days_rested[i],
            "notes":            notes_str,
            "is_synthetic":     True,
            **sensory,
        })

    # Explicitly add archetype rows so the MLP always sees extreme cases
    archetypes = [
        # Brazilian Natural — the T-BROKE profile
        {"variety": "Yellow Catuai", "process": "Natural", "origin_country": "Brasil",
         "altitude_masl": 1100.0, "days_since_roast": 10.0, "notes": "chocolate, cacahuate, terroso",
         "acidity": 2, "sweetness": 8, "body": 8, "bitterness": 6, "is_synthetic": True},
        {"variety": "Bourbon",       "process": "Natural", "origin_country": "Brazil",
         "altitude_masl": 1200.0, "days_since_roast": 14.0, "notes": "cacao, nuez, melaza",
         "acidity": 2, "sweetness": 8, "body": 7, "bitterness": 6, "is_synthetic": True},
        {"variety": "Mundo Novo",    "process": "Natural", "origin_country": "Brasil",
         "altitude_masl": 900.0,  "days_since_roast": 12.0, "notes": "pesado, chocolate con leche",
         "acidity": 2, "sweetness": 9, "body": 8, "bitterness": 5, "is_synthetic": True},
        # Ethiopian Washed — opposite archetype
        {"variety": "Heirloom",      "process": "Lavado / Washed", "origin_country": "Ethiopia",
         "altitude_masl": 2000.0, "days_since_roast": 14.0, "notes": "floral, jazmín, cítrico",
         "acidity": 9, "sweetness": 6, "body": 4, "bitterness": 3, "is_synthetic": True},
        {"variety": "SL28",          "process": "Lavado / Washed", "origin_country": "Kenya",
         "altitude_masl": 1900.0, "days_since_roast": 21.0, "notes": "limón, brillante, frambuesa",
         "acidity": 9, "sweetness": 5, "body": 4, "bitterness": 4, "is_synthetic": True},
        # Colombian Honey — middle-ground
        {"variety": "Caturra",       "process": "Honey", "origin_country": "Colombia",
         "altitude_masl": 1600.0, "days_since_roast": 10.0, "notes": "miel, caramelo, equilibrado",
         "acidity": 6, "sweetness": 7, "body": 6, "bitterness": 4, "is_synthetic": True},
        # Gesha Panama Washed — high acidity delicate
        {"variety": "Gesha / Geisha","process": "Lavado / Washed", "origin_country": "Panama",
         "altitude_masl": 1700.0, "days_since_roast": 21.0, "notes": "té de melocotón, delicado, floral",
         "acidity": 8, "sweetness": 7, "body": 4, "bitterness": 3, "is_synthetic": True},
    ]

    df_main = pd.DataFrame(rows)
    df_arch = pd.DataFrame(archetypes)
    # Archetypes get repeated 5× to anchor the MLP on critical domain patterns
    df_arch_repeated = pd.concat([df_arch] * 5, ignore_index=True)

    return pd.concat([df_main, df_arch_repeated], ignore_index=True)
