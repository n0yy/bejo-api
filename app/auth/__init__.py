from fastapi import APIRouter
from app.auth.register import router as register_router
from app.auth.login import router as login_router
from app.auth.users import router as users_router
from app.auth.dependencies import get_current_user

# Create main auth router
router = APIRouter(prefix="/api", tags=["Authentication"])

# Include all auth routes
router.include_router(register_router)
router.include_router(login_router)
router.include_router(users_router)

# Export get_current_user
__all__ = ["router", "get_current_user"]
