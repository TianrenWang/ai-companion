from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from sub_agents.nora_agent.agent import noraAgent
from sub_agents.emotion_agent.agent import emotionAgent
from sub_agents.memory_agent.agent import memoryAgent
from sub_agents.guardrails_agent.agent import guardrailsAgent


researchAgent = ParallelAgent(
    name="conversation_state_research_agent",
    sub_agents=[memoryAgent, emotionAgent],
    description="Gathers information about past memory related to the participants of this conversation,"
    "as well as the emotional state of the agent.",
)


root_agent = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[researchAgent, noraAgent, guardrailAgent],
    description="The agent used to develop the final message used for the response to the user. It should happen"
    "in the following order: research the conversation state using 'researchAgent', then have the 'noraAgent' generate"
    "a personable tentative message to response with, and lastly pass the output through 'guardrailAgent' to transform"
    "the output to something that filters out topics that are off-limit.",
)
