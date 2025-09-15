from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security

router = APIRouter()

@router.get("/scores")
async def get_scores(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This endpoint would typically be for admins only
    # Check if the user has admin role from the token
    # For now, just return dummy data
    return [
        {"user": "user1", "score": 85},
        {"user": "user2", "score": 92}
    ]

@router.get("/scores/{user_id}")
async def get_user_scores(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Get scores for a specific user
    return {"user_id": user_id, "scores": [85, 90, 78]}