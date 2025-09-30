from google.adk.agents import Agent

memoryAgent = Agent(
    name="memoryAgent",
    model="gemini-2.0-flash",
    description="Memory agent that retrieves and manages conversation history and user preferences",
    instruction="You are a memory agent responsible for retrieving relevant conversation history and user preferences to provide context for the conversation. Focus on remembering personal details, preferences, and important information shared by the user.",
)
