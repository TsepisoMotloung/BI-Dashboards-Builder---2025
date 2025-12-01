from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import User, UserStatus, Role, UserRole
from app.schemas import UserCreate, UserUpdate
from app.utils import get_password_hash, verify_password
from fastapi import HTTPException


class UserService:
    """Business logic for user management"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user and optionally attach role and organizational units"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=get_password_hash(user_data.password),
            status=UserStatus.PENDING
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Attach department and role if provided
        try:
            if getattr(user_data, 'department_id', None):
                # set user's department directly
                user.department_id = user_data.department_id

            # Attach role if provided
            if getattr(user_data, 'role_id', None):
                from app.models import UserRole
                existing = db.query(UserRole).filter(
                    UserRole.user_id == user.id,
                    UserRole.role_id == user_data.role_id
                ).first()
                if not existing:
                    db.add(UserRole(user_id=user.id, role_id=user_data.role_id))

            db.commit()
            db.refresh(user)
        except Exception:
            # if anything goes wrong attaching relationships, rollback but keep created user
            db.rollback()

        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="User account is not active")
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def serialize_user(db: Session, user: User) -> dict:
        """Return a dict representation of user including roles and organizational units"""
        # roles
        roles = [r.name for r in db.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()]
        # organizational units
        department = None
        try:
            if user.department:
                department = { 'id': user.department.id, 'name': user.department.name }
        except Exception:
            department = None

        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'status': user.status,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'roles': roles,
            'department': department
        }

    @staticmethod
    def get_all_users_enriched(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserService.serialize_user(db, u) for u in users]

    @staticmethod
    def get_user_enriched(db: Session, user_id: int) -> Optional[dict]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return UserService.serialize_user(db, user)
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    def assign_role(db: Session, user_id: int, role_id: int) -> bool:
        """Assign role to user"""
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise HTTPException(status_code=404, detail="User or Role not found")
        
        # Check if already assigned
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Role already assigned")
        
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[str]:
        """Get all roles for a user"""
        user_roles = db.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [role.name for role in user_roles]
