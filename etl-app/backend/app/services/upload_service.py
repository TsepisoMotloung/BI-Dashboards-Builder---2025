from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.models import UploadHistory, UploadStatus, DataModel, User
from app.schemas import UploadPreview, UploadRequest
from app.utils import FileHandler, DynamicTableManager
from fastapi import UploadFile, HTTPException
import pandas as pd
import json
from datetime import datetime


class UploadService:
    """Business logic for data upload and ingestion"""
    
    @staticmethod
    async def preview_file(file: UploadFile) -> UploadPreview:
        """Preview uploaded file without saving"""
        # Validate file
        FileHandler.validate_file(file)
        
        # Save temporarily
        file_path, _ = await FileHandler.save_upload_file(file)
        
        try:
            # Read preview
            preview_df, total_rows = FileHandler.read_file_preview(file_path, n_rows=10)
            
            # Detect types
            detected_types = FileHandler.detect_column_types(preview_df)
            
            # Convert to dict
            sample_data = preview_df.to_dict('records')
            
            # Clean up
            FileHandler.delete_file(file_path)
            
            return UploadPreview(
                headers=list(preview_df.columns),
                sample_data=sample_data,
                total_rows=total_rows,
                detected_types=detected_types
            )
        except Exception as e:
            FileHandler.delete_file(file_path)
            raise HTTPException(status_code=400, detail=f"Error previewing file: {str(e)}")
    
    @staticmethod
    async def upload_data(
        db: Session,
        file: UploadFile,
        upload_request: UploadRequest,
        user_id: Optional[int] = None
    ) -> UploadHistory:
        """Upload and process data file"""
        # Validate file
        FileHandler.validate_file(file)
        
        # Get data model
        data_model = db.query(DataModel).filter(DataModel.id == upload_request.model_id).first()
        if not data_model:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        # Save file
        file_path, unique_filename = await FileHandler.save_upload_file(file)
        
        # Create upload history record
        upload_history = UploadHistory(
            user_id=user_id,
            model_id=upload_request.model_id,
            file_name=file.filename,
            file_path=file_path,
            status=UploadStatus.PROCESSING,
            records_count=0
        )
        
        db.add(upload_history)
        db.commit()
        db.refresh(upload_history)
        
        try:
            # Read file
            df = FileHandler.read_full_file(file_path)
            
            # Skip rows if specified
            if upload_request.skip_rows > 0:
                df = df.iloc[upload_request.skip_rows:]
            
            # Apply column mappings
            mapping_dict = {cm.file_column: cm.model_field for cm in upload_request.column_mappings}
            df = df.rename(columns=mapping_dict)
            
            # Get schema
            schema = json.loads(data_model.schema_json)
            
            # Validate required fields
            required_fields = [f['name'] for f in schema['fields'] if f.get('required', False)]
            missing_fields = set(required_fields) - set(df.columns)
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Clean data
            df = df.fillna('')  # Replace NaN with empty string
            
            # Convert to records
            records = df.to_dict('records')
            
            if upload_request.validate_only:
                # Only validation, don't insert
                upload_history.status = UploadStatus.COMPLETED
                upload_history.records_count = len(records)
                upload_history.completed_at = datetime.utcnow()
                upload_history.upload_metadata = json.dumps({
                    "validated_only": True,
                    "validation_passed": True
                })
                db.commit()
                db.refresh(upload_history)
                return upload_history
            
            # Insert data into dynamic table
            table_name = f"data_{data_model.name.lower()}"
            rows_inserted = DynamicTableManager.insert_data_batch(table_name, records)
            
            # Update upload history
            upload_history.status = UploadStatus.COMPLETED
            upload_history.records_count = rows_inserted
            upload_history.completed_at = datetime.utcnow()
            upload_history.upload_metadata = json.dumps({
                "column_mappings": [cm.model_dump() for cm in upload_request.column_mappings],
                "skip_rows": upload_request.skip_rows
            })
            
            db.commit()
            db.refresh(upload_history)
            
            return upload_history
            
        except Exception as e:
            # Update status to failed
            upload_history.status = UploadStatus.FAILED
            upload_history.error_message = str(e)
            db.commit()
            
            raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")
    
    @staticmethod
    def get_upload_history(db: Session, upload_id: int) -> Optional[UploadHistory]:
        """Get upload history by ID"""
        return db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
    
    @staticmethod
    def get_all_uploads(
        db: Session,
        model_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UploadHistory]:
        """Get upload history with filters"""
        query = db.query(UploadHistory)
        
        if model_id:
            query = query.filter(UploadHistory.model_id == model_id)
        
        if user_id:
            query = query.filter(UploadHistory.user_id == user_id)
        
        return query.order_by(UploadHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def rollback_upload(db: Session, upload_id: int, reason: Optional[str] = None) -> bool:
        """Rollback an upload (mark as rolled back)"""
        upload = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
        
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        if upload.status != UploadStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Can only rollback completed uploads")
        
        # Note: Actual data deletion would require tracking which records belong to which upload
        # This would need an upload_id column in dynamic tables or timestamp-based tracking
        
        upload.status = UploadStatus.ROLLED_BACK
        metadata = json.loads(upload.upload_metadata) if upload.upload_metadata else {}
        metadata['rollback_reason'] = reason
        metadata['rolled_back_at'] = datetime.utcnow().isoformat()
        upload.upload_metadata = json.dumps(metadata)
        
        db.commit()
        
        return True
