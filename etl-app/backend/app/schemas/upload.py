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
    # Either model_id (legacy) or target_table_name (new table-direct mode)
    model_id: Optional[int] = None
    target_table_name: Optional[str] = None  # Direct table name (e.g., "data_customers")
    
    # mapping between file column -> model field (can be empty when creating new table)
    column_mappings: List[ColumnMapping] = Field(default_factory=list)
    skip_rows: int = 0
    validate_only: bool = False

    # upload mode: create a new table or append to existing
    mode: Optional[str] = "append"  # 'create' or 'append'
    # when creating, optional target_table name (if omitted it will be auto-generated from model)
    target_table: Optional[str] = None

    # policy for extra columns present in file but not in existing table: 'discard'|'add'|'error'
    extra_columns_action: Optional[str] = "error"

    # when adding columns automatically, make them nullable by default
    add_missing_columns: Optional[bool] = False

    # user overrides for detected types, e.g. {"colA": "string", "colB": "integer"}
    column_type_overrides: Optional[Dict[str, str]] = None
    
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
    model_id: Optional[int] = None
    upload_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RollbackRequest(BaseModel):
    upload_id: int
    reason: Optional[str] = None
    # If true, attempt to revert schema changes (drop columns added by the upload)
    revert_schema: Optional[bool] = False

    model_config = ConfigDict(protected_namespaces=())
