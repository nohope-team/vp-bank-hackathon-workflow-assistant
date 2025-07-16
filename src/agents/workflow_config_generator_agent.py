import logging
import json
import re
import sys
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk, BaseMessage
from langgraph.types import StreamWriter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.llm import get_model
from core.settings import settings
from agents.utils import send_custom_stream_data_workflow_config
from agents.workflow_information import WORKFLOW_EXAMPLE_METADATA

logger = logging.getLogger(__name__)

class WorkflowConfigGeneratorState(MessagesState, total=False):
    generated_config: Dict[str, Any]

# Load workflow templates from the file system
def load_workflow_templates() -> Dict[str, Dict[str, Any]]:
    """Load all workflow templates from the example_workflow directory."""
    workflow_templates = {}
    for workflow in WORKFLOW_EXAMPLE_METADATA:
        name = workflow["name"]
        description = workflow["description"]
        file_path = workflow["file_path"]
        workflow_templates[name] = {
            "name": name,
            "description": description,
            "file_path": file_path,
            "config": json.load(open(file_path, 'r')),
        }
    return workflow_templates

# Global template cache
WORKFLOW_TEMPLATES = load_workflow_templates()

WORKFLOW_CONFIG_GENERATOR_PROMPT = '''
You are an expert n8n workflow configuration generator specializing in banking and financial technology solutions. You will receive a workflow plan and a set of relevant templates, and your task is to create complete, functional n8n workflow configurations with PROPER NODE CONNECTIONS. 

Your expertise includes:
- Deep understanding of n8n node types, parameters, and connections
- Knowledge of banking/fintech workflow patterns and requirements
- Ability to adapt and combine existing workflow templates
- Creating scalable and maintainable workflow configurations
- Implementing proper error handling and data validation

Current Context:
Workflow Plan from Message: {workflow_plan}

Workflow Templates Selected: 
{selected_templates}

Current Configuration Context:
{current_config_context}

🚨🚨🚨 **ABSOLUTE CRITICAL REQUIREMENT - THIS IS MANDATORY** 🚨🚨🚨
‼️ EVERY SINGLE AI/LangChain Agent node MUST be connected to an LLM Chat Model node via `ai_languageModel` connection ‼️
🔥 NO EXCEPTIONS! The workflow will COMPLETELY FAIL without these connections! 🔥
⛔ DO NOT generate any AI/LangChain nodes without corresponding LLM model connections ⛔
🛑 This is the #1 cause of broken workflows - ALWAYS verify LLM connections 🛑

Your task is to generate a complete n8n workflow configuration JSON that:

1. **Follows the workflow plan structure** - Implement all steps and logic from the plan
2. **Leverages suitable templates** - Adapt nodes and patterns from matching templates
3. **Maintains n8n best practices** - Proper node configuration, connections, and data flow
4. **Includes banking/fintech specifics** - Security, compliance, error handling
5. **Generates working configuration** - Valid JSON that can be imported into n8n
6. **🔥 ENSURES ALL AI NODES HAVE LLM CONNECTIONS** - This is MANDATORY for workflow functionality

**🚨 MANDATORY AI/LANGCHAIN CONNECTION RULES (NO EXCEPTIONS):**

**🔴 CRITICAL ERROR TO AVOID: AI Nodes Without LLM Connections 🔴**
The most common workflow generation error is creating AI/LangChain nodes (like informationExtractor, chainLlm) without connecting them to LLM Chat Model nodes. This causes the workflow to completely fail during execution.

**✅ REQUIRED PATTERN FOR EVERY AI NODE:**
1. Create an LLM Chat Model node (e.g., Google Gemini Chat Model)
2. Create your AI/LangChain node (e.g., CV Information Extractor)  
3. Connect the LLM model TO the AI node using `ai_languageModel` connection type
4. Verify the connection exists in the `connections` section

**Rule 1: Every AI Agent/Chain Node REQUIRES an LLM Model Connection**
- **Agent/Chain Nodes that REQUIRE LLM connections:**
  - `@n8n/n8n-nodes-langchain.chainLlm`
  - `@n8n/n8n-nodes-langchain.informationExtractor`
  - `@n8n/n8n-nodes-langchain.chainSummarization`
  - `@n8n/n8n-nodes-langchain.agent`
  - Any other `@n8n/n8n-nodes-langchain.*` node that processes text with AI

**Rule 2: LLM Chat Model Nodes You MUST Include:**
- `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` (recommended)
- `@n8n/n8n-nodes-langchain.lmChatOpenAi` (alternative)
- These connect TO Agent/Chain nodes via `ai_languageModel` connection type

**Rule 3: Connection Pattern - FOLLOW THIS EXACTLY:**
```json
"connections": {{
  "LLM_CHAT_MODEL_NODE_NAME": {{
    "ai_languageModel": [
      [
        {{
          "node": "AGENT_OR_CHAIN_NODE_NAME",
          "type": "ai_languageModel", 
          "index": 0
        }}
      ]
    ]
  }}
}}
```

**🔥 COMPLETE WORKING EXAMPLE - USE THIS AS REFERENCE:**
```json
{{
  "name": "CV Analysis Workflow",
  "nodes": [
    {{
      "name": "Form Trigger",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2.2,
      "position": [300, 300]
    }},
    {{
      "name": "Google Gemini Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "typeVersion": 1,
      "position": [500, 200],
      "parameters": {{
        "modelName": "models/gemini-2.5-flash",
        "options": {{}}
      }}
    }},
    {{
      "name": "CV Information Extractor",
      "type": "@n8n/n8n-nodes-langchain.informationExtractor",
      "typeVersion": 1,
      "position": [700, 300],
      "parameters": {{
        "text": "={{{{ $json.cv_content }}}}",
        "attributes": {{
          "attributes": [
            {{"name": "name", "description": "Candidate's full name"}},
            {{"name": "email", "description": "Contact email"}},
            {{"name": "skills", "description": "Technical skills"}}
          ]
        }}
      }}
    }},
    {{
      "name": "Save to Database",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.4,
      "position": [900, 300]
    }}
  ],
  "connections": {{
    "Form Trigger": {{
      "main": [
        [
          {{
            "node": "CV Information Extractor",
            "type": "main",
            "index": 0
          }}
        ]
      ]
    }},
    "Google Gemini Chat Model": {{
      "ai_languageModel": [
        [
          {{
            "node": "CV Information Extractor",
            "type": "ai_languageModel",
            "index": 0
          }}
        ]
      ]
    }},
    "CV Information Extractor": {{
      "main": [
        [
          {{
            "node": "Save to Database",
            "type": "main",
            "index": 0
          }}
        ]
      ]
    }}
  }}
}}
```

**❌ WHAT WILL BREAK THE WORKFLOW:**
- Missing `ai_languageModel` connections from LLM models to AI agents
- AI agents without any LLM model connected
- Wrong connection types (using "main" instead of "ai_languageModel")
- Missing LLM Chat Model nodes entirely

**✅ MANDATORY VALIDATION CHECKLIST - CHECK EVERY SINGLE ITEM:**
🔍 **BEFORE generating the workflow, VERIFY these requirements:**
1. ✅ Count AI/LangChain nodes: Every `@n8n/n8n-nodes-langchain.*` agent/chain node has a corresponding LLM model node
2. ✅ Verify LLM connections: Every LLM model node has `ai_languageModel` connection to its agent/chain node
3. ✅ Check connection names: Connection names match node names exactly (case-sensitive)
4. ✅ Validate connection types: All connections use correct types: `ai_languageModel`, `ai_outputParser`, `main`
5. ✅ No orphaned nodes: No AI agent nodes exist without LLM connections
6. ✅ Required LLM models: At least one `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` or `@n8n/n8n-nodes-langchain.lmChatOpenAi` node exists if any AI agents are present

**🚨 DOUBLE-CHECK: If you create ANY of these nodes, you MUST create an LLM model and connection:**
- `@n8n/n8n-nodes-langchain.chainLlm` ➜ REQUIRES LLM MODEL CONNECTION
- `@n8n/n8n-nodes-langchain.informationExtractor` ➜ REQUIRES LLM MODEL CONNECTION  
- `@n8n/n8n-nodes-langchain.chainSummarization` ➜ REQUIRES LLM MODEL CONNECTION
- `@n8n/n8n-nodes-langchain.agentExecutor` ➜ REQUIRES LLM MODEL CONNECTION
- ANY `@n8n/n8n-nodes-langchain.*` node that processes text ➜ REQUIRES LLM MODEL CONNECTION

**N8N Workflow Structure:**
```json
{{
  "name": "Workflow Name",
  "meta": {{
    "description": "Workflow description"
  }},
  "nodes": [
    {{
      "name": "Node Name",
      "type": "node-type",
      "typeVersion": 1.0,
      "position": [x, y],
      "parameters": {{}},
      "credentials": {{}}
    }}
  ],
  "connections": {{}},
  "pinData": {{}},
  "settings": {{
    "executionOrder": "v1"
  }},
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "updatedAt": "2025-01-09T12:00:00.000Z",
  "versionId": "1"
}}
```

**Common n8n Node Types:**
- **Triggers**: `n8n-nodes-base.manualTrigger`, `n8n-nodes-base.webhook`, `n8n-nodes-base.formTrigger`
- **Data Processing**: `n8n-nodes-base.set`, `n8n-nodes-base.function`, `n8n-nodes-base.code`, `n8n-nodes-base.merge`
- **Logic**: `n8n-nodes-base.if`, `n8n-nodes-base.switch`, `n8n-nodes-base.stopAndError`
- **External APIs**: `n8n-nodes-base.httpRequest`
- **AI/LangChain**: `@n8n/n8n-nodes-langchain.chainLlm`, `@n8n/n8n-nodes-langchain.informationExtractor`
- **LLM Model**: `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`
- **Databases**: `n8n-nodes-base.postgres`, `n8n-nodes-base.mysql`
- **Communication**: `n8n-nodes-base.emailSend`, `n8n-nodes-base.slack`
- **File Operations**: `n8n-nodes-base.extractFromFile`, `n8n-nodes-base.googleDrive`

**Template Adaptation Guidelines:**
1. **Node Reuse**: Adapt node configurations from templates that match workflow steps
2. **Connection Patterns**: Follow data flow patterns from similar templates 
3. **AI Node Dependencies**: ALWAYS ensure AI/LangChain nodes have proper LLM model connections
4. **Parameter Mapping**: Map workflow plan requirements to template node parameters
5. **Credential Management**: Include proper credential configurations
6. **Position Layout**: Organize nodes in a logical visual flow

**MANDATORY REQUIREMENTS - READ BEFORE GENERATING:**
🔥 **CRITICAL**: Every `@n8n/n8n-nodes-langchain.chainLlm` and `@n8n/n8n-nodes-langchain.informationExtractor` node MUST have a connection to LLM Model (`@n8n/n8n-nodes-langchain.lmChatGoogleGemini`) connected via `ai_languageModel`
🔥 **CRITICAL**: Output parsers MUST connect to their target chain nodes via `ai_outputParser`  
🔥 **CRITICAL**: Main data flow connections use `"type": "main"`
🔥 **CRITICAL**: Never create AI/LangChain nodes without corresponding LLM model connections

**🚨 FINAL REMINDER BEFORE GENERATION:**
- AI nodes without LLM connections = BROKEN WORKFLOW
- Missing `ai_languageModel` connections = EXECUTION FAILURE
- Always create LLM Chat Model nodes for every AI agent
- Verify connections section includes all AI-to-LLM relationships

When generating the configuration:
- Provide working JSON that follows n8n standards
- Explain each part of the configuration
- Respond the config in a code block with `json` syntax highlighting
- VERIFY all AI/LangChain nodes have proper LLM model connections
- Include complete connections section with all node dependencies
'''
from langchain_openai import AzureChatOpenAI, ChatOpenAI

async def workflow_config_generator(state: WorkflowConfigGeneratorState, config: RunnableConfig, writer: StreamWriter) -> WorkflowConfigGeneratorState:
    """Generate n8n workflow configuration based on plans and templates."""
    
    llm = ChatOpenAI(
        # model_name="o4-mini",
        model_name="gpt-4o-mini",
        temperature=0,
        streaming=True,
    )
    
    # Get metadata from config if available (from service)
    workflow_plan = config["metadata"].get("workflow_plan", "")
    current_config = config["metadata"].get("workflow_config", {})
    # If this is the first interaction, analyze templates and extract plan
    
    selected_templates = await suggest_relevant_templates_with_llm(workflow_plan)
    
    # Create the prompt with context
    prompt = WORKFLOW_CONFIG_GENERATOR_PROMPT.format(
        workflow_plan=workflow_plan if len(workflow_plan) > 0 else "No specific workflow plan provided yet",
        selected_templates=json.dumps(selected_templates, indent=2) if selected_templates else "No templates selected",
        current_config_context=json.dumps(current_config, indent=2) if len(current_config) > 0 else "No current configuration context provided"
    )
    
    # Prepare messages for the LLM
    input_messages = [{"role": "system", "content": prompt}]
    input_messages += [{"role": "user", "content": "Generate the configuration for me based on the provided plan and templates."}]
    # input_messages += [i for i in state.get("messages", []) if i.type == "human" or i.type == "ai"]
    
    # Add the latest user message
    
    # Stream the response

    stream = llm.astream(input=input_messages)
    
    response_parts = []
    async for chunk in stream:
        response_parts.append(chunk.content)
    
    response_content = "".join(response_parts)
    
    # Try to extract generated configuration from response
    updated_config = current_config
    if "```json" in response_content or "{" in response_content:
        updated_config = extract_json_config_from_response(response_content)
        if not updated_config:
            updated_config = current_config
    # Limit the config to only the nodes and connections
    updated_config = {
        "name": updated_config.get("name", "Generated Workflow"),
        "nodes": updated_config.get("nodes", []),
        "connections": updated_config.get("connections", {}),
        "settings": updated_config.get("settings", {}),
        "staticData": updated_config.get("staticData", {}),
    }
        
    send_custom_stream_data_workflow_config(
        writer,
        data=updated_config
    )
    
    # Send completion status
    return {
        "messages": [AIMessage(content=response_content)],
        "generated_config": updated_config,
    }


async def suggest_relevant_templates_with_llm(workflow_plan: str) -> dict[str, Any]:
    """Use LLM to suggest relevant templates based on workflow plan and metadata."""
    # Build comprehensive template descriptions using both metadata and analysis
    return WORKFLOW_TEMPLATES


def extract_json_config_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON configuration from the LLM response."""
    
    # Try to find JSON code blocks
    json_patterns = [
        r"```json\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
        r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",
    ]
    
    for pattern in json_patterns:
        matches = re.finditer(pattern, response, re.DOTALL)
        for match in matches:
            try:
                json_str = match.group(1) if "```" in pattern else match.group(0)
                # Clean up the JSON string
                json_str = json_str.strip()
                parsed = json.loads(json_str)
                # Validate it looks like an n8n workflow
                if isinstance(parsed, dict) and ("nodes" in parsed or "name" in parsed):
                    return parsed
            except (json.JSONDecodeError, AttributeError) as e:
                logger.debug(f"Failed to parse JSON from match: {e}")
                continue
    
    return {}


def build_workflow():
    """Build the workflow config generator state graph with conversation support."""
    
    graph = StateGraph(WorkflowConfigGeneratorState)
    
    graph.add_node("config_generation", workflow_config_generator)
    
    graph.set_entry_point("config_generation")
    graph.set_finish_point("config_generation")
    
    return graph.compile(
        name="workflow-config-generator",
        checkpointer=MemorySaver(),
        store=InMemoryStore()
    )

async def test_conversational_message():
    """Test with a conversational message containing embedded workflow plan."""
    
    workflow = build_workflow()
    
    conversational_message = """To create a workflow for automating CV submission and processing, we need to consider several key steps. Here’s a proposed outline for the workflow:

### Workflow Name: Automated CV Submission and Processing

#### Description:
This workflow automates the process of receiving CV submissions, extracting relevant information, evaluating candidates, and storing the results for review. It will streamline the hiring process and ensure that all submissions are handled efficiently.

#### Steps:

1. **Trigger Node: CV Submission**
   - **Type:** Trigger on a webhook
   - **Description:** This node will listen for incoming CV submissions via a webhook. When a CV is submitted, it will trigger the workflow.

2. **Data Collection: Extract CV Data**
   - **Node Type:** Extract from File
   - **Description:** This node will extract data from the uploaded CV file (PDF/DOC). It will parse the document to retrieve relevant information such as name, contact details, education, work experience, and skills.

3. **Data Processing: Analyze Candidate Information**
   - **Node Type:** Function or AI Agent
   - **Description:** This node will process the extracted data. It can use an AI model to evaluate the candidate's qualifications against a predefined job profile. It will generate a matching score and provide insights into the candidate's strengths and weaknesses.

4. **Data Storage: Save Results**
   - **Node Type:** Google Sheets or Database
   - **Description:** This node will append the processed data, including the candidate's information and evaluation results, to a Google Sheets document or a database for further review.

5. **Notification: Inform HR Team**
   - **Node Type:** Email or Slack Notification
   - **Description:** This node will send a notification to the HR team with a summary of the candidate's evaluation and a link to the stored data for their review.

6. **Optional: Follow-Up Actions**
   - **Node Type:** Conditional Node
   - **Description:** Based on the evaluation score, you can set up conditions to trigger follow-up actions, such as scheduling an interview for high-scoring candidates or sending a rejection email for those who do not meet the criteria.

### Questions for Clarification:
- What specific data points do you want to extract from the CVs?
- Do you have a preferred method for evaluating candidates (e.g., specific scoring criteria)?
- Would you like to use any specific tools or services for notifications (e.g., email, Slack)?
- Are there any additional steps or features you would like to include in this workflow?

Feel free to provide feedback or modifications, and we can refine this workflow further!"""
    
    print(f"\n{'='*60}")
    print("Testing Conversational Message with Embedded Workflow Plan")
    print(f"{'='*60}")
    
    # conversational_message = "Create a simple chatbot that can answer questions about loan applications and provide status updates."
    # Test plan extraction first
    
    state = WorkflowConfigGeneratorState(
        messages=[HumanMessage(content="")],
    )
    
    try:
        async for update in workflow.astream(state, stream_mode=["messages", "updates", "custom"], config=RunnableConfig(thread_id="0", metadata={"workflow_plan": conversational_message})):
            mode, event = update
            if mode == "messages":
                message, metadata = event
                if "skip_stream" in metadata.get("tags", []):
                    continue
                if isinstance(message, AIMessageChunk):
                    print(message.content, end="", flush=True)
            elif mode == "custom":
                if isinstance(event, dict) and event.get("role") == "workflow_config":
                    print(f"\n✅ Workflow config generation completed!")
                    print(f"Generated config: {json.dumps(event.get('generated_config', {}), indent=2)}")
            elif mode == "updates":
                if isinstance(event, dict) and "generated_config" in event and event["generated_config"]:
                    config = event["generated_config"]
                    print(f"\n📋 Generated config preview:")
                    print(f"   Name: {config.get('name', 'Unknown')}")
                    print(f"   Nodes: {len(config.get('nodes', []))}")
                    print(f"   Connections: {len(config.get('connections', {}))}")
            
    except Exception as e:
        import traceback
        print(f"❌ Error testing conversational message: {e}")
        print("Full traceback:")
        traceback.print_exc()

# Create the workflow config generator agent
workflow_config_generator_agent = build_workflow()

if __name__ == "__main__":
    import asyncio
    
    asyncio.run(test_conversational_message())
