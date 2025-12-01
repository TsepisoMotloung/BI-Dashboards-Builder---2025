from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserStatus


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    # Optional associations by id (frontend will supply via dropdowns)
    organization_id: int | None = None
    department_id: int | None = None
    role_id: int | None = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    id: int
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    roles: list[str] = []
    department: dict | None = None  # {id, name}

    model_config = ConfigDict(from_attributes=True)


class UserWithRoles(UserResponse):
    # kept for compatibility; inherits roles and organizational_units
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
