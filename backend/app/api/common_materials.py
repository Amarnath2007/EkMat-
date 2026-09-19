from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.common_material import CommonMaterial, CPSEMapping
from backend.app.models.material import Material
from backend.app.schemas.common import CommonMaterialResponse, CPSEMappingDetail

router = APIRouter()

def format_common_material(cm: CommonMaterial, db: Session, include_mappings: bool = False) -> CommonMaterialResponse:
    mappings_count = db.query(CPSEMapping).filter(CPSEMapping.common_material_id == cm.id).count()
    mapping_details = []

    if include_mappings:
        maps = db.query(CPSEMapping).filter(CPSEMapping.common_material_id == cm.id).all()
        for m in maps:
            mat = m.material
            cpse = mat.cpse if mat else None
            mapping_details.append(CPSEMappingDetail(
                id=m.id,
                material_id=m.material_id,
                material_code=mat.original_code if mat else "",
                cpse_code=cpse.code if cpse else "",
                cpse_name=cpse.name if cpse else "",
                erp_system=cpse.erp_system if cpse else "SAP ECC",
                raw_description=mat.raw_description if mat else "",
                unit_of_measure=mat.unit_of_measure if mat else "NOS",
                mapped_by=m.mapped_by,
                mapped_at=m.mapped_at
            ))

    return CommonMaterialResponse(
        id=cm.id,
        common_code=cm.common_code,
        standardized_description=cm.standardized_description,
        category=cm.category,
        attributes=cm.attributes,
        created_from_match_id=cm.created_from_match_id,
        created_at=cm.created_at,
        mapped_count=mappings_count,
        mappings=mapping_details if include_mappings else None
    )


@router.get("", response_model=List[CommonMaterialResponse])
def list_common_materials(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List standardized Common National Material Master entries.
    """
    query = db.query(CommonMaterial)
    if category:
        query = query.filter(CommonMaterial.category == category.upper())
    if q:
        pat = f"%{q.strip()}%"
        query = query.filter(
            (CommonMaterial.common_code.ilike(pat)) |
            (CommonMaterial.standardized_description.ilike(pat))
        )
    records = query.order_by(CommonMaterial.created_at.desc()).all()
    return [format_common_material(r, db, include_mappings=False) for r in records]


@router.get("/{cm_id}", response_model=CommonMaterialResponse)
def get_common_material(cm_id: int, db: Session = Depends(get_db)):
    """
    Get detailed Common Material record with all mapped CPSE legacy records.
    """
    cm = db.query(CommonMaterial).filter(CommonMaterial.id == cm_id).first()
    if not cm:
        raise HTTPException(status_code=404, detail="Common material not found")
    return format_common_material(cm, db, include_mappings=True)
