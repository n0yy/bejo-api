from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.auth.models import Token
from app.auth.database import get_user_by_email
from app.auth.utils import verify_password, create_access_token
from app.auth.redis import get_user_from_cache, set_user_in_cache

router = APIRouter(prefix="/auth", tags=["Authentication"])


class EmailPasswordRequestForm(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=Token)
async def login(form_data: EmailPasswordRequestForm):
    """Login user"""
    # Try to get user from cache first
    user = get_user_from_cache(form_data.email)

    # If not in cache, get from Firestore
    if not user:
        user = get_user_by_email(form_data.email)
        if user:
            # Cache the user data
            set_user_in_cache(form_data.email, user)

    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Email atau password salah")

    # Check user status
    if user["status"] == "pending":
        raise HTTPException(
            status_code=403,
            detail="Pendaftaran anda sedang di tinjau, mohon tunggu minimal 1 jam.",
        )
    elif user["status"] == "rejected":
        raise HTTPException(
            status_code=403,
            detail="Maaf pendaftaran anda gagal karena tidak memenuhi syarat",
        )
    elif user["status"] != "approved":
        raise HTTPException(status_code=403, detail="Status akun tidak valid")

    # Create token
    access_token_expires = timedelta(weeks=4)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
