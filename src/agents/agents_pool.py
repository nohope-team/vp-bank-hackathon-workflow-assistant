from dataclasses import dataclass

from langgraph.pregel import Pregel

from agents.chatbot import agent as chatbot
# from agents.workflow_planner_chatbot import workflow_planner_chatbot_agent
from agents.workflow_explain_chatbot import workflow_explain_chatbot_agent
# from agents.n8n_config_generator_agent import n8n_config_generator_agent
from schema import AgentInfo

DEFAULT_AGENT = "simple_chatbot"


@dataclass
class Agent:
    description: str
    graph: Pregel


agents: dict[str, Agent] = {
    "simple_chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    # "workflow_planner_chatbot": Agent(
    #     description="An interactive AI workflow designer that can chat with users to refine and improve banking/fintech workflow plans through conversation.",
    #     graph=workflow_planner_chatbot_agent
    # ),
    "workflow_explain_chatbot": Agent(
        description="An interactive AI assistant that analyzes n8n workflow configurations and explains their components, data flow, and business logic through conversation.",
        graph=workflow_explain_chatbot_agent
    ),
    # "n8n_config_generator": Agent(
    #     description="An AI agent that converts workflow plans into complete n8n workflow JSON configurations ready for import.",
    #     graph=n8n_config_generator_agent
    # ),
}


def get_agent(agent_id: str) -> Pregel:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
