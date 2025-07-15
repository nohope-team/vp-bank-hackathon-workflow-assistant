from dataclasses import dataclass

from langgraph.pregel import Pregel

from agents.chatbot import agent as chatbot
from agents.workflow_planner_chatbot import workflow_planner_chatbot_agent
from agents.workflow_explain_chatbot import workflow_explain_chatbot_agent
from agents.workflow_config_generator_agent import workflow_config_generator_agent
from schema import AgentInfo

DEFAULT_AGENT = "simple_chatbot"


@dataclass
class Agent:
    description: str
    graph: Pregel


agents: dict[str, Agent] = {
    "simple_chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    "workflow_planner_chatbot": Agent(
        description="An interactive AI workflow designer that can chat with users to refine and improve banking/fintech workflow plans through conversation.",
        graph=workflow_planner_chatbot_agent
    ),
    "workflow_explain_chatbot": Agent(
        description="An interactive AI assistant that analyzes n8n workflow configurations and explains their components, data flow, and business logic through conversation.",
        graph=workflow_explain_chatbot_agent
    ),
    "workflow_config_generator": Agent(
        description="An intelligent n8n workflow configuration generator that combines workflow plans with existing templates to create complete, working n8n workflow JSON configurations for banking/fintech applications.",
        graph=workflow_config_generator_agent
    ),
}


def get_agent(agent_id: str) -> Pregel:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
