import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models.cpse import CPSE
from backend.app.models.material import Material
from backend.app.models.match import CandidateMatch
from backend.app.models.common_material import CommonMaterial, CPSEMapping
from backend.app.models.audit import AuditLog
from backend.app.api.matches import approve_candidate_match, MatchApproveRequest

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Seed 2 CPSEs
    c1 = CPSE(code="BHEL", name="BHEL Corp", erp_system="SAP ECC")
    c2 = CPSE(code="ONGC", name="ONGC Corp", erp_system="SAP S/4HANA")
    db.add_all([c1, c2])
    db.commit()

    # Seed 2 equivalent materials
    m1 = Material(
        cpse_id=c1.id,
        original_code="BHEL-001",
        raw_description="GATE VALVE 6 INCH 150# CS",
        category="VALVE"
    )
    m2 = Material(
        cpse_id=c2.id,
        original_code="ONGC-001",
        raw_description="6\" CS GATE VALVE CLASS 150",
        category="VALVE"
    )
    db.add_all([m1, m2])
    db.commit()

    # Seed Candidate Match
    match = CandidateMatch(
        material_ids=[m1.id, m2.id],
        semantic_score=0.93,
        fuzzy_score=0.88,
        attribute_score=0.95,
        weighted_score=0.919,
        confidence_band="HIGH",
        status="PENDING",
        suggested_description="Standardized 6\" CS Gate Valve Class 150",
        suggested_common_code="EKMAT-VALVE-CS-6IN-001"
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    yield db
    db.close()


def test_approval_workflow_persists_state(test_db):
    """
    Test that clicking Approve on a real cluster creates CommonMaterial,
    CPSEMapping rows, updates Material rows, and records an AuditLog entry.
    """
    match = test_db.query(CandidateMatch).first()
    assert match.status == "PENDING"

    # Call approve endpoint handler
    req = MatchApproveRequest(reviewed_by="Senior Technical Reviewer")
    resp = approve_candidate_match(match_id=match.id, req=req, db=test_db)

    # 1. Assert CandidateMatch status updated
    assert resp.status == "APPROVED"
    assert resp.reviewed_by == "Senior Technical Reviewer"

    # 2. Assert CommonMaterial row exists in DB
    cm = test_db.query(CommonMaterial).filter(CommonMaterial.common_code == "EKMAT-VALVE-CS-6IN-001").first()
    assert cm is not None
    assert cm.standardized_description == "Standardized 6\" CS Gate Valve Class 150"

    # 3. Assert CPSEMapping rows exist for both materials
    mappings = test_db.query(CPSEMapping).filter(CPSEMapping.common_material_id == cm.id).all()
    assert len(mappings) == 2
    mapped_mat_ids = {m.material_id for m in mappings}
    assert mapped_mat_ids == set(match.material_ids)

    # 4. Assert Member materials have common_material_id set
    for mid in match.material_ids:
        mat = test_db.query(Material).filter(Material.id == mid).first()
        assert mat.common_material_id == cm.id

    # 5. Assert AuditLog entry recorded
    audit_entry = test_db.query(AuditLog).filter(
        AuditLog.action == "APPROVE",
        AuditLog.entity_id == match.id
    ).first()
    assert audit_entry is not None
    assert audit_entry.actor == "Senior Technical Reviewer"
    assert audit_entry.after_state["status"] == "APPROVED"
