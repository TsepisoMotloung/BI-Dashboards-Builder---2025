from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models import Role
from pydantic import BaseModel

router = APIRouter(prefix="/roles", tags=["Roles"])


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    is_system_role: bool | None = False
    department_id: int | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_system_role: bool | None = None
    department_id: int | None = None


@router.get("/", response_model=List[dict])
def list_roles(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    roles = db.query(Role).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_system_role": r.is_system_role,
            "department_id": r.department_id,
            "department_name": r.department.name if r.department else None,
            "organization_id": r.department.organization.id if r.department and r.department.organization else None,
            "organization_name": r.department.organization.name if r.department and r.department.organization else None,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in roles
    ]


@router.get("/{role_id}")
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_system_role": role.is_system_role,
        "department_id": role.department_id,
        "department_name": role.department.name if role.department else None,
        "organization_id": role.department.organization.id if role.department and role.department.organization else None,
        "organization_name": role.department.organization.name if role.department and role.department.organization else None,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    role = Role(
        name=role_data.name,
        description=role_data.description,
        is_system_role=role_data.is_system_role,
        department_id=role_data.department_id
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_system_role": role.is_system_role,
        "department_id": role.department_id,
        "department_name": role.department.name if role.department else None,
        "organization_id": role.department.organization.id if role.department and role.department.organization else None,
        "organization_name": role.department.organization.name if role.department and role.department.organization else None,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


@router.put("/{role_id}")
def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    update_data = role_data.model_dump(exclude_unset=True) if hasattr(role_data, 'model_dump') else role_data.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(role, k, v)
    db.commit()
    db.refresh(role)
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_system_role": role.is_system_role,
        "department_id": role.department_id,
        "department_name": role.department.name if role.department else None,
        "organization_id": role.department.organization.id if role.department and role.department.organization else None,
        "organization_name": role.department.organization.name if role.department and role.department.organization else None,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    db.delete(role)
    db.commit()
    return None
