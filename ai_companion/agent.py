from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from ai_companion.prompt import ROOT_AGENT_INST
from ai_companion.sub_agents.nora_agent.agent import noraAgent
from ai_companion.sub_agents.emotion_agent.agent import emotionAgent
from ai_companion.sub_agents.memory_agent.agent import memoryAgent
from ai_companion.sub_agents.guardrails_agent.agent import guardrailAgent
from ai_companion.tools import save_to_memory_tool
from google.adk.tools.agent_tool import AgentTool
from ai_companion.tools import _load_precreated_variables


sequential_workflow = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[memoryAgent, emotionAgent, noraAgent, guardrailAgent],
    description="The agent used to develop the final message used for the response to the user. It should happen"
    "in the following order: fetch the relevant memory using 'memoryAgent', then have the 'emotionAgent' analyze the emotion of the user, then have the 'noraAgent' generate"
    "a personable tentative message to response with, and lastly pass the output through 'guardrailAgent' to transform"
    "the output to something that filters out topics that are off-limit.",
)


root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    description="The main orchestrating agent that coordinates the conversation workflow and manages memory storage",
    instruction=ROOT_AGENT_INST,
    tools=[
        save_to_memory_tool,
        # AgentTool(agent=sequential_workflow, skip_summarization=True),
    ],
    sub_agents=[sequential_workflow],
    before_agent_callback=_load_precreated_variables,
)
