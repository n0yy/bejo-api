from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.auth.models import UserCreate, User
from app.auth.database import get_user_by_email, create_user
from app.auth.utils import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    user_data["created_at"] = datetime.now().isoformat()
    user_data["status"] = (
        "pending"  # Initial status | Waiting to approved by superadmin
    )
    user_data["role"] = "user"  # Initial role

    # Save to Firestore
    user_data = create_user(user_data)

    # Return user without password
    del user_data["password"]

    return user_data
