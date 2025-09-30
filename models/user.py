from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from beanie import Document, Indexed
from pydantic import BaseModel, Field

class User(Document):
    """User document model - one document per user"""
    
    user_id: UUID = Field(default_factory=uuid4, unique=True)
    display_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "users"