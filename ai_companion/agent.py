from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from ai_companion.sub_agents.nora_agent.agent import noraAgent
from ai_companion.sub_agents.emotion_agent.agent import emotionAgent
from ai_companion.sub_agents.memory_agent.agent import memoryAgent
from ai_companion.sub_agents.guardrails_agent.agent import guardrailAgent
from ai_companion.tools import save_to_memory_tool


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

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    description="The main orchestrating agent that coordinates the conversation workflow and manages memory storage",
    instruction="Generate a response to the user's message using the sequential_workflow. Make sure to use the save_to_memory_tool whenever you need to save important information about the user for future conversations (personal details, preferences, important events, etc.).",
    sub_agents=[sequential_workflow],
    tools=[save_to_memory_tool],
)
