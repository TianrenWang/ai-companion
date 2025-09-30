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
