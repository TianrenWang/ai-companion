from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from models import User

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    """Request model for creating a new user."""
    display_name: str

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create a new user in the database.

    Args:
        user_data (UserCreate): The user data containing the display name.

    Returns:
        User: The newly created user object, including its generated user_id and creation timestamp.

    Raises:
        HTTPException: If there's an error during user creation.
    """
    new_user = User(display_name=user_data.display_name)
    try:
        await new_user.insert()
    except Exception as e:
        # In a production environment, you might want more specific error handling,
        # e.g., checking for unique constraint violations if display_name were indexed as unique.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {e}"
        )
    return new_user
