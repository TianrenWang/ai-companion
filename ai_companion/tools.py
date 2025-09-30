"""
Tools for the AI companion system.
"""

from google.adk.tools import FunctionTool


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
