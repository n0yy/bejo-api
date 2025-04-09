from firebase_admin import firestore
from app.firebase import initialize_firebase
from typing import Optional, Dict, Any

# Initialize Firebase
initialize_firebase()

# Get Firestore client
db = firestore.client()
users_collection = db.collection("users")


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user from Firestore by email"""
    users = users_collection.where("email", "==", email).limit(1).get()
    for user in users:
        user_data = user.to_dict()
        user_data["id"] = user.id
        return user_data
    return None


def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new user in Firestore"""
    doc_ref = users_collection.document()
    doc_ref.set(user_data)
    user_data["id"] = doc_ref.id
    return user_data
