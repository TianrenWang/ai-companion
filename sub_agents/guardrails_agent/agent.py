from google.adk.agents import Agent
from .prompt import GUARDRAIL_AGENT_INSTR

guardrailAgent = Agent(
    name="guardrailAgent",
    model="gemini-2.0-flash",
    description="Safety and escalation agent that monitors conversations for urgent situations requiring immediate attention",
    instruction=GUARDRAIL_AGENT_INSTR,
)
