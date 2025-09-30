from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from .prompt import GUARDRAIL_AGENT_INSTR
from typing import List, Dict

def log_guardrail_result(
    status: str, 
    action: str, 
    final_response: str, 
    risk_score: int,
    violations: List[str]
) -> str:
    """
    Logs the final guardrail decision and response to a security database.
    
    Args:
        status: The final risk status (green, orange, red).
        action: The final action taken (allow, warn, block, escalate).
        final_response: The message sent to the user.
        risk_score: The calculated risk score (0-100).
        violations: List of policy IDs that were violated.
        
    Returns:
        A confirmation message indicating the log was successful.
    """

    # TODO: Implement DB push here
    print(f"--- LOGGING GUARDRAIL RESULT ---")
    print(f"Status: {status}, Action: {action}, Score: {risk_score}")
    print(f"Violations: {violations}")
    print(f"Response: {final_response[:50]}...")
    
    return json.dumps({
        "log_status": "SUCCESS",
        "action_taken": action
    })

log_tool = FunctionTool(func=log_guardrail_result)

guardrailAgent = Agent(
    name="guardrailAgent",
    model="gemini-2.0-flash",
    description="Safety and escalation agent that monitors conversations for urgent situations requiring immediate attention and logs the result.",
    instruction=GUARDRAIL_AGENT_INSTR,
    tools=[log_tool]
)
