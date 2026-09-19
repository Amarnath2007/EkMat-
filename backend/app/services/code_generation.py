import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.common_material import CommonMaterial

def clean_code_part(text: Optional[str], default: str = "GEN") -> str:
    if not text:
        return default
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    return cleaned[:10] if cleaned else default

def generate_suggested_common_code(
    category: str,
    attributes: Dict[str, Any],
    sequence_num: int = 1
) -> str:
    """
    Format: EKMAT-{CATEGORY}-{MATERIAL}-{KEY_SPEC}-{SEQUENCE}
    """
    cat_part = clean_code_part(category, "ITEM")
    
    # Material part
    mat_raw = attributes.get("material") or "GEN"
    mat_part = clean_code_part(mat_raw, "GEN")
    if "CARBON" in mat_part or "WCB" in mat_part:
        mat_part = "CS"
    elif "STAINLESS" in mat_part or "316" in mat_part or "304" in mat_part:
        mat_part = "SS"
    elif "CASTIRON" in mat_part:
        mat_part = "CI"
    elif "MILD" in mat_part:
        mat_part = "MS"

    # Key spec part
    spec_raw = attributes.get("size_mm") or attributes.get("type") or "STD"
    spec_part = clean_code_part(spec_raw, "STD")

    seq_part = f"{sequence_num:03d}"
    return f"EKMAT-{cat_part}-{mat_part}-{spec_part}-{seq_part}"


def get_next_sequence_for_category(db: Session, category: str) -> int:
    """
    Queries existing common_materials in category to obtain atomic next sequence number.
    """
    count = db.query(CommonMaterial).filter(CommonMaterial.category == category).count()
    return count + 1
