from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class MaterialBase(BaseModel):
    original_code: str
    raw_description: str
    raw_specification: Optional[str] = None
    unit_of_measure: Optional[str] = None
    category: Optional[str] = None

class MaterialCreate(MaterialBase):
    cpse_code: str

class MaterialResponse(MaterialBase):
    id: int
    cpse_id: int
    cpse_code: Optional[str] = None
    cpse_name: Optional[str] = None
    erp_system: Optional[str] = None
    normalized_description: Optional[str] = None
    extracted_attributes: Optional[Dict[str, Any]] = None
    common_material_id: Optional[int] = None
    common_code: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MaterialListResponse(BaseModel):
    items: List[MaterialResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class CSVImportRowError(BaseModel):
    row_number: int
    material_code: Optional[str] = None
    cpse: Optional[str] = None
    error: str

class CSVImportSummary(BaseModel):
    total_rows_processed: int
    accepted_count: int
    rejected_count: int
    rejected_rows: List[CSVImportRowError]
