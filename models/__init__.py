"""
AI Companion Models

This module contains all the Beanie document models for the AI Companion application:
- User: User profiles and consent management
- Memory: Long-term memory storage with embeddings
- Session: Conversation session tracking and audit
- Message: Individual message tracking within sessions
"""

from .user import User
from .memory import Memory
from .session import Session, EmotionSnapshot
from .message import Message

__all__ = [
    "User",
    "Memory",
    "Session",
    "EmotionSnapshot",
    "Message",
]
