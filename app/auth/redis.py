import redis
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", ""),
    decode_responses=True,
)


def get_user_from_cache(email: str):
    """Get user from Redis cache"""
    user_data = redis_client.get(f"user:{email}")
    if user_data:
        return json.loads(user_data)
    return None


def set_user_in_cache(email: str, user_data: dict, expire: int = 3600):
    """Set user in Redis cache"""
    redis_client.setex(f"user:{email}", expire, json.dumps(user_data))


def delete_user_from_cache(email: str):
    """Delete user from Redis cache"""
    redis_client.delete(f"user:{email}")
