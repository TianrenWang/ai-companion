from datetime import datetime
from typing import List, Literal, Optional, Dict, Any
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
import uuid
from models.session import Session
from models.user import User


class Message(Document):
    """Message document model - tracks individual messages in conversation sessions"""
    
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True)  
    session_id: Link[Session]
    user_id: Link[User]
    speaker: Literal["agent", "human"] = Field(..., description="Who is speaking")
    content: str = Field(..., description="Message content/text")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "messages"
    
    
    @classmethod
    async def get_session_messages(cls, session_id: str, limit: Optional[int] = None) -> List["Message"]:
        """Get all messages for a session, ordered by timestamp"""
        query = cls.find(cls.session_id == session_id).sort("timestamp")
        if limit:
            query = query.limit(limit)
        return await query.to_list()
    
    @classmethod
    async def get_user_messages(cls, user_id: str, limit: Optional[int] = None) -> List["Message"]:
        """Get all messages for a user, ordered by timestamp (most recent first)"""
        query = cls.find(cls.user_id == user_id).sort("timestamp", -1)
        if limit:
            query = query.limit(limit)
        return await query.to_list()
    
    @classmethod
    async def get_conversation_thread(cls, session_id: str, speaker: Optional[str] = None) -> List["Message"]:
        """Get conversation thread for a session, optionally filtered by speaker"""
        query = cls.find(cls.session_id == session_id)
        if speaker:
            query = query.find(cls.speaker == speaker)
        return await query.sort("timestamp").to_list()
