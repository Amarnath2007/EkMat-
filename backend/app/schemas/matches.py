from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.materials import MaterialResponse

class MatchScoreBreakdown(BaseModel):
    semantic_score: float = Field(..., description="Cosine similarity of SBERT embeddings (50% weight)")
    fuzzy_score: float = Field(..., description="RapidFuzz lexical token similarity (30% weight)")
    attribute_score: float = Field(..., description="Technical attribute match score (20% weight)")
    weighted_score: float = Field(..., description="0.50*semantic + 0.30*fuzzy + 0.20*attribute")
    confidence_band: str = Field(..., description="HIGH (>0.9) | MEDIUM (0.6-0.9) | LOW (<0.6)")

class CandidateMatchResponse(BaseModel):
    id: int
    material_ids: List[int]
    semantic_score: Optional[float] = None
    fuzzy_score: Optional[float] = None
    attribute_score: Optional[float] = None
    weighted_score: float
    confidence_band: str
    status: str
    suggested_description: Optional[str] = None
    suggested_common_code: Optional[str] = None
    category: Optional[str] = None
    member_count: int = 0
    members: Optional[List[MaterialResponse]] = None
    created_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MatchApproveRequest(BaseModel):
    reviewed_by: Optional[str] = "Govt Evaluator / Lead Data Steward"

class MatchEditApproveRequest(BaseModel):
    reviewed_by: Optional[str] = "Govt Evaluator / Lead Data Steward"
    edited_description: str
    edited_common_code: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class MatchRejectRequest(BaseModel):
    reviewed_by: Optional[str] = "Govt Evaluator / Lead Data Steward"
    rejection_reason: Optional[str] = "Distinct materials / Specifications do not match"
