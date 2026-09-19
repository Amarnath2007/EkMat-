from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(40), nullable=False, index=True) # IMPORT | MATCH_GENERATED | APPROVE | REJECT | EDIT_APPROVE
    entity_type = Column(String(40), nullable=True, index=True) # MATERIAL | CANDIDATE_MATCH | COMMON_MATERIAL
    entity_id = Column(Integer, nullable=True, index=True)
    actor = Column(String(80), default="SYSTEM")
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
