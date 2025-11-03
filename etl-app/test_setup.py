#!/usr/bin/env python3
"""
Setup Verification Script
Tests that all components are properly configured
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app.main import app
        from app.api import api_router
        from app.models import User, Role, DataModel
        from app.schemas import UserCreate, DataModelCreate
        from app.services import UserService, DataModelService, UploadService
        from app.utils import get_password_hash, FileHandler, DynamicTableManager
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from app.core.config import settings
        print(f"✓ Database URL configured: {settings.DATABASE_URL.split('@')[-1]}")
        print(f"✓ Upload directory: {settings.UPLOAD_DIR}")
        print(f"✓ Allowed extensions: {settings.ALLOWED_EXTENSIONS}")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {str(e)}")
        return False


def test_routes():
    """Test API routes"""
    print("\nTesting API routes...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/users/me",
            "/api/v1/data-models",
            "/api/v1/uploads/preview",
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Route exists: {route}")
            else:
                print(f"✗ Route missing: {route}")
                return False
        
        print(f"✓ Total routes registered: {len(routes)}")
        return True
    except Exception as e:
        print(f"✗ Route test failed: {str(e)}")
        return False


def test_models():
    """Test database models"""
    print("\nTesting database models...")
    try:
        from app.models import User, Role, Permission, DataModel, UploadHistory
        from app.core.database import Base
        
        tables = Base.metadata.tables.keys()
        expected_tables = [
            'users', 'roles', 'permissions', 'data_models', 
            'upload_history', 'audit_logs', 'dashboards'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"✓ Model/Table defined: {table}")
            else:
                print(f"✗ Model/Table missing: {table}")
                return False
        
        print(f"✓ Total tables defined: {len(tables)}")
        return True
    except Exception as e:
        print(f"✗ Model test failed: {str(e)}")
        return False


def test_schemas():
    """Test Pydantic schemas"""
    print("\nTesting Pydantic schemas...")
    try:
        from app.schemas import (
            UserCreate, DataModelCreate, UploadRequest, 
            FieldDefinition, ColumnMapping
        )
        
        # Test schema validation
        field = FieldDefinition(
            name="test_field",
            type="string",
            required=True
        )
        print(f"✓ FieldDefinition schema works")
        
        print("✓ All schemas functional")
        return True
    except Exception as e:
        print(f"✗ Schema test failed: {str(e)}")
        return False


def test_utilities():
    """Test utility functions"""
    print("\nTesting utility functions...")
    try:
        from app.utils import get_password_hash, verify_password, create_access_token
        
        # Test password hashing
        password = "test123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed), "Password verification failed"
        print("✓ Password hashing works")
        
        # Test JWT token
        token = create_access_token({"sub": 1})
        assert len(token) > 0, "Token generation failed"
        print("✓ JWT token generation works")
        
        print("✓ All utilities functional")
        return True
    except Exception as e:
        print(f"✗ Utility test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ETL Pipeline Application - Setup Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_routes,
        test_models,
        test_schemas,
        test_utilities,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed! Application is ready.")
        print("\nNext steps:")
        print("1. Set up MySQL database")
        print("2. Update .env with database credentials")
        print("3. Run: python init_db.py")
        print("4. Run: python run.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
