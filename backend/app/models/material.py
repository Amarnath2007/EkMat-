from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base, VectorType

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    cpse_id = Column(Integer, ForeignKey("cpse.id"), nullable=False, index=True)
    original_code = Column(String(60), nullable=False)
    raw_description = Column(Text, nullable=False)
    raw_specification = Column(Text, nullable=True)
    unit_of_measure = Column(String(20), nullable=True)
    category = Column(String(60), nullable=True, index=True)
    normalized_description = Column(Text, nullable=True)
    extracted_attributes = Column(JSON, nullable=True)
    embedding = Column(VectorType(384), nullable=True)
    common_material_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("cpse_id", "original_code", name="uq_materials_cpse_code"),
    )

    cpse = relationship("CPSE", back_populates="materials")
    mapping = relationship("CPSEMapping", back_populates="material", uselist=False)
