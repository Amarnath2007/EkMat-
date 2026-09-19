import io
import csv
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.cpse import CPSE
from backend.app.models.material import Material
from backend.app.models.common_material import CommonMaterial
from backend.app.schemas.materials import (
    MaterialResponse, MaterialListResponse, CSVImportSummary, CSVImportRowError
)
from backend.app.services.preprocessing import normalize_text
from backend.app.services.attribute_extraction import extract_attributes_regex
from backend.app.services.embeddings import compute_embedding
from backend.app.services.clustering import run_entity_resolution_pipeline
from backend.app.services.audit import log_action

logger = logging.getLogger("ekmat.api.materials")
router = APIRouter()

DEFAULT_CPSE_DATA = {
    "BHEL": ("Bharat Heavy Electricals Limited", "SAP ECC"),
    "ONGC": ("Oil and Natural Gas Corporation", "SAP S/4HANA"),
    "GAIL": ("Gas Authority of India Limited", "SAP ECC"),
    "NTPC": ("National Thermal Power Corporation", "SAP S/4HANA"),
    "SAIL": ("Steel Authority of India Limited", "SAP ECC"),
}

def ensure_cpse_exists(db: Session, cpse_code: str) -> CPSE:
    cpse_code_clean = cpse_code.strip().upper()
    record = db.query(CPSE).filter(CPSE.code == cpse_code_clean).first()
    if not record:
        name, erp = DEFAULT_CPSE_DATA.get(cpse_code_clean, (f"{cpse_code_clean} Corporation", "SAP ECC"))
        record = CPSE(code=cpse_code_clean, name=name, erp_system=erp)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


@router.post("/import", response_model=CSVImportSummary)
async def import_materials_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Ingests CPSE Material Master CSV.
    Validates every row (required: cpse, material_code, description, category).
    Reports row-level validation errors.
    Rejects duplicate (cpse, material_code) with clear error.
    Computes normalized descriptions, technical attributes, and embeddings.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content = await file.read()
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    required_cols = {"cpse", "material_code", "description", "category"}
    if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
        missing = required_cols - set(reader.fieldnames or [])
        raise HTTPException(
            status_code=400,
            detail=f"CSV missing mandatory columns: {', '.join(missing)}"
        )

    accepted = 0
    rejected = 0
    rejected_rows: List[CSVImportRowError] = []
    seen_in_batch = set()

    row_num = 1
    for row in reader:
        row_num += 1
        cpse_code = (row.get("cpse") or "").strip().upper()
        mat_code = (row.get("material_code") or "").strip()
        desc = (row.get("description") or "").strip()
        spec = (row.get("specification") or "").strip()
        unit = (row.get("unit") or "NOS").strip().upper()
        cat = (row.get("category") or "").strip().upper()

        if not cpse_code:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error="CPSE identifier is required."))
            continue
        if not mat_code:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error="Material Code is required."))
            continue
        if not desc:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error="Material description is required."))
            continue
        if not cat:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error="Category is required."))
            continue

        pair_key = (cpse_code, mat_code)
        if pair_key in seen_in_batch:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error=f"Duplicate material code '{mat_code}' within this CSV file."))
            continue
        seen_in_batch.add(pair_key)

        cpse_obj = ensure_cpse_exists(db, cpse_code)

        existing = db.query(Material).filter(Material.cpse_id == cpse_obj.id, Material.original_code == mat_code).first()
        if existing:
            rejected += 1
            rejected_rows.append(CSVImportRowError(row_number=row_num, material_code=mat_code, cpse=cpse_code, error=f"Material '{mat_code}' already exists for CPSE '{cpse_code}'."))
            continue

        normalized = normalize_text(f"{desc} {spec}")
        attrs = extract_attributes_regex(desc, spec)
        emb = compute_embedding(normalized)

        material_obj = Material(
            cpse_id=cpse_obj.id,
            original_code=mat_code,
            raw_description=desc,
            raw_specification=spec,
            unit_of_measure=unit,
            category=cat,
            normalized_description=normalized,
            extracted_attributes=attrs,
            embedding=emb
        )
        db.add(material_obj)
        accepted += 1

    db.commit()

    log_action(
        db,
        action="IMPORT",
        entity_type="MATERIAL_BATCH",
        entity_id=None,
        actor="CSV_INGESTOR",
        after_state={"accepted_count": accepted, "rejected_count": rejected}
    )

    return CSVImportSummary(
        total_rows_processed=row_num - 1,
        accepted_count=accepted,
        rejected_count=rejected,
        rejected_rows=rejected_rows
    )


@router.get("", response_model=MaterialListResponse)
def list_materials(
    cpse: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None), # MAPPED | UNMAPPED
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Search and filter materials across CPSE master catalogs.
    """
    query = db.query(Material)

    if cpse:
        query = query.join(CPSE).filter(CPSE.code == cpse.upper())
    if category:
        query = query.filter(Material.category == category.upper())
    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Material.original_code.ilike(search_pattern),
                Material.raw_description.ilike(search_pattern),
                Material.raw_specification.ilike(search_pattern),
                Material.normalized_description.ilike(search_pattern)
            )
        )
    if status == "MAPPED":
        query = query.filter(Material.common_material_id.isnot(None))
    elif status == "UNMAPPED":
        query = query.filter(Material.common_material_id.is_(None))

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(Material.id.asc()).offset(offset).limit(page_size).all()

    # Load CPSE code and common_code mapping
    common_code_lookup = {}
    if any(m.common_material_id for m in records):
        cids = [m.common_material_id for m in records if m.common_material_id]
        cms = db.query(CommonMaterial).filter(CommonMaterial.id.in_(cids)).all()
        common_code_lookup = {c.id: c.common_code for c in cms}

    items = []
    for m in records:
        items.append(MaterialResponse(
            id=m.id,
            cpse_id=m.cpse_id,
            cpse_code=m.cpse.code if m.cpse else None,
            cpse_name=m.cpse.name if m.cpse else None,
            erp_system=m.cpse.erp_system if m.cpse else None,
            original_code=m.original_code,
            raw_description=m.raw_description,
            raw_specification=m.raw_specification,
            unit_of_measure=m.unit_of_measure,
            category=m.category,
            normalized_description=m.normalized_description,
            extracted_attributes=m.extracted_attributes,
            common_material_id=m.common_material_id,
            common_code=common_code_lookup.get(m.common_material_id),
            created_at=m.created_at
        ))

    total_pages = (total + page_size - 1) // page_size
    return MaterialListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.id == material_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    
    common_code = None
    if m.common_material_id:
        cm = db.query(CommonMaterial).filter(CommonMaterial.id == m.common_material_id).first()
        if cm:
            common_code = cm.common_code

    return MaterialResponse(
        id=m.id,
        cpse_id=m.cpse_id,
        cpse_code=m.cpse.code if m.cpse else None,
        cpse_name=m.cpse.name if m.cpse else None,
        erp_system=m.cpse.erp_system if m.cpse else None,
        original_code=m.original_code,
        raw_description=m.raw_description,
        raw_specification=m.raw_specification,
        unit_of_measure=m.unit_of_measure,
        category=m.category,
        normalized_description=m.normalized_description,
        extracted_attributes=m.extracted_attributes,
        common_material_id=m.common_material_id,
        common_code=common_code,
        created_at=m.created_at
    )


@router.post("/run-matching")
def trigger_matching_pipeline(db: Session = Depends(get_db)):
    """
    Triggers AI Entity Resolution Pipeline synchronously and returns summary.
    """
    result = run_entity_resolution_pipeline(db)
    return result
