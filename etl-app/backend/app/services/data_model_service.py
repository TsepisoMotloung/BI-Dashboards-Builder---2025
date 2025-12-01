from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.models import DataModel, DataRelationship
from app.schemas import DataModelCreate, DataModelUpdate, DataRelationshipCreate
from app.utils import DynamicTableManager
from fastapi import HTTPException
import json


class DataModelService:
    """Business logic for data model management"""
    
    @staticmethod
    def create_data_model(db: Session, model_data: DataModelCreate) -> DataModel:
        """Create new data model and corresponding database table"""
        # Check if model name already exists
        existing = db.query(DataModel).filter(DataModel.name == model_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Data model with this name already exists")
        
        # Validate table name format
        table_name = f"data_{model_data.name.lower()}"
        
        # Check if physical table already exists
        if DynamicTableManager.table_exists(table_name):
            raise HTTPException(status_code=400, detail="Table already exists in database")
        
        # Convert schema to JSON
        schema_dict = model_data.schema_definition.model_dump()
        schema_json = json.dumps(schema_dict)
        
        # Create data model record
        data_model = DataModel(
            name=model_data.name,
            schema_json=schema_json,
            description=model_data.description,
            organization_id=model_data.organization_id,
            version=1
        )
        
        db.add(data_model)
        db.flush()
        
        try:
            # Create physical table
            DynamicTableManager.create_physical_table(table_name, schema_dict)
            db.commit()
            db.refresh(data_model)
            
            return data_model
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating table: {str(e)}")
    
    @staticmethod
    def get_data_model_by_id(db: Session, model_id: int) -> Optional[DataModel]:
        """Get data model by ID"""
        return db.query(DataModel).filter(DataModel.id == model_id).first()
    
    @staticmethod
    def get_data_model_by_name(db: Session, name: str) -> Optional[DataModel]:
        """Get data model by name"""
        return db.query(DataModel).filter(DataModel.name == name).first()
    
    @staticmethod
    def get_all_data_models(db: Session, skip: int = 0, limit: int = 100) -> List[DataModel]:
        """Get all data models with pagination"""
        return db.query(DataModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_data_model(db: Session, model_id: int, model_data: DataModelUpdate) -> DataModel:
        """Update data model schema (creates new version)"""
        data_model = db.query(DataModel).filter(DataModel.id == model_id).first()
        
        if not data_model:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        if model_data.schema_definition:
            schema_dict = model_data.schema_definition.model_dump()
            data_model.schema_json = json.dumps(schema_dict)
            data_model.version += 1
        
        if model_data.description is not None:
            data_model.description = model_data.description
        
        if model_data.organization_id is not None:
            data_model.organization_id = model_data.organization_id
        
        db.commit()
        db.refresh(data_model)
        
        return data_model
    
    @staticmethod
    def delete_data_model(db: Session, model_id: int) -> bool:
        """Delete data model and drop physical table"""
        data_model = db.query(DataModel).filter(DataModel.id == model_id).first()
        
        if not data_model:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        table_name = f"data_{data_model.name.lower()}"
        
        try:
            # Drop physical table
            if DynamicTableManager.table_exists(table_name):
                DynamicTableManager.drop_table(table_name)
            
            # Delete model record
            db.delete(data_model)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")
    
    @staticmethod
    def create_relationship(db: Session, rel_data: DataRelationshipCreate) -> DataRelationship:
        """Create relationship between data models"""
        # Verify both models exist
        source = db.query(DataModel).filter(DataModel.id == rel_data.source_model_id).first()
        target = db.query(DataModel).filter(DataModel.id == rel_data.target_model_id).first()
        
        if not source or not target:
            raise HTTPException(status_code=404, detail="Source or target model not found")
        
        # Create config with field mappings
        config = {
            "source_field": rel_data.source_field,
            "target_field": rel_data.target_field
        }
        if rel_data.config:
            config.update(rel_data.config)
        
        relationship = DataRelationship(
            source_model_id=rel_data.source_model_id,
            target_model_id=rel_data.target_model_id,
            type=rel_data.type,
            config=json.dumps(config)
        )
        
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        
        return relationship
    
    @staticmethod
    def get_model_relationships(db: Session, model_id: int) -> Dict[str, List[DataRelationship]]:
        """Get all relationships for a model"""
        source_rels = db.query(DataRelationship).filter(
            DataRelationship.source_model_id == model_id
        ).all()
        
        target_rels = db.query(DataRelationship).filter(
            DataRelationship.target_model_id == model_id
        ).all()
        
        return {
            "outgoing": source_rels,
            "incoming": target_rels
        }
