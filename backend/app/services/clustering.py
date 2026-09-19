import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session

from backend.app.models.material import Material
from backend.app.models.match import CandidateMatch
from backend.app.models.cpse import CPSE
from backend.app.services.embeddings import cosine_similarity
from backend.app.services.fuzzy_match import calculate_fuzzy_score
from backend.app.services.scoring import calculate_attribute_score, compute_weighted_score
from backend.app.services.code_generation import generate_suggested_common_code, get_next_sequence_for_category
from backend.app.services.audit import log_action

logger = logging.getLogger("ekmat.clustering")


def are_materials_compatible(m1: Material, m2: Material) -> bool:
    """
    Ensures two materials do NOT have conflicting primary equipment types or sizes.
    E.g. Gate Valve vs Globe Valve must NEVER merge.
    """
    a1 = m1.extracted_attributes or {}
    a2 = m2.extracted_attributes or {}

    t1 = (a1.get("type") or "").strip().upper()
    t2 = (a2.get("type") or "").strip().upper()
    if t1 and t2 and t1 != t2:
        return False

    s1 = (a1.get("size_mm") or "").strip().upper()
    s2 = (a2.get("size_mm") or "").strip().upper()
    if s1 and s2 and s1 != s2:
        return False

    return True


def run_entity_resolution_pipeline(db: Session) -> Dict[str, Any]:
    """
    Executes the multi-stage matching pipeline:
    1. Fetches all unmapped materials from database.
    2. Blocks by category.
    3. Computes multi-signal scores (Semantic 50%, Fuzzy 30%, Attribute 20%).
    4. Routes by confidence (>0.9 HIGH, 0.6-0.9 MEDIUM, <0.6 LOW).
    5. Forms candidate match clusters and persists to candidate_matches table.
    6. Logs audit trail.
    """
    materials = db.query(Material).all()
    if not materials:
        return {"status": "empty", "message": "No materials available for matching", "clusters_created": 0}

    # 1. Blocking by category
    blocks = defaultdict(list)
    for mat in materials:
        cat = mat.category or "MISC"
        blocks[cat].append(mat)

    total_comparisons = 0
    candidate_edges = []
    pair_scores = {}

    for cat, mat_list in blocks.items():
        n = len(mat_list)
        for i in range(n):
            for j in range(i + 1, n):
                m1 = mat_list[i]
                m2 = mat_list[j]
                if m1.cpse_id == m2.cpse_id and m1.original_code == m2.original_code:
                    continue

                total_comparisons += 1

                # Check attribute compatibility first
                compatible = are_materials_compatible(m1, m2)
                if not compatible:
                    continue

                # Signal 1: SBERT Cosine Similarity (50%)
                sem_score = cosine_similarity(m1.embedding, m2.embedding)

                # Signal 2: RapidFuzz Lexical Similarity (30%)
                fuz_score = calculate_fuzzy_score(m1.normalized_description, m2.normalized_description)

                # Signal 3: Technical Attribute Compatibility (20%)
                attr_score = calculate_attribute_score(m1.extracted_attributes, m2.extracted_attributes)

                # Multi-Signal Weighted Formula
                weighted, band = compute_weighted_score(sem_score, fuz_score, attr_score)

                # Routing: candidate edge only if HIGH or MEDIUM (score >= 0.60)
                if band in ("HIGH", "MEDIUM") and weighted >= 0.65:
                    candidate_edges.append((m1.id, m2.id))
                    pair_scores[(m1.id, m2.id)] = (sem_score, fuz_score, attr_score, weighted, band)

    # 2. Consistent Clustering (no transitive contamination across incompatible types)
    adj = defaultdict(set)
    for u, v in candidate_edges:
        adj[u].add(v)
        adj[v].add(u)

    mat_lookup = {m.id: m for m in materials}
    visited = set()
    clusters = []

    for node in list(adj.keys()):
        if node not in visited:
            component = [node]
            visited.add(node)
            queue = [node]

            while queue:
                curr = queue.pop(0)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        # Check compatibility with all members in component
                        candidate_mat = mat_lookup[neighbor]
                        can_add = all(are_materials_compatible(candidate_mat, mat_lookup[m]) for m in component)
                        if can_add:
                            visited.add(neighbor)
                            component.append(neighbor)
                            queue.append(neighbor)

            if len(component) >= 2:
                clusters.append(component)

    # 3. Persist Candidate Matches to DB
    # Clear previous PENDING matches
    db.query(CandidateMatch).filter(CandidateMatch.status == "PENDING").delete()
    db.commit()

    created_count = 0
    for comp in clusters:
        comp_mats = [mat_lookup[mid] for mid in comp if mid in mat_lookup]
        if not comp_mats:
            continue

        cat = comp_mats[0].category or "GEN"

        sem_list, fuz_list, attr_list, wt_list = [], [], [], []
        for i in range(len(comp)):
            for j in range(i + 1, len(comp)):
                u, v = comp[i], comp[j]
                pair_key = (u, v) if (u, v) in pair_scores else (v, u)
                if pair_key in pair_scores:
                    s, f, a, w, _ = pair_scores[pair_key]
                    sem_list.append(s)
                    fuz_list.append(f)
                    attr_list.append(a)
                    wt_list.append(w)

        avg_sem = round(sum(sem_list) / len(sem_list), 3) if sem_list else 0.88
        avg_fuz = round(sum(fuz_list) / len(fuz_list), 3) if fuz_list else 0.82
        avg_attr = round(sum(attr_list) / len(attr_list), 3) if attr_list else 0.90
        avg_weighted, band = compute_weighted_score(avg_sem, avg_fuz, avg_attr)

        suggested_desc = max(
            (m.normalized_description or m.raw_description for m in comp_mats),
            key=len
        )

        merged_attrs = {}
        for m in comp_mats:
            if m.extracted_attributes:
                for k, v in m.extracted_attributes.items():
                    if v and not merged_attrs.get(k):
                        merged_attrs[k] = v

        seq = get_next_sequence_for_category(db, cat) + created_count
        suggested_code = generate_suggested_common_code(cat, merged_attrs, seq)

        match_record = CandidateMatch(
            material_ids=comp,
            semantic_score=avg_sem,
            fuzzy_score=avg_fuz,
            attribute_score=avg_attr,
            weighted_score=avg_weighted,
            confidence_band=band,
            status="PENDING",
            suggested_description=suggested_desc,
            suggested_common_code=suggested_code
        )
        db.add(match_record)
        db.flush()

        log_action(
            db,
            action="MATCH_GENERATED",
            entity_type="CANDIDATE_MATCH",
            entity_id=match_record.id,
            actor="AI_ENGINE",
            after_state={
                "material_ids": comp,
                "weighted_score": avg_weighted,
                "confidence_band": band,
                "suggested_code": suggested_code
            }
        )
        created_count += 1

    db.commit()

    return {
        "status": "success",
        "total_materials": len(materials),
        "total_comparisons": total_comparisons,
        "clusters_created": created_count,
        "high_confidence_count": sum(1 for c in db.query(CandidateMatch).filter(CandidateMatch.confidence_band == "HIGH", CandidateMatch.status == "PENDING").all()),
        "medium_confidence_count": sum(1 for c in db.query(CandidateMatch).filter(CandidateMatch.confidence_band == "MEDIUM", CandidateMatch.status == "PENDING").all())
    }
