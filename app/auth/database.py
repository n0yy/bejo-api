from firebase_admin import firestore
from app.firebase import initialize_firebase
from typing import Optional, Dict, Any

# Initialize Firebase
initialize_firebase()

# Get Firestore client
db = firestore.client()
users_collection = db.collection("users")


def get_user_by_email(email: str):
    """Get user by email from Firestore"""
    try:
        # Gunakan parameter keyword filter
        users_ref = db.collection("users")
        query = users_ref.where(filter=firestore.FieldFilter("email", "==", email))
        docs = query.get()

        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new user in Firestore"""
    doc_ref = users_collection.document()
    doc_ref.set(user_data)
    user_data["id"] = doc_ref.id
    return user_data
