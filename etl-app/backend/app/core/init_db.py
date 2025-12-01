from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import Role, Permission, RolePermission, User, UserRole, Organization, Department
from app.models.user import UserStatus
from app.utils import get_password_hash
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def init_organizations_and_departments(db: Session):
    """Initialize default organization and department"""
    logger.info("Initializing organizations and departments...")
    
    # Create default organization
    existing_org = db.query(Organization).filter(Organization.name == "Default Company").first()
    if not existing_org:
        org = Organization(
            name="Default Company",
            description="Default organization"
        )
        db.add(org)
        db.flush()
        org_id = org.id
        logger.info("Created organization: Default Company")
    else:
        org_id = existing_org.id
        logger.info("Organization already exists: Default Company")
    
    # Create default department
    existing_dept = db.query(Department).filter(Department.name == "Engineering").first()
    if not existing_dept:
        dept = Department(
            name="Engineering",
            organization_id=org_id
        )
        db.add(dept)
        db.flush()
        logger.info(f"Created department: Engineering (org_id={org_id})")
    else:
        logger.info("Department already exists: Engineering")
    
    db.commit()


def init_roles_and_permissions(db: Session):
    """Initialize default roles and permissions"""
    logger.info("Initializing roles and permissions...")
    # Ensure the roles table has the new `department_id` column (handle older DBs)
    try:
        with engine.connect() as conn:
            # quick check: try selecting the column
            conn.execute(text("SELECT department_id FROM roles LIMIT 1"))
    except Exception:
        logger.info("Patching roles table to add department_id column (if missing)")
        try:
            with engine.begin() as conn:
                # Add column (assume missing); plain ALTER without IF NOT EXISTS for compatibility
                conn.execute(text("ALTER TABLE roles ADD COLUMN department_id INT NULL"))
                # add index
                conn.execute(text("CREATE INDEX idx_roles_department_id ON roles (department_id)"))
                # add FK constraint (if departments table exists)
                conn.execute(text("ALTER TABLE roles ADD CONSTRAINT fk_roles_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE"))
        except Exception as e:
            logger.warning(f"Could not alter roles table automatically: {e}")
    
    permissions_data = [
        {"resource": "users", "action": "view", "description": "View users"},
        {"resource": "users", "action": "create", "description": "Create users"},
        {"resource": "users", "action": "edit", "description": "Edit users"},
        {"resource": "users", "action": "delete", "description": "Delete users"},
        
        {"resource": "data_models", "action": "view", "description": "View data models"},
        {"resource": "data_models", "action": "create", "description": "Create data models"},
        {"resource": "data_models", "action": "edit", "description": "Edit data models"},
        {"resource": "data_models", "action": "delete", "description": "Delete data models"},
        
        {"resource": "uploads", "action": "view", "description": "View uploads"},
        {"resource": "uploads", "action": "create", "description": "Upload data"},
        {"resource": "uploads", "action": "rollback", "description": "Rollback uploads"},
        
        {"resource": "dashboards", "action": "view", "description": "View dashboards"},
        {"resource": "dashboards", "action": "create", "description": "Create dashboards"},
        {"resource": "dashboards", "action": "edit", "description": "Edit dashboards"},
        {"resource": "dashboards", "action": "delete", "description": "Delete dashboards"},
        
        {"resource": "audit", "action": "view", "description": "View audit logs"},
    ]
    
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
    
    default_dept = db.query(Department).filter(Department.name == "Engineering").first()
    dept_id = default_dept.id if default_dept else None
    
    roles_data = {
        "Super Admin": {
            "description": "Full system access",
            "is_system_role": True,
            "permissions": list(permissions.keys())
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
    
    for role_name, role_info in roles_data.items():
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        
        if not existing_role:
            role = Role(
                name=role_name,
                description=role_info["description"],
                is_system_role=role_info["is_system_role"],
                department_id=dept_id
            )
            db.add(role)
            db.flush()
            
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
    # Ensure users table has department_id column for newer schema
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT department_id FROM users LIMIT 1"))
    except Exception:
        logger.info("Patching users table to add department_id column (if missing)")
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN department_id INT NULL"))
                conn.execute(text("CREATE INDEX idx_users_department_id ON users (department_id)"))
                conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE"))
        except Exception as e:
            logger.warning(f"Could not alter users table automatically: {e}")

    existing = db.query(User).filter(User.email == "admin@example.com").first()
    if existing:
        logger.info("Super admin already exists")
        return
    
    default_dept = db.query(Department).filter(Department.name == "Engineering").first()
    dept_id = default_dept.id if default_dept else None
    
    admin_user = User(
        email="admin@example.com",
        full_name="Super Administrator",
        password_hash=get_password_hash("admin123"),
        status=UserStatus.ACTIVE,
        department_id=dept_id
    )
    db.add(admin_user)
    db.flush()
    
    super_admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
    if super_admin_role:
        user_role = UserRole(user_id=admin_user.id, role_id=super_admin_role.id)
        db.add(user_role)
    
    db.commit()
    logger.info("Super admin created: admin@example.com / admin123")


def init_db():
    """Initialize database with tables and seed data"""
    logger.info("Starting database initialization...")
    
    create_tables()
    
    db = SessionLocal()
    
    try:
        init_organizations_and_departments(db)
        init_roles_and_permissions(db)
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
