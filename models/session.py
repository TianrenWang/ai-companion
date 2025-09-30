from datetime import datetime
from typing import List, Dict, Any, Optional
from beanie import Document, Indexed, Link, before_event, Replace, Insert
from pydantic import BaseModel, Field
import uuid
from models.user import User


class EmotionSnapshot(BaseModel):
    """Emotion state snapshot for a session"""
    valence: float = Field(..., ge=-1.0, le=1.0, description="Emotional valence (-1 to 1)")
    labels: List[str] = Field(default_factory=list, description="Emotion labels (e.g., 'sad', 'happy', 'anxious')")


class Session(Document):
    """Session document model - conversation sessions and audit trail"""
    
    session_id: uuid.UUID = Indexed(default_factory=uuid.uuid4, unique=True)
    title: str = Field(..., description="Title of the session")
    user_id: Link[User]
    start_ts: datetime =  Field(default_factory=datetime.now)
    end_ts: Optional[datetime] = Field(default_factory=datetime.now)
    transcript_uri: Optional[str] = Field(None, description="GS bucket URI for full transcript")
    summary: Optional[str] = Field(None, description="Short text summary of the session")
    used_memories: List[str] = Field(default_factory=list, description="List of memory IDs used in this session")
    emotion_snapshot: Optional[EmotionSnapshot] = Field(None, description="Emotion state at session end")
    
    class Settings:
        name = "sessions"
    
    @before_event([Replace, Insert])
    def update_updated_at(self):
        self.end_ts = datetime.now()
    
    def add_used_memory(self, memory_id: str):
        """Add a memory ID to the used memories list"""
        if memory_id not in self.used_memories:
            self.used_memories.append(memory_id)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate session duration in seconds"""
        if self.end_ts:
            return (self.end_ts - self.start_ts).total_seconds()
        return None
