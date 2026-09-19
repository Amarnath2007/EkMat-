from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.materials import MaterialResponse

class CPSEMappingDetail(BaseModel):
    id: int
    material_id: int
    material_code: str
    cpse_code: str
    cpse_name: str
    erp_system: str
    raw_description: str
    unit_of_measure: Optional[str] = None
    mapped_by: Optional[str] = None
    mapped_at: Optional[datetime] = None

class CommonMaterialResponse(BaseModel):
    id: int
    common_code: str
    standardized_description: str
    category: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    created_from_match_id: Optional[int] = None
    created_at: Optional[datetime] = None
    mapped_count: int = 0
    mappings: Optional[List[CPSEMappingDetail]] = None

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    actor: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
