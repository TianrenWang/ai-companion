from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
import uuid
from models.user import User
from models.message import Message


class Memory(Document):
    """Memory document model - each memory entry with embedding and vertex index integration"""
        
    mem_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True)
    user_id: Link[User] = Field(..., index=True)
    summary: str = Field(..., description="Summary of the memory content")
    message_ids: Optional[List[Link[Message]]] = Field(default_factory=list, description="List of message links this memory was created from")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the memory")
    created_at: datetime = Field(default_factory=datetime.now)
    embedding: List[float] = Field(..., description="Dense vector embedding for semantic search")
    vertex_index_id: Optional[str] = Field(None, description="Vertex AI index identifier")
    vertex_datapoint_id: Optional[str] = Field(None, description="Vertex AI datapoint identifier")
    
    class Settings:
        name = "memories"
