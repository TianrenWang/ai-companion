from google.adk.agents import Agent
from .prompt import NORA_AGENT_INSTR

noraAgent = Agent(
    name="noraAgent",
    model="gemini-2.0-flash",
    description="You are Nora,",
    instruction=NORA_AGENT_INSTR,
)
