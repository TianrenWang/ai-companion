<<<<<<< HEAD
from enum import Enum
from pydantic import BaseModel, Field


class GuardrailAction(str, Enum):
    """Enum for guardrail actions."""

    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class GuardrailResponse(BaseModel):
    """Structured output for guardrail response."""

    action: GuardrailAction = Field(
        description="The action to take: ALLOW, WARN, BLOCK, or ESCALATE"
    )
=======
"""
Pydantic schemas for the Guardrails agent.
"""

from enum import Enum


class RiskLevel(Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"

class Action(Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"

class GuardRailInputSchema:
    user_message: str
    persona_response: str
    conversation_history: str

class GuardrailResultSchema:
    status: RiskLevel
    action: Action
    final_response: str 
>>>>>>> cec733350e0a32b9b2e9234e27b48cdb53539677
