from google.adk.agents import LlmAgent
from .prompt import GUARDRAIL_AGENT_INSTR

guardrailAgent = LlmAgent(
    name="guardrailAgent",
    model="gemini-2.0-flash",
    description="Safety and escalation agent that monitors conversations for urgent situations requiring immediate attention",
    instruction=GUARDRAIL_AGENT_INSTR,
)
