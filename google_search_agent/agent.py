from google.adk.agents import Agent, ParallelAgent, SequentialAgent


memoryAgent = Agent(
    name="memoryAgent",
    model="",
    description="",
    instruction="",
)

emotionAgent = Agent(
    name="emotionAgent",
    model="",
    description="",
    instruction="",
)

researchAgent = ParallelAgent(
    name="conversation_state_research_agent",
    sub_agents=[memoryAgent, emotionAgent],
    description="Gathers information about past memory related to the participants of this conversation,"
    "as well as the emotional state of the agent.",
)


guardrailAgent = Agent(
    name="guardrailAgent",
    model="",
    description="",
    instruction="",
)

noraAgent = Agent(
    name="noraAgent",
    model="",
    description="",
    instruction="",
)

messageDevelopmentAgent = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[researchAgent, noraAgent, guardrailAgent],
    description="The agent used to develop the final message used for the response to the user. It should happen"
    "in the following order: research the conversation state using 'researchAgent', then have the 'noraAgent' generate"
    "a personable tentative message to response with, and lastly pass the output through 'guardrailAgent' to transform"
    "the output to something that filters out topics that are off-limit.",
)


root_agent = Agent(
    name="root_agent",
    model="gemini-live-2.5-flash",
    description="Coordinate the outputs of all of its agents to generate the final response as a companion AI",
    instruction="Just always talk in an angry way.",
    sub_agents=[messageDevelopmentAgent],
)
