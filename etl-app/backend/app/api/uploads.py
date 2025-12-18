from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas import (
    UploadPreview,
    UploadRequest,
    UploadResponse,
    UploadHistoryResponse,
    RollbackRequest
)
from app.services import UploadService
from app.models import User
import json

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.get("/tables/list")
def list_existing_tables(
    current_user: User = Depends(get_current_active_user)
):
    """List all existing dynamic tables that can be appended to."""
    try:
        tables = UploadService.list_dynamic_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/preview", response_model=UploadPreview)
async def preview_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Preview uploaded file without saving to database"""
    try:
        preview = await UploadService.preview_file(file)
        return preview
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing file: {str(e)}"
        )



@router.post("/", response_model=UploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    upload_request: str = Form(...),  # JSON string
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process data file"""
    try:
        # Parse upload request JSON
        upload_data = UploadRequest.model_validate_json(upload_request)
        
        # Process upload
        upload_history = await UploadService.upload_data(
            db, file, upload_data, user_id=current_user.id
        )
        return upload_history
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )


@router.get("/", response_model=List[UploadHistoryResponse])
def list_uploads(
    model_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List upload history with optional filters"""
    uploads = UploadService.get_all_uploads(
        db, model_id=model_id, user_id=user_id, skip=skip, limit=limit
    )
    return uploads


@router.get("/{upload_id}", response_model=UploadHistoryResponse)
def get_upload(
    upload_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upload history by ID"""
    upload = UploadService.get_upload_history(db, upload_id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    return upload


@router.post("/{upload_id}/rollback", status_code=status.HTTP_200_OK)
def rollback_upload(
    upload_id: int,
    rollback_data: RollbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Rollback an upload (mark as rolled back)"""
    try:
        success = UploadService.rollback_upload(db, upload_id, rollback_data.reason)
        return {"message": "Upload rolled back successfully", "success": success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rolling back upload: {str(e)}"
        )


@router.get("/{upload_id}/logs")
def get_upload_logs(
    upload_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upload logs/metadata for an upload"""
    upload = UploadService.get_upload_history(db, upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    # Attempt to parse upload metadata as JSON
    try:
        metadata = upload.upload_metadata
        if metadata:
            import json
            parsed = json.loads(metadata)
            return parsed
        return {}
    except Exception:
        return {"metadata": upload.upload_metadata}


@router.get("/model/{model_id}/history", response_model=List[UploadHistoryResponse])
def get_model_upload_history(
    model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upload history for a specific data model"""
    uploads = UploadService.get_all_uploads(
        db, model_id=model_id, skip=skip, limit=limit
    )
    return uploads
