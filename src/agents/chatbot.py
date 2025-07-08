from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import MessagesState, add_messages
from typing import Annotated

from core import get_model, settings

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

def math_calculation(a: int, b: int) -> str:
    """Perform a simple math calculation."""
    return f"The result of {a} + {b} is {a + b}."

class CustomState(MessagesState, total=False):
    """Custom state schema for the agent."""
    messages: Annotated[list[BaseMessage], add_messages]  # List of messages in the conversation
    tools_used: list[str] = []  # List of tools used in the conversation
    remaining_steps: int = 3  # Number of steps remaining in the conversation
    
agent = create_react_agent(
    model=get_model(settings.DEFAULT_MODEL),
    tools=[get_weather, math_calculation],
    prompt="You are a helpful assistant. You can use 2 tools: `get_weather(city: str)` to get the weather of a city, and `math_calculation(a: int, b: int)` to perform a simple math calculation. Use these tools when necessary.",
    checkpointer=MemorySaver(),
    store=InMemoryStore(),
    state_schema=CustomState,
)

