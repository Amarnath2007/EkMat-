from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class CommonMaterial(Base):
    __tablename__ = "common_materials"

    id = Column(Integer, primary_key=True, index=True)
    common_code = Column(String(80), unique=True, nullable=False, index=True)
    standardized_description = Column(Text, nullable=False)
    category = Column(String(60), nullable=True, index=True)
    attributes = Column(JSON, nullable=True)
    created_from_match_id = Column(Integer, ForeignKey("candidate_matches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mappings = relationship("CPSEMapping", back_populates="common_material", cascade="all, delete-orphan")


class CPSEMapping(Base):
    __tablename__ = "cpse_mappings"

    id = Column(Integer, primary_key=True, index=True)
    common_material_id = Column(Integer, ForeignKey("common_materials.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), unique=True, nullable=False, index=True)
    mapped_by = Column(String(80), nullable=True)
    mapped_at = Column(DateTime, default=datetime.utcnow)

    common_material = relationship("CommonMaterial", back_populates="mappings")
    material = relationship("Material", back_populates="mapping")
