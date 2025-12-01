from fastapi import APIRouter
from app.api import auth, users, data_models, uploads, roles, organizations, departments

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(data_models.router)
api_router.include_router(uploads.router)
api_router.include_router(roles.router)
api_router.include_router(organizations.router)
api_router.include_router(departments.router)

__all__ = ["api_router"]
