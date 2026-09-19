import os
import csv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.cpse import CPSE
from backend.app.models.material import Material
from backend.app.models.match import CandidateMatch
from backend.app.services.preprocessing import normalize_text
from backend.app.services.attribute_extraction import extract_attributes_regex
from backend.app.services.embeddings import compute_embedding
from backend.app.services.clustering import run_entity_resolution_pipeline
from backend.app.api.analytics import compute_ground_truth_metrics

@pytest.fixture(scope="module")
def seeded_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    seed_csv = os.path.join(os.path.dirname(__file__), "../../data/seed/cpse_seed.csv")
    assert os.path.exists(seed_csv), "cpse_seed.csv must exist"

    cpse_map = {}
    with open(seed_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cpse_code = (row.get("cpse") or "").strip().upper()
            if cpse_code not in cpse_map:
                c = CPSE(code=cpse_code, name=f"{cpse_code} Corp", erp_system="SAP ECC")
                db.add(c)
                db.flush()
                cpse_map[cpse_code] = c.id

            mat_code = (row.get("material_code") or "").strip()
            desc = (row.get("description") or "").strip()
            spec = (row.get("specification") or "").strip()
            unit = (row.get("unit") or "NOS").strip().upper()
            cat = (row.get("category") or "GEN").strip().upper()

            norm = normalize_text(f"{desc} {spec}")
            attrs = extract_attributes_regex(desc, spec)
            emb = compute_embedding(norm)

            m = Material(
                cpse_id=cpse_map[cpse_code],
                original_code=mat_code,
                raw_description=desc,
                raw_specification=spec,
                unit_of_measure=unit,
                category=cat,
                normalized_description=norm,
                extracted_attributes=attrs,
                embedding=emb
            )
            db.add(m)

    db.commit()
    # Run the entity resolution matching engine
    run_entity_resolution_pipeline(db)

    yield db
    db.close()


def test_ground_truth_precision_and_recall(seeded_db):
    """
    Computes real, defensible precision and recall against ground truth clusters.
    Asserts precision >= 0.85 and recall >= 0.80.
    """
    metrics = compute_ground_truth_metrics(seeded_db)
    print(f"\n[BENCHMARK RESULTS] Precision: {metrics.precision:.2%}, Recall: {metrics.recall:.2%}, F1: {metrics.f1_score:.2%}")
    print(f"[DISCRIMINATION] Rate: {metrics.discrimination_rate:.2%} across {metrics.near_misses_tested} deliberate near-misses.")

    assert metrics.precision >= 0.85, f"Precision {metrics.precision} below 0.85 threshold"
    assert metrics.recall >= 0.80, f"Recall {metrics.recall} below 0.80 threshold"
    assert metrics.discrimination_rate == 1.0, "All deliberate near-misses must be discriminated!"


def test_gate_vs_globe_valve_not_merged(seeded_db):
    """
    Crucial evaluation test:
    Verify that 6" Carbon Steel Gate Valve and 6" Carbon Steel Globe Valve
    are NOT merged into the same candidate match cluster!
    """
    matches = seeded_db.query(CandidateMatch).all()
    for m in matches:
        mats = seeded_db.query(Material).filter(Material.id.in_(m.material_ids)).all()
        types = set()
        for mat in mats:
            if mat.extracted_attributes and mat.extracted_attributes.get("type"):
                types.add(mat.extracted_attributes["type"])
        assert not ("GATE VALVE" in types and "GLOBE VALVE" in types), (
            f"Cluster {m.id} improperly merged Gate Valve and Globe Valve!"
        )
