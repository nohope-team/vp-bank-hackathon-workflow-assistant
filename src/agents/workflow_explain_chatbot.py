import logging
import json
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk, BaseMessage
from langgraph.types import StreamWriter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from core.llm import get_model
from core.settings import settings
from agents.utils import send_custom_stream_data
from agents.prompts import WORKFLOW_EXPLAIN_PROMPT

logger = logging.getLogger(__name__)

class WorkflowExplainState(MessagesState, total=False):
    ...  # Inherits from MessagesState to manage conversation history
    


async def workflow_explanation(state: WorkflowExplainState, config: RunnableConfig, writer: StreamWriter) -> WorkflowExplainState:
    """Interactive workflow explanation that responds to user questions about the workflow."""
    
    llm = get_model(settings.DEFAULT_MODEL)
    
    # Initialize state variables
    workflow_config = config["metadata"].get("workflow_config", {})
    
    # Create the prompt with context
    prompt = WORKFLOW_EXPLAIN_PROMPT.format(
        workflow_analysis=json.dumps(workflow_config, indent=2),
    )
    
    # Prepare messages for the LLM
    input_messages = [{"role": "system", "content": prompt}]
    input_messages += [i for i in state.get("messages", []) if i.type == "human" or i.type == "ai"]
    
    # Stream the response
    stream = llm.astream(input=input_messages)
    
    response_parts = []
    async for chunk in stream:
        response_parts.append(chunk.content)
    
    response_content = "".join(response_parts)
    
    # Update conversation history
    return {
        "messages": [AIMessage(content=response_content)]
    }

def build_workflow():
    """Build the workflow explanation state graph with conversation support."""
    
    graph = StateGraph(WorkflowExplainState)
    
    graph.add_node("explanation", workflow_explanation)
    
    graph.set_entry_point("explanation")
    graph.set_finish_point("explanation")
    
    return graph.compile(
        name="workflow-explain-chatbot",
        checkpointer=MemorySaver(),
        store=InMemoryStore()
    )

# Example usage and testing
async def test_workflow_explanation_chatbot():
    """Test the workflow explanation chatbot with sample n8n configuration."""
    
    workflow = build_workflow()
    
    # Sample n8n workflow configuration
    sample_config = json.load(open("../example_workflow/Email.json", "r"))
    sample_config = json.loads(json.dumps(sample_config))  # Ensure it's a proper dict
    # Simulate a conversation about the workflow
    conversation_messages = [
        "Please explain this workflow configuration",
        "What are the trigger points in this workflow?",
    ]
    
    print(f"\n{'='*60}")
    print("Testing Workflow Explanation Chatbot")
    print(f"{'='*60}")
    
    # Initialize conversation state with the workflow config
    state = WorkflowExplainState(
        messages=[],
    )
    
    for i, user_message in enumerate(conversation_messages):
        print(f"\n👤 User (Message {i+1}): {user_message}")
        print("-" * 50)
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        try:
            # Process one iteration of the conversation
            async for update in workflow.astream(state, stream_mode=["messages", "updates"], config=RunnableConfig(thread_id="0", metadata={"workflow_config": sample_config})):
                mode, event = update
                if mode == "messages":
                    message, metadata = event
                    if "skip_stream" in metadata.get("tags", []):
                        continue
                    if isinstance(message, AIMessageChunk):
                        print(message.content, end="", flush=True)
                    elif message.type == "ai":
                        print(message.content)
                elif mode == "updates":
                    # Update our state with the new values
                    for key, value in event.items():
                        if key in state:
                            state[key] = value
                
        except Exception as e:
            import traceback
            print(f"❌ Error in conversation turn {i+1}: {e}")
            traceback.print_exc()            
            break
        
        print("\n")  # Add spacing between responses

async def test_with_custom_config():
    """Test with a custom workflow configuration provided by user."""
    
    workflow = build_workflow()
    
    print("Enter your n8n workflow JSON configuration (or press Enter for sample):")
    config_input = input().strip()
    
    if not config_input:
        # Use a simple sample
        sample_config = {
            "name": "Simple API Workflow",
            "nodes": [
                {"name": "Start", "type": "manual", "position": [100, 100]},
                {"name": "API Call", "type": "httpRequest", "position": [300, 100], 
                 "parameters": {"method": "GET", "url": "https://api.example.com/data"}}
            ],
            "connections": {
                "Start": [[{"node": "API Call", "type": "main", "index": 0}]]
            }
        }
        config_input = json.dumps(sample_config)
    
    try:
        workflow_config = json.loads(config_input)
    except json.JSONDecodeError:
        print("❌ Invalid JSON configuration provided")
        return
    
    state = WorkflowExplainState(
        messages=[HumanMessage(content="Please explain this workflow")],
        workflow_config=workflow_config,
        workflow_analysis={},
        conversation_history=[],
        current_iteration=0
    )
    
    print(f"\n{'='*60}")
    print("Analyzing Your Workflow Configuration")
    print(f"{'='*60}")
    
    try:
        async for update in workflow.astream(state, stream_mode=["messages"], config=RunnableConfig(thread_id="0")):
            mode, event = update
            if mode == "messages":
                message, metadata = event
                if isinstance(message, AIMessageChunk):
                    print(message.content, end="", flush=True)
                elif message.type == "ai":
                    print(message.content)
                    
    except Exception as e:
        print(f"❌ Error analyzing workflow: {e}")

# Create the workflow explanation agent
workflow_explain_chatbot_agent = build_workflow()

if __name__ == "__main__":
    import asyncio
    
    print("Choose test mode:")
    print("1. Interactive Chatbot Test (with sample workflow)")
    print("2. Custom Workflow Configuration Test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_workflow_explanation_chatbot())
    else:
        asyncio.run(test_with_custom_config())
