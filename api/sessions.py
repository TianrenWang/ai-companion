from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models import Session, User, EmotionSnapshot

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    """Request model for creating a new session."""
    user_id: str = Field(..., description="User ID for the session")
    title: str = Field(..., description="Title of the session")

class SessionUpdate(BaseModel):
    """Request model for updating a session."""
    title: Optional[str] = Field(None, description="Updated session title")
    summary: Optional[str] = Field(None, description="Updated session summary")
    transcript_uri: Optional[str] = Field(None, description="GS bucket URI for full transcript")
    used_memories: Optional[List[str]] = Field(None, description="List of memory IDs used in this session")
    emotion_snapshot: Optional[EmotionSnapshot] = Field(None, description="Emotion state at session end")
    end_session: bool = Field(default=False, description="Whether to end the session")

class SessionResponse(BaseModel):
    """Response model for session data."""
    title: str
    session_id: str
    user_id: str
    start_ts: datetime
    end_ts: Optional[datetime]
    transcript_uri: Optional[str]
    summary: Optional[str]
    used_memories: List[str]
    emotion_snapshot: Optional[EmotionSnapshot]
    duration_seconds: Optional[float]

class SessionListResponse(BaseModel):
    """Response model for session list with pagination."""
    sessions: List[SessionResponse]
    total: int
    page: int
    page_size: int
    has_next: bool

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: SessionCreate):
    """
    Create a new conversation session.
    """
    try:
        # Verify user exists - look up by user_id field, not document id
        # Convert string user_id to UUID for lookup
        try:
            user_uuid = uuid.UUID(session_data.user_id)
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
        
        # Create new session
        session = Session(
            user_id=user,  # Pass the User object, not a string
            title=session_data.title,
            start_ts=datetime.now(),
            end_ts=None  # Session is active
        )
        
        await session.insert()
        
        # Fetch the linked user to get the user_id
        await session.fetch_link(Session.user_id)
        
        return SessionResponse(
            title=session.title,
            session_id=str(session.session_id),
            user_id=str(session.user_id.user_id),
            start_ts=session.start_ts,
            end_ts=session.end_ts,
            transcript_uri=session.transcript_uri,
            summary=session.summary,
            used_memories=session.used_memories,
            emotion_snapshot=session.emotion_snapshot,
            duration_seconds=session.duration_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, session_data: SessionUpdate):
    """
    Update an existing session.
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
        
        # Get the session by session_id field, not document _id
        session = await Session.find_one(Session.session_id == session_uuid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Update fields if provided
        if session_data.title is not None:
            session.title = session_data.title
        
        if session_data.summary is not None:
            session.summary = session_data.summary
        
        if session_data.transcript_uri is not None:
            session.transcript_uri = session_data.transcript_uri
        
        if session_data.used_memories is not None:
            session.used_memories = session_data.used_memories
        
        if session_data.emotion_snapshot is not None:
            session.emotion_snapshot = session_data.emotion_snapshot
        
        # End session if requested
        if session_data.end_session and session.end_ts is None:
            session.end_ts = datetime.now()
        
        # Save the updated session
        await session.save()
        
        # Fetch the linked user to get the user_id
        await session.fetch_link(Session.user_id)
        
        return SessionResponse(
            title=session.title,
            session_id=str(session.session_id),
            user_id=str(session.user_id.user_id),
            start_ts=session.start_ts,
            end_ts=session.end_ts,
            transcript_uri=session.transcript_uri,
            summary=session.summary,
            used_memories=session.used_memories,
            emotion_snapshot=session.emotion_snapshot,
            duration_seconds=session.duration_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get a specific session by ID.
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
        
        # Get the session by session_id field, not document _id
        session = await Session.find_one(Session.session_id == session_uuid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Fetch the linked user to get the user_id
        await session.fetch_link(Session.user_id)
        
        return SessionResponse(
            title=session.title,
            session_id=str(session.session_id),
            user_id=str(session.user_id.user_id),
            start_ts=session.start_ts,
            end_ts=session.end_ts,
            transcript_uri=session.transcript_uri,
            summary=session.summary,
            used_memories=session.used_memories,
            emotion_snapshot=session.emotion_snapshot,
            duration_seconds=session.duration_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: str,
    active_only: bool = Query(default=False, description="Only return active sessions")
):
    """
    Get all sessions for a specific user.
    """
    try:
        # Verify user exists - convert string user_id to UUID for lookup
        try:
            user_uuid = uuid.UUID(user_id)
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
        
        # Build query - match user's user_id field with session's user_id.id field
        query = Session.find(Session.user_id.id == user.id)
        
        # Get all sessions sorted by start time
        sessions = await query.sort("-start_ts").to_list()
        
        # Convert to response format
        session_responses = []
        for session in sessions:
            # Fetch the linked user to get the user_id
            await session.fetch_link(Session.user_id)
            session_responses.append(SessionResponse(
                title=session.title,
                session_id=str(session.session_id),
                user_id=str(session.user_id.user_id),
                start_ts=session.start_ts,
                end_ts=session.end_ts,
                transcript_uri=session.transcript_uri,
                summary=session.summary,
                used_memories=session.used_memories,
                emotion_snapshot=session.emotion_snapshot,
                duration_seconds=session.duration_seconds
            ))
        
        return session_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )
