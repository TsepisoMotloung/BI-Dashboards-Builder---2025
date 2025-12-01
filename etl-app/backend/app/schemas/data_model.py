from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.data_model import RelationType
import json


class FieldDefinition(BaseModel):
    """Schema for individual field definition"""
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(string|integer|float|boolean|date|datetime|text)$")
    required: bool = False
    unique: bool = False
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[Any] = None


class DataModelSchema(BaseModel):
    """Schema for complete data model definition"""
    fields: List[FieldDefinition]
    primary_key: str = "id"
    indexes: List[str] = []


class DataModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, pattern="^[a-zA-Z][a-zA-Z0-9_]*$")
    schema_definition: DataModelSchema
    description: Optional[str] = None
    organization_id: Optional[int] = None
    
    model_config = ConfigDict(protected_namespaces=())


class DataModelUpdate(BaseModel):
    schema_definition: Optional[DataModelSchema] = None
    description: Optional[str] = None
    organization_id: Optional[int] = None
    
    model_config = ConfigDict(protected_namespaces=())


class DataModelResponse(BaseModel):
    id: int
    name: str
    schema_json: Dict[str, Any]
    description: Optional[str] = None
    organization_id: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class DataRelationshipCreate(BaseModel):
    source_model_id: int
    target_model_id: int
    type: RelationType
    source_field: str
    target_field: str
    config: Optional[Dict[str, Any]] = None


class DataRelationshipResponse(BaseModel):
    id: int
    source_model_id: int
    target_model_id: int
    type: RelationType
    config: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
