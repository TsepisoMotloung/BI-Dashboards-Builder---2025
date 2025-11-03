import pandas as pd
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any
from fastapi import UploadFile, HTTPException
from app.core.config import settings
import uuid


class FileHandler:
    """Utility class for handling file uploads and processing"""
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file name provided")
        
        # Check file extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"File type .{file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
    
    @staticmethod
    async def save_upload_file(file: UploadFile, upload_dir: str = None) -> Tuple[str, str]:
        """Save uploaded file and return path and unique filename"""
        if upload_dir is None:
            upload_dir = settings.UPLOAD_DIR
        
        # Create upload directory if it doesn't exist
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path, unique_filename
    
    @staticmethod
    def read_file_preview(file_path: str, n_rows: int = 10) -> Tuple[pd.DataFrame, int]:
        """Read file and return preview DataFrame and total row count"""
        file_ext = file_path.split('.')[-1].lower()
        
        try:
            if file_ext == 'csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            total_rows = len(df)
            preview_df = df.head(n_rows)
            
            return preview_df, total_rows
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """Detect data types for each column"""
        type_mapping = {
            'int64': 'integer',
            'float64': 'float',
            'bool': 'boolean',
            'datetime64[ns]': 'datetime',
            'object': 'string'
        }
        
        detected_types = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            detected_types[col] = type_mapping.get(dtype, 'string')
        
        return detected_types
    
    @staticmethod
    def read_full_file(file_path: str) -> pd.DataFrame:
        """Read complete file into DataFrame"""
        file_ext = file_path.split('.')[-1].lower()
        
        try:
            if file_ext == 'csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    @staticmethod
    def delete_file(file_path: str) -> None:
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
