from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CategoryMetric(BaseModel):
    category: str
    total_materials: int
    candidate_matches: int
    approved_harmonized: int

class CPSEMetric(BaseModel):
    code: str
    name: str
    erp_system: str
    total_materials: int
    mapped_materials: int

class GroundTruthAccuracyMetric(BaseModel):
    precision: float
    recall: float
    f1_score: float
    total_ground_truth_clusters: int
    correctly_identified_clusters: int
    near_misses_tested: int
    near_misses_successfully_discriminated: int
    discrimination_rate: float
    benchmark_note: str

class AnalyticsSummaryResponse(BaseModel):
    total_materials_ingested: int
    candidate_clusters_total: int
    pending_review_count: int
    approved_count: int
    rejected_count: int
    common_codes_generated: int
    cpse_coverage_rate: float
    category_distribution: List[CategoryMetric]
    cpse_distribution: List[CPSEMetric]
    ground_truth_accuracy: GroundTruthAccuracyMetric
