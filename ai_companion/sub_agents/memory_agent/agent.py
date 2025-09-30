from google.adk.agents import Agent
import requests
from google.adk.tools import FunctionTool

from .prompt import RETREIVE_RELEVANT_MEMORY


def fetch_relevant_memory(user_message: str):
    """Retrieves the relevant memories based on latest user message

    Args:
        user_message (str): Latest user message

    Returns:
        relevant memory: string of relevant memory
    """
    print(user_message)
    return "No relevant information found"


fetch_relevant_memory_tool = FunctionTool(
    func=fetch_relevant_memory,
)

memoryAgent = Agent(
    name="memoryAgent",
    model="gemini-2.0-flash",
    description="Memory agent that retrieves relevant conversation history",
    instruction=RETREIVE_RELEVANT_MEMORY
    tools = [fetch_relevant_memory_tool]
)
