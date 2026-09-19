from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class CPSE(Base):
    __tablename__ = "cpse"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    erp_system = Column(String(50), default="SAP ECC")

    materials = relationship("Material", back_populates="cpse")
