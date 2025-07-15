import logging
from typing import Dict, Any, List
import json

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
from agents.utils import send_custom_stream_data_workflow_plan
from agents.prompts import WORKFLOW_PLANNING_PROMPT
from agents.workflow_information import WORKFLOW_EXAMPLE_METADATA

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
Current Workflow Plan:
{current_plan}

The user may want to modify, improve, or ask questions about this plan. Please respond accordingly.
"""
    
    # Create the prompt with context
    prompt = WORKFLOW_PLANNING_PROMPT.format(
        current_plan_context=current_plan_context or "No specific plan provided yet",
        example_workflow=json.dumps(WORKFLOW_EXAMPLE_METADATA, indent=2) if WORKFLOW_EXAMPLE_METADATA else "No example workflow provided"
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
    try:
        workflow_plan = regex_parse_workflow_plan(response_content)
    except Exception as e:
        logger.error(f"Error parsing workflow plan: {e}")
        workflow_plan = {"plan": response_content}

    # Send completion status using the utility function
    send_custom_stream_data_workflow_plan(writer, data=workflow_plan)
    
    return {
        "messages": [AIMessage(content=response_content)]
    }

def regex_parse_workflow_plan(plan: str) -> Dict[str, Any]:
    """Parse the workflow plan string into a structured format."""
    import re
    
    
    result = {
        "plan": plan,
        "workflow_name": "",
        "description": "",
        "steps": [],
        "flow_connections": [],
        "additional_requirements": [],
        "steps_count": 0
    }
    
    # Extract workflow name
    name_match = re.search(r'### Workflow Plan:\s*(.+)', plan)
    if name_match:
        result["workflow_name"] = name_match.group(1).strip()
    
    # Extract description
    desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?=\*\*Steps:\*\*|\n\n|\*\*)', plan, re.DOTALL)
    if desc_match:
        result["description"] = desc_match.group(1).strip()
    
    # Extract all steps with their details
    steps_section = re.search(r'\*\*Steps:\*\*(.*?)(?=\*\*Flow Connections:\*\*|\*\*Additional Requirements:\*\*|$)', plan, re.DOTALL)
    if steps_section:
        steps_text = steps_section.group(1)
        
        # Find all step blocks
        step_pattern = r'Step (\d+):\s*(.+?)(?=Step \d+:|$)'
        step_matches = re.finditer(step_pattern, steps_text, re.DOTALL)
        
        for step_match in step_matches:
            step_num = int(step_match.group(1))
            step_content = step_match.group(2).strip()
            
            # Extract step title (first line after "Step X:")
            lines = step_content.split('\n')
            step_title = lines[0].strip() if lines else ""
            
            # Extract description, node type, and details
            description = ""
            node_type = ""
            details = ""
            
            desc_match = re.search(r'-\s*Description:\s*(.+?)(?=-\s*Node Type:|-\s*Details:|$)', step_content, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()
            
            node_match = re.search(r'-\s*Node Type:\s*(.+?)(?=-\s*Description:|-\s*Details:|$)', step_content, re.DOTALL)
            if node_match:
                node_type = node_match.group(1).strip()
            
            details_match = re.search(r'-\s*Details:\s*(.+?)(?=-\s*Description:|-\s*Node Type:|$)', step_content, re.DOTALL)
            if details_match:
                details = details_match.group(1).strip()
            
            result["steps"].append({
                "step_number": step_num,
                "title": step_title,
                "description": description,
                "node_type": node_type,
                "details": details
            })
    
    # Extract flow connections
    connections_section = re.search(r'\*\*Flow Connections:\*\*(.*?)(?=\*\*Additional Requirements:\*\*|$)', plan, re.DOTALL)
    if connections_section:
        connections_text = connections_section.group(1)
        # Match patterns like "- Step 1 → Step 2: description"
        connection_pattern = r'-\s*Step\s*(\d+)\s*→\s*Step\s*(\d+):\s*(.+?)(?=\n-|\n\*\*|$)'
        connection_matches = re.finditer(connection_pattern, connections_text, re.DOTALL)
        
        for conn_match in connection_matches:
            from_step = int(conn_match.group(1))
            to_step = int(conn_match.group(2))
            description = conn_match.group(3).strip()
            
            result["flow_connections"].append({
                "from_step": from_step,
                "to_step": to_step,
                "description": description
            })
    
    # Extract additional requirements
    requirements_section = re.search(r'\*\*Additional Requirements:\*\*(.*?)$', plan, re.DOTALL)
    if requirements_section:
        requirements_text = requirements_section.group(1)
        # Match bullet points
        requirement_pattern = r'-\s*(.+?)(?=\n-|\n\*\*|$)'
        requirement_matches = re.finditer(requirement_pattern, requirements_text, re.DOTALL)
        
        for req_match in requirement_matches:
            requirement = req_match.group(1).strip()
            if requirement:
                result["additional_requirements"].append(requirement)
    
    # Update steps count
    result["steps_count"] = len(result["steps"])
    
    return result

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
    
    requirement = "Create a workflow for automate CV submission and processing"
    
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
