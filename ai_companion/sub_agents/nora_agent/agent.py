from google.adk.agents import Agent
from .prompt import NORA_AGENT_INSTR

noraAgent = Agent(
    name="noraAgent",
    model="gemini-2.0-flash",
    description="A warm and empathetic companion for elderly residents in an old age home",
    instruction=NORA_AGENT_INSTR,
    output_key="nora_response",
)
