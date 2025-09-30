from .prompt import EMOTION_AGENT_INSTR
from .schemas import EmotionDetectionResponse
from google.adk.agents import LlmAgent

# Emotion detection agent using Google ADK with Vertex AI
emotionAgent = LlmAgent(
    # A unique name for the agent.
    name="emotion_detection_agent",
    model="gemini-2.0-flash",
    # A short description of the agent's purpose.
    description="An emotion detection specialist that analyzes user text and identifies the emotions being expressed",
    # Instructions to set the agent's behavior.
    instruction=EMOTION_AGENT_INSTR,  # Configure the agent to use structured output
    output_schema=EmotionDetectionResponse,
    output_key="emotion_detection_response",
)
