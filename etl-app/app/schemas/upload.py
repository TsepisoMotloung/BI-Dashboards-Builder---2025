from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.upload import UploadStatus


class ColumnMapping(BaseModel):
    """Mapping between file column and data model field"""
    file_column: str
    model_field: str
    transform: Optional[str] = None  # e.g., "uppercase", "trim", "date_format"
    
    model_config = ConfigDict(protected_namespaces=())


class UploadPreview(BaseModel):
    """Preview data before upload"""
    headers: List[str]
    sample_data: List[Dict[str, Any]]
    total_rows: int
    detected_types: Dict[str, str]


class UploadRequest(BaseModel):
    model_id: int
    column_mappings: List[ColumnMapping]
    skip_rows: int = 0
    validate_only: bool = False
    
    model_config = ConfigDict(protected_namespaces=())


class UploadResponse(BaseModel):
    id: int
    file_name: str
    status: UploadStatus
    records_count: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UploadHistoryResponse(UploadResponse):
    user_id: Optional[int] = None
    model_id: int
    upload_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RollbackRequest(BaseModel):
    upload_id: int
    reason: Optional[str] = None
