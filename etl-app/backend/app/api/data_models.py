from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas import (
    DataModelCreate,
    DataModelUpdate,
    DataModelResponse,
    DataRelationshipCreate,
    DataRelationshipResponse
)
from app.services import DataModelService
from app.models import User

router = APIRouter(prefix="/data-models", tags=["Data Models"])


@router.post("/", response_model=DataModelResponse, status_code=status.HTTP_201_CREATED)
def create_data_model(
    model_data: DataModelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new data model and corresponding database table"""
    try:
        data_model = DataModelService.create_data_model(db, model_data)
        return data_model
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating data model: {str(e)}"
        )


@router.get("/", response_model=List[DataModelResponse])
def list_data_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all data models"""
    models = DataModelService.get_all_data_models(db, skip=skip, limit=limit)
    return models


@router.get("/{model_id}", response_model=DataModelResponse)
def get_data_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get data model by ID"""
    model = DataModelService.get_data_model_by_id(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data model not found"
        )
    return model


@router.get("/name/{model_name}", response_model=DataModelResponse)
def get_data_model_by_name(
    model_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get data model by name"""
    model = DataModelService.get_data_model_by_name(db, model_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data model not found"
        )
    return model


@router.put("/{model_id}", response_model=DataModelResponse)
def update_data_model(
    model_id: int,
    model_data: DataModelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update data model schema"""
    try:
        model = DataModelService.update_data_model(db, model_id, model_data)
        return model
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating data model: {str(e)}"
        )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete data model and drop physical table"""
    try:
        DataModelService.delete_data_model(db, model_id)
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting data model: {str(e)}"
        )


@router.post("/relationships", response_model=DataRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(
    rel_data: DataRelationshipCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create relationship between data models"""
    try:
        relationship = DataModelService.create_relationship(db, rel_data)
        return relationship
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating relationship: {str(e)}"
        )


@router.get("/{model_id}/relationships")
def get_model_relationships(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all relationships for a data model"""
    relationships = DataModelService.get_model_relationships(db, model_id)
    return relationships
