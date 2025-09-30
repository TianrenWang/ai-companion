from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid

from models import Message, Session, User

router = APIRouter(prefix="/messages", tags=["messages"])

class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    session_id: str = Field(..., description="Session ID for the message")
    user_id: str = Field(..., description="User ID for the message")
    speaker: Literal["agent", "human"] = Field(..., description="Who is speaking")
    content: str = Field(..., description="Message content/text")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")

class MessageUpdate(BaseModel):
    """Request model for updating a message."""
    content: Optional[str] = Field(None, description="Updated message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated message metadata")

class MessageResponse(BaseModel):
    """Response model for message data."""
    message_id: str
    session_id: str
    user_id: str
    speaker: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

class ConversationThreadResponse(BaseModel):
    """Response model for conversation thread."""
    session_id: str
    messages: List[MessageResponse]
    total_messages: int
    human_messages: int
    agent_messages: int

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(message_data: MessageCreate):
    """
    Create a new message in a session.
    """
    try:
        
        # Convert string session_id to UUID for lookup
        try:
            session_uuid = uuid.UUID(message_data.session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        session = await Session.find_one(Session.session_id == session_uuid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Convert string user_id to UUID for lookup
        try:
            user_uuid = uuid.UUID(message_data.user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format. Must be a valid UUID."
            )
        
        user = await User.find_one(User.user_id == user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        message = Message(
            session_id=session,
            user_id=user,
            speaker=message_data.speaker,
            content=message_data.content,
            metadata=message_data.metadata or {}
        )
        
        await message.insert()
        
        # Fetch the linked documents to access their IDs
        await message.fetch_link(Message.session_id)
        await message.fetch_link(Message.user_id)
        
        return MessageResponse(
            message_id=str(message.message_id),
            session_id=str(message.session_id.session_id),
            user_id=str(message.user_id.user_id),
            speaker=message.speaker,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    """
    Get a specific message by ID.
    """
    try:
        # Convert string message_id to UUID for lookup
        try:
            message_uuid = uuid.UUID(message_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid message_id format. Must be a valid UUID."
            )
        
        message = await Message.find_one(Message.message_id == message_uuid)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Fetch the linked documents to access their IDs
        await message.fetch_link(Message.session_id)
        await message.fetch_link(Message.user_id)
        
        return MessageResponse(
            message_id=str(message.message_id),
            session_id=str(message.session_id.session_id),
            user_id=str(message.user_id.user_id),
            speaker=message.speaker,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    speaker: Optional[Literal["agent", "human"]] = Query(None, description="Filter by speaker")
):
    """
    Get all messages for a specific session with optional speaker filtering.
    """
    try:
        # Convert string session_id to UUID for lookup
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        session = await Session.find_one(Session.session_id == session_uuid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Query messages by the linked session's MongoDB _id
        query = Message.find(Message.session_id.id == session.id)
        
        if speaker:
            query = query.find(Message.speaker == speaker)
        
        messages = await query.sort("timestamp").to_list()
        
        message_responses = []
        for message in messages:
            # Fetch the linked documents to access their IDs
            await message.fetch_link(Message.session_id)
            await message.fetch_link(Message.user_id)
            
            message_responses.append(MessageResponse(
                message_id=str(message.message_id),
                session_id=str(message.session_id.session_id),
                user_id=str(message.user_id.user_id),
                speaker=message.speaker,
                content=message.content,
                timestamp=message.timestamp,
                metadata=message.metadata
            ))
        
        return message_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session messages: {str(e)}"
        )
