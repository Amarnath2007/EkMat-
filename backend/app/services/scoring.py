from typing import Dict, Any, Tuple
from backend.app.core.config import settings

def calculate_attribute_score(attr1: Dict[str, Any], attr2: Dict[str, Any]) -> float:
    """
    Computes attribute compatibility score in range [0.0, 1.0].
    Critically discriminates intentional near-misses:
    If equipment type or size strictly conflict, returns 0.0.
    """
    if not attr1 or not attr2:
        return 0.50 # Neutral score when attributes are missing

    # 1. Critical Type Conflict Check (e.g. GATE VALVE vs GLOBE VALVE)
    type1 = (attr1.get("type") or "").strip().upper()
    type2 = (attr2.get("type") or "").strip().upper()
    if type1 and type2 and type1 != type2:
        # Genuinely different equipment types must not merge!
        return 0.0

    # 2. Size Conflict Check (e.g. 6" vs 4", 150MM vs 50MM)
    size1 = (attr1.get("size_mm") or "").strip().upper()
    size2 = (attr2.get("size_mm") or "").strip().upper()
    if size1 and size2 and size1 != size2:
        return 0.0

    score = 0.0
    weights_total = 0.0

    # Field weights
    fields = [
        ("type", 0.35),
        ("size_mm", 0.30),
        ("pressure_class", 0.15),
        ("material", 0.15),
        ("standard", 0.05),
    ]

    for field, weight in fields:
        val1 = (attr1.get(field) or "").strip().upper()
        val2 = (attr2.get(field) or "").strip().upper()

        if val1 and val2:
            weights_total += weight
            if val1 == val2:
                score += weight
            elif val1 in val2 or val2 in val1:
                score += weight * 0.85
            else:
                # Value mismatch on field
                pass
        elif val1 or val2:
            weights_total += weight * 0.5
            score += weight * 0.35

    if weights_total == 0:
        return 0.50

    return round(score / weights_total, 4)


def compute_weighted_score(
    semantic_score: float,
    fuzzy_score: float,
    attribute_score: float,
    type_conflict: bool = False,
    size_conflict: bool = False
) -> Tuple[float, str]:
    """
    Computes weighted multi-signal similarity score:
      weighted_score = 0.50 * semantic + 0.30 * fuzzy + 0.20 * attribute

    If there is a strict conflict in equipment type or size (intentional near-misses
    like Gate vs Globe Valve, or different sizes), the score is penalized so that
    it strictly routes to LOW (<0.60), guaranteeing discrimination.

    Applies confidence routing:
      > 0.90 -> HIGH (suggested for approval)
      0.60 - 0.90 -> MEDIUM (manual review)
      < 0.60 -> LOW (distinct, non-candidate)
    """
    raw_weighted = (
        settings.WEIGHT_SEMANTIC * semantic_score +
        settings.WEIGHT_FUZZY * fuzzy_score +
        settings.WEIGHT_ATTRIBUTE * attribute_score
    )

    if type_conflict or size_conflict or attribute_score == 0.0:
        # Severe penalty for near-miss discrimination: cap below LOW threshold
        weighted = min(round(float(raw_weighted * 0.5), 4), 0.48)
    else:
        weighted = round(float(raw_weighted), 4)

    if weighted > settings.THRESHOLD_HIGH:
        band = "HIGH"
    elif weighted >= settings.THRESHOLD_MEDIUM:
        band = "MEDIUM"
    else:
        band = "LOW"

    return weighted, band
