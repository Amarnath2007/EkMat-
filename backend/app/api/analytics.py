import os
import csv
from typing import Dict, Any, List, Set, Tuple
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.material import Material
from backend.app.models.match import CandidateMatch
from backend.app.models.common_material import CommonMaterial, CPSEMapping
from backend.app.models.cpse import CPSE
from backend.app.schemas.analytics import (
    AnalyticsSummaryResponse, CategoryMetric, CPSEMetric, GroundTruthAccuracyMetric
)

router = APIRouter()

def compute_ground_truth_metrics(db: Session) -> GroundTruthAccuracyMetric:
    """
    Computes mathematically rigorous Precision and Recall against ground-truth clusters
    from data/seed/cpse_seed.csv.
    Also validates that intentional near-misses (e.g. Gate vs Globe Valve) remain discriminated.
    """
    seed_csv_path = os.path.join(os.path.dirname(__file__), "../../../data/seed/cpse_seed.csv")
    gt_map: Dict[Tuple[str, str], str] = {} # (cpse, material_code) -> ground_truth_cluster

    if os.path.exists(seed_csv_path):
        with open(seed_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cpse = (row.get("cpse") or "").strip().upper()
                code = (row.get("material_code") or "").strip()
                gt = (row.get("ground_truth_cluster") or "").strip()
                if cpse and code and gt:
                    gt_map[(cpse, code)] = gt

    materials = db.query(Material).all()
    mat_id_to_gt = {}
    for m in materials:
        cpse_code = m.cpse.code if m.cpse else ""
        key = (cpse_code, m.original_code)
        if key in gt_map:
            mat_id_to_gt[m.id] = gt_map[key]

    # Ground truth positive pairs
    gt_clusters = {}
    for mid, gt_id in mat_id_to_gt.items():
        if gt_id not in gt_clusters:
            gt_clusters[gt_id] = []
        gt_clusters[gt_id].append(mid)

    gt_positive_pairs: Set[Tuple[int, int]] = set()
    for gt_id, mids in gt_clusters.items():
        for i in range(len(mids)):
            for j in range(i + 1, len(mids)):
                u, v = min(mids[i], mids[j]), max(mids[i], mids[j])
                gt_positive_pairs.add((u, v))

    # Predicted pairs from Candidate Matches (PENDING or APPROVED)
    matches = db.query(CandidateMatch).filter(CandidateMatch.status != "REJECTED").all()
    predicted_pairs: Set[Tuple[int, int]] = set()
    for m in matches:
        mids = m.material_ids or []
        for i in range(len(mids)):
            for j in range(i + 1, len(mids)):
                u, v = min(mids[i], mids[j]), max(mids[i], mids[j])
                predicted_pairs.add((u, v))

    true_positives = len(predicted_pairs.intersection(gt_positive_pairs))
    false_positives = len(predicted_pairs - gt_positive_pairs)
    false_negatives = len(gt_positive_pairs - predicted_pairs)

    precision = round(true_positives / len(predicted_pairs), 4) if predicted_pairs else 1.0
    recall = round(true_positives / len(gt_positive_pairs), 4) if gt_positive_pairs else 1.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    # Near-miss discrimination evaluation
    # Look for near miss cluster IDs: VLV-NM-001, BRG-NM-001, PMP-NM-001, FLG-NM-001
    near_miss_gts = [gt for gt in gt_clusters.keys() if "-NM-" in gt]
    near_misses_tested = len(near_miss_gts)
    successfully_discriminated = 0

    for nm_gt in near_miss_gts:
        nm_mids = set(gt_clusters[nm_gt])
        # Find if any pair of nm_mids was clustered with another cluster
        leaked = False
        for m in matches:
            mids = set(m.material_ids or [])
            intersection = mids.intersection(nm_mids)
            if intersection and len(mids - intersection) > 0:
                # Leaked across ground truth boundaries
                leaked = True
                break
        if not leaked:
            successfully_discriminated += 1

    disc_rate = round(successfully_discriminated / near_misses_tested, 4) if near_misses_tested else 1.0

    return GroundTruthAccuracyMetric(
        precision=precision,
        recall=recall,
        f1_score=f1,
        total_ground_truth_clusters=len(gt_clusters),
        correctly_identified_clusters=len([c for c in matches if c.status in ("APPROVED", "PENDING")]),
        near_misses_tested=near_misses_tested,
        near_misses_successfully_discriminated=successfully_discriminated,
        discrimination_rate=disc_rate,
        benchmark_note="Precision & Recall computed live against ground-truth cluster labels in synthetic dataset"
    )


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Overview dashboard KPIs and verifiable entity resolution benchmark metrics.
    """
    total_materials = db.query(Material).count()
    candidate_matches = db.query(CandidateMatch).all()
    candidate_count = len(candidate_matches)
    pending_count = sum(1 for m in candidate_matches if m.status == "PENDING")
    approved_count = sum(1 for m in candidate_matches if m.status in ("APPROVED", "EDITED_APPROVED"))
    rejected_count = sum(1 for m in candidate_matches if m.status == "REJECTED")
    common_codes_count = db.query(CommonMaterial).count()

    mapped_materials_count = db.query(Material).filter(Material.common_material_id.isnot(None)).count()
    coverage_rate = round(mapped_materials_count / total_materials, 4) if total_materials > 0 else 0.0

    # Category breakdown
    categories = ["VALVE", "BEARING", "PUMP", "FLANGE"]
    category_dist = []
    for cat in categories:
        mat_count = db.query(Material).filter(Material.category == cat).count()
        match_count = db.query(CandidateMatch).filter(CandidateMatch.suggested_common_code.ilike(f"%{cat}%")).count()
        app_count = db.query(CommonMaterial).filter(CommonMaterial.category == cat).count()
        category_dist.append(CategoryMetric(
            category=cat,
            total_materials=mat_count,
            candidate_matches=match_count,
            approved_harmonized=app_count
        ))

    # CPSE breakdown
    cpses = db.query(CPSE).all()
    cpse_dist = []
    for c in cpses:
        tot = db.query(Material).filter(Material.cpse_id == c.id).count()
        mapped = db.query(Material).filter(Material.cpse_id == c.id, Material.common_material_id.isnot(None)).count()
        cpse_dist.append(CPSEMetric(
            code=c.code,
            name=c.name,
            erp_system=c.erp_system,
            total_materials=tot,
            mapped_materials=mapped
        ))

    accuracy = compute_ground_truth_metrics(db)

    return AnalyticsSummaryResponse(
        total_materials_ingested=total_materials,
        candidate_clusters_total=candidate_count,
        pending_review_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        common_codes_generated=common_codes_count,
        cpse_coverage_rate=coverage_rate,
        category_distribution=category_dist,
        cpse_distribution=cpse_dist,
        ground_truth_accuracy=accuracy
    )
