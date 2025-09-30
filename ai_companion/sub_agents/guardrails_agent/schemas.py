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
