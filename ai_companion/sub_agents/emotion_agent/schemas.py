"""
Pydantic schemas for structured emotion detection.
Simplified to use single input and output schemas.
"""

from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class EmotionType(str, Enum):
    """Enumeration of possible emotion types."""

    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    FEAR = "fear"
    ANXIETY = "anxiety"
    NEUTRAL = "neutral"
    INTEREST = "interest"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence levels for emotion detection."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Input schema for emotion detection requests
class EmotionDetectionRequest(BaseModel):
    """Input schema for emotion detection requests."""

    text: str = Field(
        description="The text to analyze for emotions", min_length=1, max_length=10000
    )


# Output schema for emotion detection responses
class EmotionDetectionResponse(BaseModel):
    """Structured output for emotion detection analysis."""

    primary_emotion: EmotionType = Field(
        description="The primary emotion detected in the text"
    )

    secondary_emotions: List[EmotionType] = Field(
        default=[], description="Additional emotions detected, in order of prominence"
    )

    intensity: int = Field(
        ge=1,
        le=10,
        description="Emotional intensity on a scale from 1 (very mild) to 10 (very intense)",
    )

    analysis: str = Field(
        description="Brief explanation of linguistic cues and context that led to this conclusion"
    )

    emotional_indicators: List[str] = Field(
        default=[],
        description="Specific words or phrases that indicate the detected emotions",
    )

    confidence: ConfidenceLevel = Field(
        description="The confidence level in the emotion detection"
    )

    context_influence: str = Field(
        default="",
        description="How conversation history influenced the emotion detection",
    )

    emotional_trajectory: str = Field(
        default="",
        description="Description of how emotions have evolved throughout the conversation",
    )

    conversation_sentiment: float = Field(
        ge=-1.0,
        le=1.0,
        default=0.0,
        description="Overall sentiment trend across the conversation from -1 (negative) to 1 (positive)",
    )
