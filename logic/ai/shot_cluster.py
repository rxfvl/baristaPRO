# logic/ai/shot_cluster.py
# Bonus — K-Means clustering of espresso extractions.
# Groups shots into 3 clusters with human-readable profile names.

from __future__ import annotations

import numpy as np
from typing import Optional

CLUSTER_FEATURES = [
    "ratio", "extraction_time", "score",
    "acidity", "sweetness", "body", "bitterness",
]

# Mapping from dominant characteristic → cluster label pair (ES / EN)
_LABEL_RULES = [
    # (feature, threshold, direction, label_es, label_en)
    ("score",      7.5, "above", "Shots Estelares",   "Star Shots"),
    ("score",      5.5, "below", "Shots en Proceso",  "Work in Progress"),
    ("bitterness", 6.5, "above", "Perfil Intenso",    "Intense Profile"),
    ("sweetness",  7.0, "above", "Perfil Dulce",      "Sweet Profile"),
    ("acidity",    7.0, "above", "Perfil Brillante",  "Bright & Acidic"),
    ("body",       7.0, "above", "Perfil Cremoso",    "Full & Creamy"),
    ("ratio",      2.5, "above", "Extracción Larga",  "Long Extraction"),
    ("ratio",      1.9, "below", "Extracción Corta",  "Short & Dense"),
]

_CLUSTER_ICONS = ["\U0001f31f", "\U0001f4a7", "\U0001f338"]


def _auto_label(averages: dict) -> tuple[str, str]:
    """Pick the most descriptive label for a cluster given its averages."""
    for feat, thresh, direction, es, en in _LABEL_RULES:
        val = averages.get(feat, 0)
        if direction == "above" and val >= thresh:
            return es, en
        if direction == "below" and val <= thresh:
            return es, en
    return "Variado / Mixed", "Varied"


def cluster_extractions(extractions: list) -> list[dict]:
    """
    Cluster a list of ExtractionLog ORM objects into groups.
    Returns a list of dicts, one per cluster, with:
        - id: int (0-based)
        - icon: str
        - label_es: str
        - label_en: str
        - count: int
        - averages: dict {feature: value}
        - extraction_ids: list[int]
    Returns [] if fewer than 6 extractions.
    """
    if len(extractions) < 6:
        return []

    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    # Build feature matrix
    rows, ids = [], []
    for ext in extractions:
        dose   = ext.dose_in or 18.0
        yield_ = ext.yield_out or 36.0
        ratio  = yield_ / dose if dose > 0 else 2.0
        rows.append([
            ratio,
            ext.extraction_time or 27,
            ext.score or 7.0,
            ext.acidity    or 5,
            ext.sweetness  or 5,
            ext.body       or 5,
            ext.bitterness or 5,
        ])
        ids.append(ext.id)

    X = np.array(rows, dtype=float)
    X_scaled = StandardScaler().fit_transform(X)

    n_clusters = min(3, len(extractions) // 2)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)

    clusters = []
    for c in range(n_clusters):
        mask = labels == c
        member_rows = X[mask]
        member_ids  = [ids[i] for i, m in enumerate(mask) if m]

        avgs = {CLUSTER_FEATURES[j]: float(np.mean(member_rows[:, j]))
                for j in range(len(CLUSTER_FEATURES))}

        label_es, label_en = _auto_label(avgs)
        clusters.append({
            "id":             c,
            "icon":           _CLUSTER_ICONS[c % len(_CLUSTER_ICONS)],
            "label_es":       label_es,
            "label_en":       label_en,
            "count":          int(np.sum(mask)),
            "averages":       {k: round(v, 1) for k, v in avgs.items()},
            "extraction_ids": member_ids,
        })

    # Sort by count descending for consistent display
    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters
