from google.adk.agents import Agent
import requests
from google.adk.tools import FunctionTool
import requests

from .prompt import RETREIVE_RELEVANT_MEMORY


def fetch_relevant_memory(user_message: str):
    """Retrieves the relevant memories based on latest user message

    Args:
        user_message (str): Latest user message

    Returns:
        relevant memory: list of strings, where each string corresponds to a memory summary and is ordered by relevance in descending order
    """
    search_payload = {
        "query": user_message,
        "user_id": "7a5d7dcf-e0fc-48bb-9790-cc27e2714998", # Retain the hardcoded user_id from the original selection
        "limit": 5
    }
    response = requests.post(f"http://localhost:8001/memories/search-global-summaries", json=search_payload)
    memories = response.json()
    return "\n".join(memories)


fetch_relevant_memory_tool = FunctionTool(
    func=fetch_relevant_memory,
)

memoryAgent = Agent(
    name="memoryAgent",
    model="gemini-2.0-flash",
    description="Memory agent that retrieves relevant conversation history",
    instruction=RETREIVE_RELEVANT_MEMORY,
    tools = [fetch_relevant_memory_tool]
)
