from google.adk.agents import Agent
import requests

def fetch_relevant_memory(user_message = str):
    """Retrieves the relevant memories based on latest user message

    Args:
        user_message (str): Latest user message

    Returns:
        relevant memory: list of relevant memory
    """
    print(user_message)
    return ["",""]


memoryAgent = Agent(
    name="memoryAgent",
    model="gemini-2.0-flash",
    description="Memory agent that retrieves relevant conversation history",
    instruction="You are a memory agent responsible for retrieving relevant conversation history and user preferences to provide context for the conversation. Focus on remembering personal details, preferences, and important information shared by the user.",
    tools = [fetch_relevant_memory]
)
