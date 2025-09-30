from google.adk.agents import LlmAgent
from .prompt import GUARDRAIL_AGENT_INSTR
from .schemas import GuardrailResponse

guardrailAgent = LlmAgent(
    name="guardrailAgent",
    model="gemini-2.0-flash",
    description="Safety and escalation agent that monitors conversations for urgent situations requiring immediate attention and logs the result.",
    instruction=GUARDRAIL_AGENT_INSTR,
    output_key="guardrail_response",
    output_schema=GuardrailResponse,
)
