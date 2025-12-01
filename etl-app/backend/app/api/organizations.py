from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Organization

router = APIRouter(prefix="/organizations", tags=["Organizations"])


class OrgCreate(BaseModel):
    name: str
    description: Optional[str] = None


class OrgUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_orgs(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    orgs = db.query(Organization).offset(skip).limit(limit).all()
    return [
        {
            "id": o.id,
            "name": o.name,
            "description": o.description,
            "created_at": o.created_at,
            "updated_at": o.updated_at,
        }
        for o in orgs
    ]


@router.get("/{org_id}")
def get_org(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_org(org_data: OrgCreate, db: Session = Depends(get_db)):
    org = Organization(
        name=org_data.name,
        description=org_data.description,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }


@router.put("/{org_id}")
def update_org(org_id: int, org_data: OrgUpdate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if org_data.name is not None:
        org.name = org_data.name
    if org_data.description is not None:
        org.description = org_data.description
    db.commit()
    db.refresh(org)
    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Deleting organization will cascade to departments -> roles/users via FK ON DELETE CASCADE
    db.delete(org)
    db.commit()
    return None
