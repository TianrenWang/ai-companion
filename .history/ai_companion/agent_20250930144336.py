from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from ai_companion.prompt import ROOT_AGENT_INST
from ai_companion.sub_agents.nora_agent.agent import noraAgent
from ai_companion.sub_agents.emotion_agent.agent import emotionAgent
from ai_companion.sub_agents.memory_agent.agent import memoryAgent
from ai_companion.sub_agents.guardrails_agent.agent import guardrailAgent
from ai_companion.tools import save_to_memory_tool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

researchAgent = ParallelAgent(
    name="conversation_state_research_agent",
    sub_agents=[memoryAgent, emotionAgent],
    description="Gathers information about past memory related to the participants of this conversation,"
    "as well as the emotional state of the agent.",
)


sequential_workflow = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[researchAgent, noraAgent, guardrailAgent],
    description="The agent used to develop the final message used for the response to the user. It should happen"
    "in the following order: research the conversation state using 'researchAgent', then have the 'noraAgent' generate"
    "a personable tentative message to response with, and lastly pass the output through 'guardrailAgent' to transform"
    "the output to something that filters out topics that are off-limit.",
)


def save_relevant_memory(relevant_memory: str):
    """Store relevant memory of the user.

    Args:
        relevant_memory (str): Relevant memory

    """
    print(f"relevant memory to store: {relevant_memory}")


save_relevant_memory_tool = FunctionTool(
    func=save_relevant_memory,
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    description="The main orchestrating agent that coordinates the conversation workflow and manages memory storage",
    instruction=ROOT_AGENT_INST,
    tools=[
        save_to_memory_tool,
        AgentTool(agent=sequential_workflow, skip_summarization=True),
    ],
)
