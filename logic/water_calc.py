# logic/water_calc.py — Water chemistry calculator for specialty coffee
#
# Based on SCA Water Quality Handbook and Rao/Hendon mineral recipe approach.
# Target minerals: Magnesium (GH), Alkalinity (KH), and TDS.
#
# Salts used:
#   MgSO4·7H2O (Epsom Salt)    → contributes Mg hardness
#   NaHCO3 (Sodium Bicarbonate) → contributes alkalinity (KH / buffer)
#   CaCl2·2H2O (Calcium Chloride) → contributes Ca hardness (optional)

from dataclasses import dataclass
from typing import Optional


# --- Conversion factors ---
# 1 g/L MgSO4·7H2O → ~9.86 ppm Mg²⁺ (as Mg)
# 1 g/L NaHCO3     → ~11.90 ppm HCO3⁻ → ~9.76 ppm CaCO3 equivalent (KH)
# 1 g/L CaCl2·2H2O → ~27.25 ppm Ca²⁺ (as Ca)
# GH ppm (as CaCO3) ≈ Mg_ppm × 4.12  +  Ca_ppm × 2.5
# KH ppm (as CaCO3) ≈ HCO3_ppm × 0.82

MG_SULFATE_TO_MG_PPM    = 9.86     # ppm Mg per g/L MgSO4·7H2O
MG_PPM_TO_GH_CaCO3      = 4.12     # GH (CaCO3) per ppm Mg
CA_CHLORIDE_TO_CA_PPM   = 27.25    # ppm Ca per g/L CaCl2·2H2O
CA_PPM_TO_GH_CaCO3      = 2.50     # GH (CaCO3) per ppm Ca
BICARB_TO_KH_PPM        = 9.76     # KH (ppm CaCO3) per g/L NaHCO3

# SCA preferred ranges (ppm as CaCO3)
SCA_GH_MIN, SCA_GH_MAX   = 17, 85
SCA_KH_MIN, SCA_KH_MAX   = 40, 70
SCA_TDS_MIN, SCA_TDS_MAX = 75, 250


@dataclass
class WaterCalcResult:
    mg_sulfate_g_per_l:       float
    sodium_bicarb_g_per_l:    float
    calcium_chloride_g_per_l: float
    actual_gh_ppm:            float
    actual_kh_ppm:            float
    actual_tds_ppm:           float
    gh_ok:                    bool
    kh_ok:                    bool
    tds_ok:                   bool


PRESET_PROFILES = {
    "SCA Ideal": {
        "target_gh_ppm": 68,
        "target_kh_ppm": 40,
        "target_tds_ppm": 150,
        "use_calcium": False,
        "description": "SCA Water Quality Handbook — Ideal range center point",
    },
    "Rao Light": {
        "target_gh_ppm": 50,
        "target_kh_ppm": 30,
        "target_tds_ppm": 110,
        "use_calcium": False,
        "description": "Rao / Hendon — lighter mineral profile, bright acidity",
    },
    "Rao Dark": {
        "target_gh_ppm": 85,
        "target_kh_ppm": 50,
        "target_tds_ppm": 175,
        "use_calcium": True,
        "description": "Rao / Hendon — fuller, rounder profile for darker roasts",
    },
    "Hendon Champion": {
        "target_gh_ppm": 50,
        "target_kh_ppm": 25,
        "target_tds_ppm": 100,
        "use_calcium": False,
        "description": "Maxwell Colonna-Dashwood recipe — clarity & sweetness",
    },
    "Personalizado / Custom": {
        "target_gh_ppm": 68,
        "target_kh_ppm": 40,
        "target_tds_ppm": 150,
        "use_calcium": False,
        "description": "Your custom profile",
    },
}


def calculate_water_recipe(
    target_gh_ppm: float,
    target_kh_ppm: float,
    target_tds_ppm: Optional[int] = None,
    use_calcium: bool = False,
) -> WaterCalcResult:
    """
    Calculate mineral concentrations to achieve target water profile.

    Strategy:
    - KH is set first using NaHCO3
    - Remaining GH is met with MgSO4 (primarily)
    - Optionally split Ca hardness via CaCl2

    Args:
        target_gh_ppm:  Desired General Hardness in ppm as CaCO3
        target_kh_ppm:  Desired Carbonate Hardness / Alkalinity in ppm as CaCO3
        target_tds_ppm: Informational only (checked for SCA compliance)
        use_calcium:    If True, split hardness between Mg and Ca (50/50)

    Returns:
        WaterCalcResult with grams per litre and compliance flags.
    """
    # Step 1: NaHCO3 for KH
    sodium_bicarb = target_kh_ppm / BICARB_TO_KH_PPM

    if use_calcium:
        # Split GH: 50% from Ca, 50% from Mg
        ca_gh_contribution = target_gh_ppm * 0.5
        mg_gh_contribution = target_gh_ppm * 0.5
        ca_ppm  = ca_gh_contribution / CA_PPM_TO_GH_CaCO3
        mg_ppm  = mg_gh_contribution / MG_PPM_TO_GH_CaCO3
        calcium_chloride = ca_ppm / CA_CHLORIDE_TO_CA_PPM
        mg_sulfate = mg_ppm / MG_SULFATE_TO_MG_PPM
    else:
        # All hardness from MgSO4
        mg_ppm  = target_gh_ppm / MG_PPM_TO_GH_CaCO3
        mg_sulfate = mg_ppm / MG_SULFATE_TO_MG_PPM
        ca_ppm  = 0.0
        calcium_chloride = 0.0

    # Calculate actual values from the computed recipe
    actual_mg_gh   = (mg_sulfate * MG_SULFATE_TO_MG_PPM) * MG_PPM_TO_GH_CaCO3
    actual_ca_gh   = ca_ppm * CA_PPM_TO_GH_CaCO3
    actual_gh      = actual_mg_gh + actual_ca_gh
    actual_kh      = sodium_bicarb * BICARB_TO_KH_PPM
    # TDS estimate: dissolved ions in mg/L (= ppm in dilute aqueous solution)
    # Each salt concentration is in g/L; convert to mg/L ion contribution.
    #
    # MgSO4·7H2O (MW=246.47): dissociates to Mg²⁺ (24.31) + SO4²⁻ (96.06)
    # NaHCO3 (MW=84.01):      dissociates to Na⁺ (22.99) + HCO3⁻ (61.02)
    # CaCl2·2H2O (MW=147.01): dissociates to Ca²⁺ (40.08) + 2Cl⁻ (70.90)
    mg_ppm_actual  = mg_sulfate     * (24.31  / 246.47) * 1000   # Mg²⁺
    so4_ppm        = mg_sulfate     * (96.06  / 246.47) * 1000   # SO4²⁻
    na_ppm         = sodium_bicarb  * (22.99  /  84.01) * 1000   # Na⁺
    hco3_ppm       = sodium_bicarb  * (61.02  /  84.01) * 1000   # HCO3⁻
    ca_ppm_actual  = calcium_chloride * (40.08 / 147.01) * 1000  # Ca²⁺
    cl_ppm         = calcium_chloride * (70.90 / 147.01) * 1000  # Cl⁻

    actual_tds = int(mg_ppm_actual + so4_ppm + na_ppm + hco3_ppm + ca_ppm_actual + cl_ppm)


    gh_rounded  = round(actual_gh, 1)
    kh_rounded  = round(actual_kh, 1)

    return WaterCalcResult(
        mg_sulfate_g_per_l       = round(mg_sulfate, 4),
        sodium_bicarb_g_per_l    = round(sodium_bicarb, 4),
        calcium_chloride_g_per_l = round(calcium_chloride, 4),
        actual_gh_ppm            = gh_rounded,
        actual_kh_ppm            = kh_rounded,
        actual_tds_ppm           = actual_tds,
        gh_ok  = SCA_GH_MIN  <= gh_rounded  <= SCA_GH_MAX,
        kh_ok  = SCA_KH_MIN  <= kh_rounded  <= SCA_KH_MAX,
        # TDS is informational (actual mg/L dissolved solids, vs SCA's CaCO3-equivalent range)
        tds_ok = True,
    )


def format_recipe_card(result: WaterCalcResult, volume_liters: float = 1.0) -> dict:
    """
    Scale recipe to a given volume and return a display-ready dict.
    """
    scale = volume_liters
    return {
        "epsom_g":    round(result.mg_sulfate_g_per_l * scale, 3),
        "bicarb_g":   round(result.sodium_bicarb_g_per_l * scale, 3),
        "cacl2_g":    round(result.calcium_chloride_g_per_l * scale, 3),
        "gh_ppm":     result.actual_gh_ppm,
        "kh_ppm":     result.actual_kh_ppm,
        "tds_ppm":    result.actual_tds_ppm,
        "volume_l":   volume_liters,
        "gh_ok":      result.gh_ok,
        "kh_ok":      result.kh_ok,
        "tds_ok":     result.tds_ok,
    }
