from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Department, Organization, Role, User, RolePermission, UserRole

router = APIRouter(prefix="/departments", tags=["Departments"])


class DeptCreate(BaseModel):
    name: str
    organization_id: int


class DeptUpdate(BaseModel):
    name: Optional[str] = None
    organization_id: Optional[int] = None


@router.get("/", response_model=List[dict])
def list_departments(organization_id: Optional[int] = Query(None), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    q = db.query(Department)
    if organization_id is not None:
        q = q.filter(Department.organization_id == organization_id)
    deps = q.offset(skip).limit(limit).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "organization_id": d.organization_id,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
        }
        for d in deps
    ]


@router.get("/{dep_id}")
def get_department(dep_id: int, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dep_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return {
        "id": d.id,
        "name": d.name,
        "organization_id": d.organization_id,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_department(payload: DeptCreate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not found")
    d = Department(name=payload.name, organization_id=payload.organization_id)
    db.add(d)
    db.commit()
    db.refresh(d)
    return {
        "id": d.id,
        "name": d.name,
        "organization_id": d.organization_id,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


@router.put("/{dep_id}")
def update_department(dep_id: int, payload: DeptUpdate, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dep_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    if payload.name is not None:
        d.name = payload.name
    if payload.organization_id is not None:
        org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
        if not org:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not found")
        d.organization_id = payload.organization_id
    db.commit()
    db.refresh(d)
    return {
        "id": d.id,
        "name": d.name,
        "organization_id": d.organization_id,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dep_id: int, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dep_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    # Clean up dependent RolePermission and UserRole entries for roles/users in this department
    role_ids = [r.id for r in db.query(Role).filter(Role.department_id == dep_id).all()]
    if role_ids:
        db.query(RolePermission).filter(RolePermission.role_id.in_(role_ids)).delete(synchronize_session=False)
        db.query(Role).filter(Role.id.in_(role_ids)).delete(synchronize_session=False)

    # delete user roles for users in this department
    user_ids = [u.id for u in db.query(User).filter(User.department_id == dep_id).all()]
    if user_ids:
        db.query(UserRole).filter(UserRole.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)

    # delete the department itself
    db.delete(d)
    db.commit()
    return None
