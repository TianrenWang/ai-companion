from fastapi import APIRouter, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import os
import uuid
from dotenv import load_dotenv

from google import genai
from google.genai import types

from models import Memory, User, Message

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/memories", tags=["memories"])

VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "memory_vector_index")

class MemoryCreate(BaseModel):
    user_id: str = Field(..., description="User ID for the memory")
    summary: str = Field(..., description="Summary of the memory content")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the memory")


class MemorySearch(BaseModel):
    query: str = Field(..., description="Search query for semantic search")
    user_id: str = Field(..., description="User ID to search within")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of results to return")
    tags: Optional[List[str]] = Field(None, description="Filter by specific tags")


class MemoryResponse(BaseModel):
    mem_id: str
    user_id: str
    summary: str
    tags: List[str]
    created_at: datetime
    score: Optional[float] = None


class MemoryClusterResponse(BaseModel):
    cluster_id: str
    theme: str
    memories: List[MemoryResponse]
    count: int


class MemoryMergeRequest(BaseModel):
    memory_ids: List[str] = Field(..., description="List of memory IDs to merge")
    new_summary: Optional[str] = Field(None, description="New summary for merged memory")


class UpdateTagsRequest(BaseModel):
    tags: List[str] = Field(..., description="New tags for the memory")


async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding using the current Google GenAI SDK.
    Model: gemini-embedding-001
    """
    try:
        result = await client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        return result.embeddings[0].values
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {e}"
        )


async def run_aggregate(pipeline: list) -> List[dict]:
    """
    Use Motor collection directly for predictable aggregate behavior.
    """
    cursor = Memory.get_pymongo_collection().aggregate(pipeline)
    return await cursor.to_list(length=None)

@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(memory_data: MemoryCreate):
    """
    Create a new memory with automatic embedding generation and tag extraction.
    """
    try:
        # Convert string user_id to UUID for lookup
        try:
            user_uuid = uuid.UUID(memory_data.user_id)
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


        embedding = await generate_embedding(memory_data.summary)

        memory = Memory(
            user_id=user,
            summary=memory_data.summary,
            message_ids=[],
            tags=memory_data.tags or [],
            embedding=embedding,
        )
        await memory.insert()

        # Fetch the linked user to access its ID
        await memory.fetch_link(Memory.user_id)
        
        return MemoryResponse(
            mem_id=str(memory.mem_id),
            user_id=str(memory.user_id.user_id),
            summary=memory.summary,
            message_ids=[],
            tags=memory.tags,
            created_at=memory.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to create memory: {e}")



class GlobalSummarySearch(BaseModel):
    query: str = Field(..., description="Semantic query")
    limit: int = Field(default=5, ge=1, le=50)

@router.post("/search-global-summaries")
async def search_global_summaries(payload: GlobalSummarySearch):
    qvec = await generate_embedding(payload.query)
    pipeline = [
        {"$vectorSearch": {
            "index": VECTOR_INDEX_NAME,
            "path": "embedding",
            "queryVector": qvec,
            "numCandidates": max(50, payload.limit * 10),
            "limit": payload.limit
        }},
        {"$project": {
            "_id": 0,
            "summary": 1,
            # uncomment next line if you also want scores in debug
            # "score": {"$meta": "vectorSearchScore"},
        }},
    ]
    docs = await run_aggregate(pipeline)
    return [d["summary"] for d in docs]