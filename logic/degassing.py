# logic/degassing.py — Degassing and rest-day calculations

from datetime import date
from typing import Tuple


PROCESS_REST_DEFAULTS = {
    "Lavado":      (7, 14),
    "Washed":      (7, 14),
    "Natural":     (10, 21),
    "Honey":       (8, 18),
    "Anaeróbico":  (10, 21),
    "Anaerobic":   (10, 21),
    "Carbonic":    (10, 21),
    "Experimental":(10, 28),
}

PREP_METHOD_REST_DEFAULTS = {
    "Espresso": (7, 14),
    "Cold Brew": (10, 14),
    "Chemex": (5, 10),
    "Goteo Eléctrico": (5, 10),
    "Moka / Aeropress": (5, 10),
    "Sifón": (5, 10),
    "Café Turco": (5, 7),
    "Pour Over / V60": (3, 7),
    "Prensa Francesa": (3, 5),
}

DEFAULT_REST = (7, 14)  # Espresso default



def get_rest_window(process: str) -> Tuple[int, int]:
    """Return (min_days, max_days) rest window for a given process."""
    if not process:
        return DEFAULT_REST
    for key, window in PROCESS_REST_DEFAULTS.items():
        if key.lower() in process.lower():
            return window
    return DEFAULT_REST


def days_since_roast(roast_date: date) -> int:
    """Return how many days have passed since roast date."""
    return (date.today() - roast_date).days


def degassing_info(roast_date: date, rest_min: int, rest_max: int) -> dict:
    """
    Returns a dict with:
      - days_rested: int
      - status: 'resting' | 'peak' | 'declining' | 'stale'
      - progress: float 0.0–1.0 (toward peak window start)
      - days_to_peak: int (negative if already past)
      - peak_start: date
      - peak_end: date
    """
    from datetime import timedelta

    days = days_since_roast(roast_date)
    peak_start = roast_date + timedelta(days=rest_min)
    peak_end   = roast_date + timedelta(days=rest_max)

    if days < rest_min:
        status = "resting"
        progress = days / rest_min if rest_min else 0
    elif days <= rest_max:
        status = "peak"
        progress = 1.0
    elif days <= rest_max + 14:
        status = "declining"
        progress = 1.0
    else:
        status = "stale"
        progress = 1.0

    return {
        "days_rested":  days,
        "status":       status,
        "progress":     min(progress, 1.0),
        "days_to_peak": rest_min - days,
        "peak_start":   peak_start,
        "peak_end":     peak_end,
    }


STATUS_COLORS = {
    "resting":   "#5B9BD5",   # blue — still resting
    "peak":      "#4CAF6E",   # green — ready!
    "declining": "#E8A838",   # amber — use soon
    "stale":     "#7A7570",   # grey — past prime
    "unknown":   "#7A7570",
}

STATUS_LABELS = {
    "resting":   "Reposando / Resting",
    "peak":      "¡Listo! / Peak",
    "declining": "Usando / Use Soon",
    "stale":     "Pasado / Stale",
    "unknown":   "Desconocido / Unknown",
}
