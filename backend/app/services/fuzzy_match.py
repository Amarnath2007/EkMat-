from rapidfuzz import fuzz

def calculate_fuzzy_score(text1: str, text2: str) -> float:
    """
    Computes lexical similarity using RapidFuzz.
    Combines token_sort_ratio (40%) and token_set_ratio (60%) to handle
    word reordering and extra descriptor tokens effectively.
    Returns float in range [0.0, 1.0].
    """
    if not text1 or not text2:
        return 0.0

    t1 = text1.lower().strip()
    t2 = text2.lower().strip()

    if t1 == t2:
        return 1.0

    sort_ratio = fuzz.token_sort_ratio(t1, t2) / 100.0
    set_ratio = fuzz.token_set_ratio(t1, t2) / 100.0

    # Token set ratio gives robustness to phrasing length differences,
    # token sort ratio ensures token multiset alignment.
    score = 0.40 * sort_ratio + 0.60 * set_ratio
    return round(float(score), 4)
