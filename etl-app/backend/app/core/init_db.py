from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import Role, Permission, RolePermission, User, UserRole
from app.models.user import UserStatus
from app.utils import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def init_roles_and_permissions(db: Session):
    """Initialize default roles and permissions"""
    logger.info("Initializing roles and permissions...")
    
    # Define permissions
    permissions_data = [
        # User permissions
        {"resource": "users", "action": "view", "description": "View users"},
        {"resource": "users", "action": "create", "description": "Create users"},
        {"resource": "users", "action": "edit", "description": "Edit users"},
        {"resource": "users", "action": "delete", "description": "Delete users"},
        
        # Data model permissions
        {"resource": "data_models", "action": "view", "description": "View data models"},
        {"resource": "data_models", "action": "create", "description": "Create data models"},
        {"resource": "data_models", "action": "edit", "description": "Edit data models"},
        {"resource": "data_models", "action": "delete", "description": "Delete data models"},
        
        # Upload permissions
        {"resource": "uploads", "action": "view", "description": "View uploads"},
        {"resource": "uploads", "action": "create", "description": "Upload data"},
        {"resource": "uploads", "action": "rollback", "description": "Rollback uploads"},
        
        # Dashboard permissions
        {"resource": "dashboards", "action": "view", "description": "View dashboards"},
        {"resource": "dashboards", "action": "create", "description": "Create dashboards"},
        {"resource": "dashboards", "action": "edit", "description": "Edit dashboards"},
        {"resource": "dashboards", "action": "delete", "description": "Delete dashboards"},
        
        # Audit permissions
        {"resource": "audit", "action": "view", "description": "View audit logs"},
    ]
    
    # Create permissions
    permissions = {}
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(
            Permission.resource == perm_data["resource"],
            Permission.action == perm_data["action"]
        ).first()
        
        if not existing:
            perm = Permission(**perm_data)
            db.add(perm)
            db.flush()
            permissions[f"{perm_data['resource']}:{perm_data['action']}"] = perm
        else:
            permissions[f"{perm_data['resource']}:{perm_data['action']}"] = existing
    
    db.commit()
    
    # Define roles with their permissions
    roles_data = {
        "Super Admin": {
            "description": "Full system access",
            "is_system_role": True,
            "permissions": list(permissions.keys())  # All permissions
        },
        "Admin": {
            "description": "Administrative access",
            "is_system_role": True,
            "permissions": [
                "users:view", "users:create", "users:edit",
                "data_models:view", "data_models:create", "data_models:edit", "data_models:delete",
                "uploads:view", "uploads:create", "uploads:rollback",
                "dashboards:view", "dashboards:create", "dashboards:edit", "dashboards:delete",
            ]
        },
        "Standard User": {
            "description": "Standard user access",
            "is_system_role": True,
            "permissions": [
                "data_models:view",
                "uploads:view", "uploads:create",
                "dashboards:view",
            ]
        }
    }
    
    # Create roles and assign permissions
    for role_name, role_info in roles_data.items():
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        
        if not existing_role:
            role = Role(
                name=role_name,
                description=role_info["description"],
                is_system_role=role_info["is_system_role"]
            )
            db.add(role)
            db.flush()
            
            # Assign permissions to role
            for perm_key in role_info["permissions"]:
                if perm_key in permissions:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permissions[perm_key].id
                    )
                    db.add(role_perm)
            
            logger.info(f"Created role: {role_name}")
        else:
            logger.info(f"Role already exists: {role_name}")
    
    db.commit()
    logger.info("Roles and permissions initialized successfully")


def create_super_admin(db: Session):
    """Create default super admin user"""
    logger.info("Creating super admin user...")
    
    # Check if super admin already exists
    existing = db.query(User).filter(User.email == "admin@example.com").first()
    if existing:
        logger.info("Super admin already exists")
        return
    
    # Create super admin user
    admin_user = User(
        email="admin@example.com",
        full_name="Super Administrator",
        password_hash=get_password_hash("admin123"),  # Change in production!
        status=UserStatus.ACTIVE
    )
    db.add(admin_user)
    db.flush()
    
    # Assign Super Admin role
    super_admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
    if super_admin_role:
        user_role = UserRole(user_id=admin_user.id, role_id=super_admin_role.id)
        db.add(user_role)
    
    db.commit()
    logger.info("Super admin created: admin@example.com / admin123")


def init_db():
    """Initialize database with tables and seed data"""
    logger.info("Starting database initialization...")
    
    # Create tables
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Initialize roles and permissions
        init_roles_and_permissions(db)
        
        # Create super admin
        create_super_admin(db)
        
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)
        logger.info("Default Super Admin Credentials:")
        logger.info("Email: admin@example.com")
        logger.info("Password: admin123")
        logger.info("⚠️  Please change the default password in production!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
