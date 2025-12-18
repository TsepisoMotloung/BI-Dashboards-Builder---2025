from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.models import UploadHistory, UploadStatus, DataModel, User
from app.schemas import UploadPreview, UploadRequest
from app.utils import FileHandler, DynamicTableManager
from fastapi import UploadFile, HTTPException
import pandas as pd
import json
from datetime import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


class UploadService:
    """Business logic for data upload and ingestion"""
    
    @staticmethod
    def list_dynamic_tables() -> List[str]:
        """List all existing dynamic tables (data_* prefix)"""
        from sqlalchemy import inspect
        inspector = inspect(DynamicTableManager.engine if hasattr(DynamicTableManager, 'engine') else __import__('app.core.database', fromlist=['engine']).engine)
        all_tables = inspector.get_table_names()
        # Filter tables that start with 'data_' (our dynamic tables naming convention)
        dynamic_tables = [t for t in all_tables if t.startswith('data_')]
        return dynamic_tables
    
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
            
            # Convert to dict and clean up any non-serializable types
            sample_data = []
            for record in preview_df.to_dict('records'):
                clean_record = {}
                for k, v in record.items():
                    # Convert numpy/pandas types to native Python types
                    if pd.isna(v):
                        clean_record[k] = None
                    elif isinstance(v, (pd.Timestamp, pd.Timedelta)):
                        clean_record[k] = str(v)
                    elif isinstance(v, (int, float, str, bool, type(None))):
                        clean_record[k] = v
                    else:
                        clean_record[k] = str(v)
                sample_data.append(clean_record)
            
            # Clean up
            FileHandler.delete_file(file_path)
            
            return UploadPreview(
                headers=list(preview_df.columns),
                sample_data=sample_data,
                total_rows=int(total_rows),
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
        
        # Determine target table: either from direct table name or from model
        table_name = None
        model_id = None
        
        if upload_request.target_table_name:
            # Direct table mode: use the provided table name
            table_name = upload_request.target_table_name
            model_id = None  # No associated model
        elif upload_request.model_id:
            # Legacy model-based mode
            data_model = db.query(DataModel).filter(DataModel.id == upload_request.model_id).first()
            if not data_model:
                raise HTTPException(status_code=404, detail="Data model not found")
            table_name = upload_request.target_table or f"data_{data_model.name.lower()}"
            model_id = upload_request.model_id
        else:
            raise HTTPException(status_code=400, detail="Either model_id or target_table_name must be provided")
        
        # Save file
        file_path, unique_filename = await FileHandler.save_upload_file(file)
        
        # Create upload history record
        try:
            upload_history = UploadHistory(
                user_id=user_id,
                model_id=model_id,
                file_name=file.filename,
                file_path=file_path,
                status=UploadStatus.PROCESSING,
                records_count=0
            )
            
            db.add(upload_history)
            db.commit()
            db.refresh(upload_history)
            logger.info(f"Created upload history record: {upload_history.id}")
        except Exception as db_err:
            logger.error(f"Failed to create upload history record: {str(db_err)}")
            raise Exception(f"Database error creating upload record: {str(db_err)}")
        
        try:
            # Read file
            df = FileHandler.read_full_file(file_path)
            print(f"DEBUG: Read file successfully, shape: {df.shape}")
            
            # Skip rows if specified
            if upload_request.skip_rows > 0:
                df = df.iloc[upload_request.skip_rows:]
            
            # Detect types from dataframe
            detected_types = FileHandler.detect_column_types(df)
            print(f"DEBUG: Detected types: {detected_types}")

            # Apply column mappings (after detection to map file cols)
            mapping_dict = {cm.file_column: cm.model_field for cm in upload_request.column_mappings}
            df = df.rename(columns=mapping_dict)

            # Replace NaN with None for proper DB nulls
            df = df.where(pd.notnull(df), None)

            # Columns present in file after mapping
            file_columns = list(df.columns)
            print(f"DEBUG: File columns: {file_columns}")

            # If mode is create => create new table from detected types
            if upload_request.mode == 'create' or not DynamicTableManager.table_exists(table_name):
                print(f"DEBUG: Creating new table: {table_name} with mode: {upload_request.mode}")
                try:
                    # Build minimal schema from detected types and any overrides
                    fields = []
                    for col in file_columns:
                        col_type = (upload_request.column_type_overrides or {}).get(col) or detected_types.get(col, 'string')
                        fields.append({
                            'name': col,
                            'type': col_type,
                            'required': False
                        })

                    schema = {'fields': fields}
                    print(f"DEBUG: Schema: {schema}")
                    DynamicTableManager.create_physical_table(table_name, schema)
                    print(f"DEBUG: Table created successfully")
                    added_columns = [c['name'] for c in fields]
                except Exception as create_err:
                    raise Exception(f"Failed to create table '{table_name}': {str(create_err)}")
            else:
                # Append mode: compare headers
                existing_columns = DynamicTableManager.get_table_columns(table_name)
                # exclude common system cols
                system_cols = {'id', 'created_at', 'updated_at', 'upload_id'}
                existing_user_cols = [c for c in existing_columns if c not in system_cols]

                missing_in_table = [c for c in file_columns if c not in existing_user_cols]
                # columns present in table but not in file
                extra_in_table = [c for c in existing_user_cols if c not in file_columns]

                added_columns = []

                if missing_in_table:
                    if upload_request.add_missing_columns:
                        # Prepare types for missing cols with overrides
                        cols_to_add = {}
                        for c in missing_in_table:
                            cols_to_add[c] = (upload_request.column_type_overrides or {}).get(c) or detected_types.get(c, 'string')

                        added_columns = DynamicTableManager.add_missing_columns(table_name, cols_to_add)
                    else:
                        # If validate_only, return metadata about diffs
                        if upload_request.validate_only:
                            upload_history.status = UploadStatus.COMPLETED
                            upload_history.records_count = 0
                            upload_history.completed_at = datetime.utcnow()
                            upload_history.upload_metadata = json.dumps({
                                'file_columns': file_columns,
                                'existing_columns': existing_user_cols,
                                'missing_in_table': missing_in_table,
                                'extra_in_table': extra_in_table,
                                'detected_types': detected_types
                            })
                            db.commit()
                            db.refresh(upload_history)
                            return upload_history

                        raise HTTPException(status_code=400, detail={
                            'message': 'Columns missing in target table',
                            'missing_columns': missing_in_table,
                            'advice': 'Set add_missing_columns=true to automatically add nullable columns, or run a validate-only preview.'
                        })

            # Convert to records
            records = df.to_dict('records')
            print(f"DEBUG: Converted to records, count: {len(records)}")

            if upload_request.validate_only:
                upload_history.status = UploadStatus.COMPLETED
                upload_history.records_count = len(records)
                upload_history.completed_at = datetime.utcnow()
                upload_history.upload_metadata = json.dumps({
                    "validated_only": True,
                    "detected_types": detected_types,
                    "added_columns": added_columns,
                    "column_mappings": [cm.model_dump() for cm in upload_request.column_mappings],
                    "skip_rows": upload_request.skip_rows
                })
                db.commit()
                db.refresh(upload_history)
                return upload_history

            # Insert data into dynamic table and tag with upload id
            try:
                print(f"DEBUG: Ensuring upload_id column in {table_name}")
                DynamicTableManager.ensure_upload_id_column(table_name)
                print(f"DEBUG: Inserting {len(records)} records")
                rows_inserted = DynamicTableManager.insert_data_batch_with_upload(table_name, records, upload_id=upload_history.id)
                print(f"DEBUG: Inserted {rows_inserted} rows")
            except Exception as insert_err:
                raise Exception(f"Failed to insert data into table '{table_name}': {str(insert_err)}")

            # Update upload history
            try:
                upload_history.status = UploadStatus.COMPLETED
                upload_history.records_count = rows_inserted
                upload_history.completed_at = datetime.utcnow()
                upload_history.upload_metadata = json.dumps({
                    "column_mappings": [cm.model_dump() for cm in upload_request.column_mappings],
                    "skip_rows": upload_request.skip_rows,
                    "added_columns": added_columns,
                    "detected_types": detected_types
                })

                db.commit()
                db.refresh(upload_history)
            except Exception as update_err:
                raise Exception(f"Failed to update upload history: {str(update_err)}")

            return upload_history
            
        except HTTPException as http_err:
            logger.error(f"HTTP Exception during upload: {http_err.detail}")
            upload_history.status = UploadStatus.FAILED
            upload_history.error_message = str(http_err.detail)
            db.commit()
            raise http_err
            
        except Exception as e:
            # Log detailed error information
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            logger.error(f"=== UPLOAD ERROR ===")
            logger.error(f"Error: {error_msg}")
            logger.error(f"Type: {type(e).__name__}")
            logger.error(f"Traceback:\n{error_trace}")
            
            # Update status to failed
            upload_history.status = UploadStatus.FAILED
            upload_history.error_message = f"{type(e).__name__}: {error_msg}"
            try:
                db.commit()
            except Exception as commit_err:
                logger.error(f"Failed to commit error status to DB: {str(commit_err)}")
            
            raise HTTPException(
                status_code=500,
                detail=f"{type(e).__name__}: {error_msg}"
            )
    
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
        
        # Attempt to delete rows in the dynamic table belonging to this upload
        data_model = db.query(DataModel).filter(DataModel.id == upload.model_id).first()
        if not data_model:
            raise HTTPException(status_code=404, detail="Associated data model not found")

        table_name = f"data_{data_model.name.lower()}"

        # Determine if caller requested schema revert by inspecting upload.upload_metadata
        # (the API route will pass revert_schema via RollbackRequest; here we expect caller to pass it)
        # For backward compatibility, default to not reverting schema.
        revert_schema = False
        # If upload_metadata includes a key 'revert_schema_requested' use it
        try:
            parsed_meta = json.loads(upload.upload_metadata) if upload.upload_metadata else {}
            revert_schema = parsed_meta.get('revert_schema_requested', False)
        except Exception:
            parsed_meta = json.loads(upload.upload_metadata) if upload.upload_metadata else {}

        try:
            deleted = DynamicTableManager.delete_data_by_upload(table_name, upload_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting uploaded rows: {str(e)}")

        upload.status = UploadStatus.ROLLED_BACK
        metadata = parsed_meta or {}
        metadata['rollback_reason'] = reason
        metadata['rolled_back_at'] = datetime.utcnow().isoformat()
        metadata['rows_deleted'] = deleted

        # If revert_schema true and metadata lists added_columns, attempt to drop them
        if revert_schema and metadata.get('added_columns'):
            try:
                dropped = DynamicTableManager.drop_columns(table_name, metadata.get('added_columns'))
                metadata['dropped_columns'] = dropped
            except Exception as e:
                metadata['dropped_columns_error'] = str(e)

        upload.upload_metadata = json.dumps(metadata)

        db.commit()

        return True
