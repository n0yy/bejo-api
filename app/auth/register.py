from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.auth.models import UserCreate, User
from app.auth.database import get_user_by_email, create_user
from app.auth.utils import hash_password
from app.auth.redis import set_user_in_cache

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email Anda sudah terdaftar")

    # Create user
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    user_data["created_at"] = datetime.now().isoformat()
    user_data["status"] = "pending"  # Initial status | Waiting to approved by superuser
    user_data["role"] = "user"  # Initial role
    user_data["level_knowledge"] = "low"  # Low | Medium | High | Ultra

    # Save to Firestore
    user_data = create_user(user_data)

    # Cache the user data
    set_user_in_cache(user.email, user_data)

    # Return user without password
    del user_data["password"]

    return user_data
