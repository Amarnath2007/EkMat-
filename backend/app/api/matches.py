from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.match import CandidateMatch
from backend.app.models.material import Material
from backend.app.models.common_material import CommonMaterial, CPSEMapping
from backend.app.schemas.matches import (
    CandidateMatchResponse, MatchApproveRequest, MatchEditApproveRequest, MatchRejectRequest
)
from backend.app.schemas.materials import MaterialResponse
from backend.app.services.audit import log_action

router = APIRouter()

def format_match_response(m: CandidateMatch, db: Session, include_members: bool = False) -> CandidateMatchResponse:
    mat_ids = m.material_ids or []
    members = []
    category = None

    if include_members or mat_ids:
        mats = db.query(Material).filter(Material.id.in_(mat_ids)).all()
        if mats:
            category = mats[0].category
        if include_members:
            for mat in mats:
                members.append(MaterialResponse(
                    id=mat.id,
                    cpse_id=mat.cpse_id,
                    cpse_code=mat.cpse.code if mat.cpse else None,
                    cpse_name=mat.cpse.name if mat.cpse else None,
                    erp_system=mat.cpse.erp_system if mat.cpse else None,
                    original_code=mat.original_code,
                    raw_description=mat.raw_description,
                    raw_specification=mat.raw_specification,
                    unit_of_measure=mat.unit_of_measure,
                    category=mat.category,
                    normalized_description=mat.normalized_description,
                    extracted_attributes=mat.extracted_attributes,
                    common_material_id=mat.common_material_id,
                    created_at=mat.created_at
                ))

    return CandidateMatchResponse(
        id=m.id,
        material_ids=mat_ids,
        semantic_score=m.semantic_score,
        fuzzy_score=m.fuzzy_score,
        attribute_score=m.attribute_score,
        weighted_score=m.weighted_score,
        confidence_band=m.confidence_band,
        status=m.status,
        suggested_description=m.suggested_description,
        suggested_common_code=m.suggested_common_code,
        category=category,
        member_count=len(mat_ids),
        members=members if include_members else None,
        created_at=m.created_at,
        reviewed_by=m.reviewed_by,
        reviewed_at=m.reviewed_at
    )


@router.get("", response_model=List[CandidateMatchResponse])
def list_candidate_matches(
    confidence_band: Optional[str] = Query(None), # HIGH | MEDIUM | LOW
    status: Optional[str] = Query(None),          # PENDING | APPROVED | REJECTED | EDITED_APPROVED
    db: Session = Depends(get_db)
):
    """
    List candidate match clusters for human validation.
    """
    query = db.query(CandidateMatch)
    if confidence_band:
        query = query.filter(CandidateMatch.confidence_band == confidence_band.upper())
    if status:
        query = query.filter(CandidateMatch.status == status.upper())

    records = query.order_by(CandidateMatch.weighted_score.desc()).all()
    return [format_match_response(r, db, include_members=False) for r in records]


@router.get("/{match_id}", response_model=CandidateMatchResponse)
def get_candidate_match(match_id: int, db: Session = Depends(get_db)):
    """
    Retrieve candidate cluster details with all constituent CPSE records and signal breakdown.
    """
    m = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Candidate match not found")
    return format_match_response(m, db, include_members=True)


@router.post("/{match_id}/approve", response_model=CandidateMatchResponse)
def approve_candidate_match(
    match_id: int,
    req: MatchApproveRequest = MatchApproveRequest(),
    db: Session = Depends(get_db)
):
    """
    Human Validation: Approve candidate cluster.
    Creates CommonMaterial record, CPSEMapping records, updates member materials,
    and appends an immutable audit log entry.
    """
    m = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Candidate match not found")

    if m.status in ("APPROVED", "EDITED_APPROVED"):
        raise HTTPException(status_code=400, detail="Match is already approved")

    before_state = {
        "status": m.status,
        "suggested_common_code": m.suggested_common_code,
        "reviewed_by": m.reviewed_by
    }

    # 1. Ensure or Create CommonMaterial
    mats = db.query(Material).filter(Material.id.in_(m.material_ids)).all()
    category = mats[0].category if mats else "GEN"

    common_code = m.suggested_common_code
    existing_cm = db.query(CommonMaterial).filter(CommonMaterial.common_code == common_code).first()
    if not existing_cm:
        existing_cm = CommonMaterial(
            common_code=common_code,
            standardized_description=m.suggested_description or "Harmonized Material Description",
            category=category,
            created_from_match_id=m.id,
            attributes=mats[0].extracted_attributes if mats else {}
        )
        db.add(existing_cm)
        db.flush()

    # 2. Create CPSE Mappings
    for mat in mats:
        mat.common_material_id = existing_cm.id
        # Check mapping
        mapping = db.query(CPSEMapping).filter(CPSEMapping.material_id == mat.id).first()
        if not mapping:
            mapping = CPSEMapping(
                common_material_id=existing_cm.id,
                material_id=mat.id,
                mapped_by=req.reviewed_by
            )
            db.add(mapping)
        else:
            mapping.common_material_id = existing_cm.id
            mapping.mapped_by = req.reviewed_by

    # 3. Update Match status
    m.status = "APPROVED"
    m.reviewed_by = req.reviewed_by
    m.reviewed_at = datetime.utcnow()

    after_state = {
        "status": m.status,
        "common_code": existing_cm.common_code,
        "common_material_id": existing_cm.id,
        "mapped_material_count": len(mats),
        "reviewed_by": m.reviewed_by
    }

    # 4. Audit Log
    log_action(
        db,
        action="APPROVE",
        entity_type="CANDIDATE_MATCH",
        entity_id=m.id,
        actor=req.reviewed_by,
        before_state=before_state,
        after_state=after_state
    )

    db.commit()
    db.refresh(m)

    return format_match_response(m, db, include_members=True)


@router.post("/{match_id}/edit-approve", response_model=CandidateMatchResponse)
def edit_and_approve_candidate_match(
    match_id: int,
    req: MatchEditApproveRequest,
    db: Session = Depends(get_db)
):
    """
    Human Validation: Edit & Approve cluster with human-corrected description or code.
    """
    m = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Candidate match not found")

    before_state = {
        "status": m.status,
        "suggested_description": m.suggested_description,
        "suggested_common_code": m.suggested_common_code
    }

    mats = db.query(Material).filter(Material.id.in_(m.material_ids)).all()
    category = mats[0].category if mats else "GEN"

    chosen_code = req.edited_common_code.strip() if req.edited_common_code else m.suggested_common_code

    existing_cm = db.query(CommonMaterial).filter(CommonMaterial.common_code == chosen_code).first()
    if not existing_cm:
        existing_cm = CommonMaterial(
            common_code=chosen_code,
            standardized_description=req.edited_description,
            category=category,
            created_from_match_id=m.id,
            attributes=req.attributes or (mats[0].extracted_attributes if mats else {})
        )
        db.add(existing_cm)
        db.flush()
    else:
        existing_cm.standardized_description = req.edited_description

    for mat in mats:
        mat.common_material_id = existing_cm.id
        mapping = db.query(CPSEMapping).filter(CPSEMapping.material_id == mat.id).first()
        if not mapping:
            mapping = CPSEMapping(
                common_material_id=existing_cm.id,
                material_id=mat.id,
                mapped_by=req.reviewed_by
            )
            db.add(mapping)
        else:
            mapping.common_material_id = existing_cm.id
            mapping.mapped_by = req.reviewed_by

    m.status = "EDITED_APPROVED"
    m.suggested_description = req.edited_description
    m.suggested_common_code = chosen_code
    m.reviewed_by = req.reviewed_by
    m.reviewed_at = datetime.utcnow()

    after_state = {
        "status": m.status,
        "common_code": chosen_code,
        "edited_description": req.edited_description,
        "reviewed_by": req.reviewed_by
    }

    log_action(
        db,
        action="EDIT_APPROVE",
        entity_type="CANDIDATE_MATCH",
        entity_id=m.id,
        actor=req.reviewed_by,
        before_state=before_state,
        after_state=after_state
    )

    db.commit()
    db.refresh(m)

    return format_match_response(m, db, include_members=True)


@router.post("/{match_id}/reject", response_model=CandidateMatchResponse)
def reject_candidate_match(
    match_id: int,
    req: MatchRejectRequest = MatchRejectRequest(),
    db: Session = Depends(get_db)
):
    """
    Human Validation: Reject candidate match.
    Marks cluster REJECTED and logs rejection reason in audit trail.
    No Common Material code is created.
    """
    m = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Candidate match not found")

    before_state = {"status": m.status, "reviewed_by": m.reviewed_by}

    m.status = "REJECTED"
    m.reviewed_by = req.reviewed_by
    m.reviewed_at = datetime.utcnow()

    after_state = {
        "status": "REJECTED",
        "reason": req.rejection_reason,
        "reviewed_by": req.reviewed_by
    }

    log_action(
        db,
        action="REJECT",
        entity_type="CANDIDATE_MATCH",
        entity_id=m.id,
        actor=req.reviewed_by,
        before_state=before_state,
        after_state=after_state
    )

    db.commit()
    db.refresh(m)

    return format_match_response(m, db, include_members=True)
