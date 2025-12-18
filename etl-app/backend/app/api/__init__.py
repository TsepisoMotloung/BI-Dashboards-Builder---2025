from fastapi import APIRouter
from app.api import auth, uploads

# Restrict API surface: keep only authentication and uploads
api_router = APIRouter()

# Keep auth (login) and uploads endpoints only
api_router.include_router(auth.router)
api_router.include_router(uploads.router)

__all__ = ["api_router"]
