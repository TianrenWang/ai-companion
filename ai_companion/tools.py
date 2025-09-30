"""
Tools for the AI companion system.
"""

from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from .sub_agents.guardrails_agent.schemas import GuardrailResponse


def save_to_memory(text: str) -> str:
    """
    Dummy function for saving to memory - doesn't actually save anything.

    Args:
        text: The text to save

    Returns:
        Simple acknowledgment without saving
    """
    # Dummy function - doesn't actually save anything
    return {"status": "success"}


save_to_memory_tool = FunctionTool(
    func=save_to_memory,
)


def _load_precreated_variables(callback_context: CallbackContext):
    """Load precreated variables with initial values before sequential workflow runs"""
    callback_context.state["nora_response"] = (
        "I'm here to help and chat with you. How are you feeling today?"
    )
    callback_context.state["guardrail_response"] = GuardrailResponse(action="ALLOW")
