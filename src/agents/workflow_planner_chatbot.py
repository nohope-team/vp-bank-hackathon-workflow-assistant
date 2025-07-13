import logging
from typing import Dict, Any, List

from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk, BaseMessage
from langgraph.types import StreamWriter
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from core.llm import get_model
from core.settings import settings
from agents.utils import send_custom_stream_data
from agents.prompts import WORKFLOW_PLANNING_PROMPT

logger = logging.getLogger(__name__)

class WorkflowPlannerState(MessagesState, total=False):
    ...  # List of messages including user and assistant



async def workflow_planning(state: WorkflowPlannerState, config: RunnableConfig, writer: StreamWriter) -> WorkflowPlannerState:
    """Interactive workflow planning that responds to user messages and refines plans."""
    
    llm = get_model(settings.DEFAULT_MODEL)
    # Initialize state variables if not present
    current_plan = config["metadata"].get("current_workflow_config", "")
    
    # Build conversation context
    current_plan_context = ""
    if current_plan:
        current_plan_context = f"""
Current Workflow Configuration:
{current_plan}

The user may want to modify, improve, or ask questions about this plan. Please respond accordingly.
"""
    
    # Create the prompt with context
    prompt = WORKFLOW_PLANNING_PROMPT.format(
        current_plan_context=current_plan_context or "No specific plan provided yet"
    )
    
    # Prepare messages for the LLM
    input_messages = [{"role": "system", "content": prompt}]
    
    # Add the latest user message
    input_messages = input_messages + [i for i in state["messages"] if i.type != "tool"]
    
    # Stream the response
    stream = llm.astream(input=input_messages)
    
    response_parts = []
    async for chunk in stream:
        response_parts.append(chunk.content)
    
    response_content = "".join(response_parts)
    
    # Send completion status using the utility function
    return {
        "messages": [AIMessage(content=response_content)]
    }


def build_workflow():
    """Build the workflow planner state graph with conversation support."""
    
    graph = StateGraph(WorkflowPlannerState)
    
    graph.add_node("planning", workflow_planning)
    
    graph.set_entry_point("planning")
    graph.set_finish_point("planning")  # End after each response, caller can continue conversation
    
    return graph.compile(
        name="workflow-planner-chatbot",
        checkpointer=MemorySaver(),
        store=InMemoryStore()# No checkpointing needed for interactive chatbot
        
    )
    
async def test_single_requirement():
    """Test with a single requirement like the original version."""
    
    workflow = build_workflow()
    
    requirement = "Create a workflow that can read received CV and save the base information to a sheet"
    
    print(f"\n{'='*60}")
    print(f"Testing Single Requirement: {requirement}")
    print(f"{'='*60}")
    
    state = WorkflowPlannerState(
        messages=[HumanMessage(content=requirement)],
    )
    
    try:
        async for update in workflow.astream(state, stream_mode=["messages", "updates", "custom"], config=RunnableConfig(thread_id="0")):
            mode, event = update
            if mode == "messages":
                message, metadata = event
                if "skip_stream" in metadata.get("tags", []):
                    continue
                if isinstance(message, AIMessageChunk):
                    print(message.content, end="", flush=True)
            elif mode == "custom":
                if event.get("type") == "workflow_planning_complete":
                    data = event.get("data", {})
                    print(f"\n✅ Workflow planning completed!")
                    print(f"📊 Generated plan with {data.get('steps_count', 0)} steps")
            
    except Exception as e:
        print(f"❌ Error testing single requirement: {e}")

# Create the workflow planner agent
workflow_planner_chatbot_agent = build_workflow()

if __name__ == "__main__":
    import asyncio
    
    asyncio.run(test_single_requirement())
