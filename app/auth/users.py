from fastapi import APIRouter, HTTPException, Depends
from app.auth.models import User, UserBase, UserUpdate
from app.auth.database import users_collection, get_user_by_email
from app.auth.dependencies import get_current_user
from app.auth.redis import delete_user_from_cache
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


def check_superuser(current_user: dict):
    """Check if user is superuser"""
    if current_user["role"] != "superuser":
        raise HTTPException(
            status_code=403, detail="Hanya superuser yang dapat mengakses fitur ini"
        )


@router.get("", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users"""
    users = []
    for doc in users_collection.stream():
        user_data = doc.to_dict()
        user_data["id"] = doc.id
        # Remove password from response
        if "password" in user_data:
            del user_data["password"]
        users.append(user_data)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    doc = users_collection.document(user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    user_data = doc.to_dict()
    user_data["id"] = doc.id
    # Remove password from response
    if "password" in user_data:
        del user_data["password"]
    return user_data


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update user data"""
    # Check if user is superuser
    check_superuser(current_user)

    # Check if user exists
    doc = users_collection.document(user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    # Get existing user data
    existing_user = doc.to_dict()

    # Update user data
    update_data = {
        k: v
        for k, v in user_update.model_dump(exclude_unset=True).items()
        if v is not None
    }

    # If email is being changed, check if new email already exists
    if "email" in update_data and update_data["email"] != existing_user["email"]:
        if get_user_by_email(update_data["email"]):
            raise HTTPException(status_code=400, detail="Email sudah terdaftar")

        # Delete old cache
        delete_user_from_cache(existing_user["email"])

    # Update document
    users_collection.document(user_id).update(update_data)

    return {"message": "User berhasil di update!"}


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user"""
    # Check if user is superuser
    check_superuser(current_user)

    # Check if user exists
    doc = users_collection.document(user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    # Get user data for cache deletion
    user_data = doc.to_dict()

    # Delete user
    users_collection.document(user_id).delete()

    # Delete from cache
    delete_user_from_cache(user_data["email"])

    return {"message": "User berhasil dihapus"}
