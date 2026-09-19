from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from backend.app.core.database import Base

class CandidateMatch(Base):
    __tablename__ = "candidate_matches"

    id = Column(Integer, primary_key=True, index=True)
    material_ids = Column(JSON, nullable=False) # list of material ids
    semantic_score = Column(Float, nullable=True)
    fuzzy_score = Column(Float, nullable=True)
    attribute_score = Column(Float, nullable=True)
    weighted_score = Column(Float, nullable=False)
    confidence_band = Column(String(10), nullable=False) # HIGH | MEDIUM | LOW
    status = Column(String(20), default="PENDING", index=True) # PENDING | APPROVED | REJECTED | EDITED_APPROVED
    suggested_description = Column(Text, nullable=True)
    suggested_common_code = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String(80), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
