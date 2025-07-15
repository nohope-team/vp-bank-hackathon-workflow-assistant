import uuid
from typing import Any, Literal, NotRequired, List, Dict

from pydantic import BaseModel, Field, SerializeAsAny
from typing_extensions import TypedDict

from schema.models import AllModelEnum, AnthropicModelName, OpenAIModelName


class AgentInfo(BaseModel):
    """Info about an available agent."""

    key: str = Field(
        description="Agent key.",
        examples=["research-assistant"],
    )
    description: str = Field(
        description="Description of the agent.",
        examples=["A research assistant for generating research papers."],
    )


class ServiceMetadata(BaseModel):
    """Metadata about the service including available agents and models."""

    agents: list[AgentInfo] = Field(
        description="List of available agents.",
    )
    models: list[AllModelEnum] = Field(
        description="List of available LLMs.",
    )
    default_agent: str = Field(
        description="Default agent used when none is specified.",
        examples=["research-assistant"],
    )
    default_model: AllModelEnum = Field(
        description="Default model used when none is specified.",
    )


class UserInput(BaseModel):
    """Basic user input for the agent."""

    message: str = Field(
        description="User input to the agent.",
        examples=[""],
    )
    model: SerializeAsAny[AllModelEnum] | None = Field(
        title="Model",
        description="LLM Model to use for the agent.",
        default=OpenAIModelName.GPT_4O_MINI,
        examples=[OpenAIModelName.GPT_4O_MINI, AnthropicModelName.HAIKU_35],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=[str(uuid.uuid4())],
    )
    user_id: str | None = Field(
        description="User ID to persist and continue a conversation across multiple threads.",
        default=None,
        examples=[str(uuid.uuid4())],
    )
    agent_config: dict[str, Any] = Field(
        description="Additional configuration to pass through to the agent",
        default={},
        examples=[{"spicy_level": 0.8}],
    )
    
    # Whether to stream LLM tokens to the client.
    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )

class StreamInput(UserInput):
    """Input for streaming responses from the agent."""
    
    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )

class UserInputSelectFeatureAgent(UserInput):
    """User input for selecting features in the agent."""

    category_config: dict[str, Any] = Field(
        description="Product configuration to pass through to the agent",
        default={},
        examples=[{"category_id": "CreditCard"}],
    )

class UserInputExplainWorkflowAgent(UserInput):
    """User input for explaining a model in the agent."""
    message: str = Field(
        description="User input to the agent.",
        examples=["Please explain this workflow configuration."],
    )
    
    workflow_json_data: dict[str, Any] = Field(
        description="Configuration of the workflow.",
        default={},
        examples=[
            {"workflow_config": {
                "name": "Contact",
                "nodes": [
                    {
                    "parameters": {
                        "operation": "search",
                        "base": {
                        "__rl": True,
                        "value": "appo9AT6RTEL9HCen",
                        "mode": "list",
                        "cachedResultName": "Base",
                        "cachedResultUrl": "https://airtable.com/appo9AT6RTEL9HCen"
                        },
                        "table": {
                        "__rl": True,
                        "value": "tblNH2z0sIttxM8lX",
                        "mode": "list",
                        "cachedResultName": "Table 1",
                        "cachedResultUrl": "https://airtable.com/appo9AT6RTEL9HCen/tblNH2z0sIttxM8lX"
                        },
                        "filterByFormula": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Filter_By_Formula', ``, 'string') }}",
                        "returnAll": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Return_All', ``, 'boolean') }}",
                        "options": {}
                    },
                    "type": "n8n-nodes-base.airtableTool",
                    "typeVersion": 2.1,
                    "position": [
                        -360,
                        380
                    ],
                    "id": "6b6adeaf-9dbe-4aa6-9ff5-73bf58759f63",
                    "name": "Get Contacts",
                    "credentials": {
                        "airtableTokenApi": {
                        "id": "G4nDJh2BzQ7papIj",
                        "name": "Airtable Personal Access Token account 2"
                        }
                    }
                    },
                    {
                    "parameters": {
                        "operation": "upsert",
                        "base": {
                        "__rl": True,
                        "value": "appo9AT6RTEL9HCen",
                        "mode": "list",
                        "cachedResultName": "Base",
                        "cachedResultUrl": "https://airtable.com/appo9AT6RTEL9HCen"
                        },
                        "table": {
                        "__rl": True,
                        "value": "tblNH2z0sIttxM8lX",
                        "mode": "list",
                        "cachedResultName": "Table 1",
                        "cachedResultUrl": "https://airtable.com/appo9AT6RTEL9HCen/tblNH2z0sIttxM8lX"
                        },
                        "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "name": "={{ $fromAI(\"name\") }}",
                            "email": "={{ $fromAI(\"emailAddress\") }}",
                            "phoneNumber": "={{ $fromAI(\"phoneNumber\") }}"
                        },
                        "matchingColumns": [
                            "name"
                        ],
                        "schema": [
                            {
                            "id": "id",
                            "displayName": "id",
                            "required": False,
                            "defaultMatch": True,
                            "display": True,
                            "type": "string",
                            "readOnly": True,
                            "removed": False
                            },
                            {
                            "id": "name",
                            "displayName": "name",
                            "required": False,
                            "defaultMatch": False,
                            "canBeUsedToMatch": True,
                            "display": True,
                            "type": "string",
                            "readOnly": False,
                            "removed": False
                            },
                            {
                            "id": "email",
                            "displayName": "email",
                            "required": False,
                            "defaultMatch": False,
                            "canBeUsedToMatch": True,
                            "display": True,
                            "type": "string",
                            "readOnly": False,
                            "removed": False
                            },
                            {
                            "id": "phoneNumber",
                            "displayName": "phoneNumber",
                            "required": False,
                            "defaultMatch": False,
                            "canBeUsedToMatch": True,
                            "display": True,
                            "type": "string",
                            "readOnly": False,
                            "removed": False
                            }
                        ],
                        "attemptToConvertTypes": False,
                        "convertFieldsToString": False
                        },
                        "options": {}
                    },
                    "type": "n8n-nodes-base.airtableTool",
                    "typeVersion": 2.1,
                    "position": [
                        -220,
                        360
                    ],
                    "id": "052ea1f7-bdff-4955-b8f1-d887b13e36ad",
                    "name": "Add or Update Contact",
                    "credentials": {
                        "airtableTokenApi": {
                        "id": "G4nDJh2BzQ7papIj",
                        "name": "Airtable Personal Access Token account 2"
                        }
                    }
                    },
                    {
                    "parameters": {
                        "assignments": {
                        "assignments": [
                            {
                            "id": "4f360190-a717-4a93-8336-d03ea65975d5",
                            "name": "response",
                            "value": "={{ $json.output }}",
                            "type": "string"
                            }
                        ]
                        },
                        "options": {}
                    },
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 3.4,
                    "position": [
                        0,
                        0
                    ],
                    "id": "29602472-e6cc-4aea-805e-4a090c3de8dc",
                    "name": "Response"
                    },
                    {
                    "parameters": {
                        "assignments": {
                        "assignments": [
                            {
                            "id": "4f360190-a717-4a93-8336-d03ea65975d5",
                            "name": "response",
                            "value": "An error occurred. Please try again.",
                            "type": "string"
                            }
                        ]
                        },
                        "options": {}
                    },
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 3.4,
                    "position": [
                        0,
                        180
                    ],
                    "id": "e59c1ef2-4f4b-4d9f-b3c1-c660c972b0b8",
                    "name": "Try Again2"
                    },
                    {
                    "parameters": {
                        "modelName": "models/gemini-2.5-flash",
                        "options": {}
                    },
                    "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
                    "typeVersion": 1,
                    "position": [
                        -600,
                        340
                    ],
                    "id": "64571bbf-36cc-4136-8def-062fff567dfe",
                    "name": "Google Gemini Chat Model1",
                    "credentials": {
                        "googlePalmApi": {
                        "id": "mOHwaPE68rRhYNI2",
                        "name": "Google Gemini(PaLM) Api account"
                        }
                    }
                    },
                    {
                    "parameters": {
                        "workflowInputs": {
                        "values": [
                            {
                            "name": "query"
                            }
                        ]
                        }
                    },
                    "type": "n8n-nodes-base.executeWorkflowTrigger",
                    "typeVersion": 1.1,
                    "position": [
                        -760,
                        80
                    ],
                    "id": "dd66f8b0-c2d1-41db-a8c0-5a0d78d92a60",
                    "name": "When Executed by Another Workflow"
                    },
                    {
                    "parameters": {
                        "promptType": "define",
                        "text": "={{ $json.query }}",
                        "options": {
                        "systemMessage": "=# Overview\nYou are a contact management assistant. Your responsibilities include looking up contacts, adding new contacts, or updating a contact's information.\n\n**Contact Management**  \n   - Use \"Get Contacts\" to retrieve contact information. \n   - Use \"Add or Update Contact\" to store new contact information or modify existing entries. "
                        }
                    },
                    "type": "@n8n/n8n-nodes-langchain.agent",
                    "typeVersion": 1.7,
                    "position": [
                        -520,
                        80
                    ],
                    "id": "26b9ee19-b881-4b80-a98d-dc4ae8dfb9f5",
                    "name": "Contact Agent2",
                    "onError": "continueErrorOutput"
                    }
                ],
                "pinData": {},
                "connections": {
                    "Get Contacts": {
                    "ai_tool": [
                        [
                        {
                            "node": "Contact Agent2",
                            "type": "ai_tool",
                            "index": 0
                        }
                        ]
                    ]
                    },
                    "Add or Update Contact": {
                    "ai_tool": [
                        [
                        {
                            "node": "Contact Agent2",
                            "type": "ai_tool",
                            "index": 0
                        }
                        ]
                    ]
                    },
                    "Google Gemini Chat Model1": {
                    "ai_languageModel": [
                        [
                        {
                            "node": "Contact Agent2",
                            "type": "ai_languageModel",
                            "index": 0
                        }
                        ]
                    ]
                    },
                    "When Executed by Another Workflow": {
                    "main": [
                        [
                        {
                            "node": "Contact Agent2",
                            "type": "main",
                            "index": 0
                        }
                        ]
                    ]
                    },
                    "Contact Agent2": {
                    "main": [
                        [
                        {
                            "node": "Response",
                            "type": "main",
                            "index": 0
                        }
                        ],
                        [
                        {
                            "node": "Try Again2",
                            "type": "main",
                            "index": 0
                        }
                        ]
                    ]
                    }
                },
                "active": False,
                "settings": {
                    "executionOrder": "v1"
                },
                "versionId": "07f46e94-c82d-4da1-a972-e415c38b6872",
                "meta": {
                    "instanceId": "150692bad95c45279834c73a1668cb2894616f65767d082d2e66cc2431e380fa"
                },
                "id": "eYgtJ3zjSOo2IWtp",
                "tags": []
                }}
        ]
    )

class UserInputWorkflowConfigGeneratorAgent(UserInput):
    """User input for generating n8n workflow configurations."""
    message: str = Field(
        description="User input to the agent for workflow configuration generation.",
        examples=[
            "Generate an n8n workflow configuration for processing CVs and saving to a database",
            "Create a workflow that handles banking loan applications with AI risk assessment",
            "Build a workflow for customer onboarding with KYC verification"
        ],
    )
    
    workflow_plan: str = Field(
        description="Optional workflow plan or description to guide the configuration generation.",
        default="",
        examples=[
            "1. Receive CV via webhook\n2. Parse CV content using AI\n3. Extract candidate information\n4. Save to Google Sheets\n5. Send confirmation email",
            "1. Customer submits loan application\n2. Validate application data\n3. Perform credit check\n4. AI risk assessment\n5. Auto-approve or route to manual review"
        ]
    )
    
class ToolCall(TypedDict):
    """Represents a request to call a tool."""

    name: str
    """The name of the tool to be called."""
    args: dict[str, Any]
    """The arguments to the tool call."""
    id: str | None
    """An identifier associated with the tool call."""
    type: NotRequired[Literal["tool_call"]]


class ChatMessage(BaseModel):
    """Message in a chat."""

    type: Literal["human", "ai", "tool", "custom", "workflow_config", "workflow_plan"] = Field(
        description="Role of the message.",
        examples=["human", "ai", "tool", "custom"],
    )
    content: str = Field(
        description="Content of the message.",
        examples=["Hello, world!"],
    )
    tool_calls: list[ToolCall] = Field(
        description="Tool calls in the message.",
        default=[],
    )
    tool_call_id: str | None = Field(
        description="Tool call that this message is responding to.",
        default=None,
        examples=["call_Jja7J89XsjrOLA5r!MEOW!SL"],
    )
    run_id: str | None = Field(
        description="Run ID of the message.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    response_metadata: dict[str, Any] = Field(
        description="Response metadata. For example: response headers, logprobs, token counts.",
        default={},
    )
    custom_data: dict[str, Any] = Field(
        description="Custom message data.",
        default={},
    )

    def pretty_repr(self) -> str:
        """Get a pretty representation of the message."""
        base_title = self.type.title() + " Message"
        padded = " " + base_title + " "
        sep_len = (80 - len(padded)) // 2
        sep = "=" * sep_len
        second_sep = sep + "=" if len(padded) % 2 else sep
        title = f"{sep}{padded}{second_sep}"
        return f"{title}\n\n{self.content}"

    def pretty_print(self) -> None:
        print(self.pretty_repr())  # noqa: T201


class Feedback(BaseModel):  # type: ignore[no-redef]
    """Feedback for a run, to record to LangSmith."""

    run_id: str = Field(
        description="Run ID to record feedback for.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    key: str = Field(
        description="Feedback key.",
        examples=["human-feedback-stars"],
    )
    score: float = Field(
        description="Feedback score.",
        examples=[0.8],
    )
    kwargs: dict[str, Any] = Field(
        description="Additional feedback kwargs, passed to LangSmith.",
        default={},
        examples=[{"comment": "In-line human feedback"}],
    )


class FeedbackResponse(BaseModel):
    status: Literal["success"] = "success"


class ChatHistoryInput(BaseModel):
    """Input for retrieving chat history."""

    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    
    agent_id: str | None = Field(
        description="Agent ID to filter the chat history. Includes workflow_explain_chatbot, and other agent IDs.",
        default="workflow_explain_chatbot",
        examples=["workflow_explain_chatbot"],
    )


class ChatHistory(BaseModel):
    messages: list[ChatMessage]
    
class ModelInferenceInput(BaseModel):
    """Input for model inference."""

    model_id: str = Field(
        description="ID of the model to use for inference.",
        examples=["model_CreditCard_20250614_015533"],
    )

class ColumnSchema(BaseModel):
    """Schema for column information in ETL input."""
    table_name: str
    column_name: str
    data_type: str

class SchemaAnalysisInput(UserInput):
    """Schema for ETL connection string input. All ETL parameters are nested inside clean_etl_input."""
    schemas_analysis_config: dict[str, Any] = Field(
        description="Clean ETL input for the agent. All ETL parameters should be included as keys in this dictionary.",
        default={},
        examples=[
            {
                "catalog": None,
                "dsn": "bhdl:Brotherhoodofdeadline@tcp(13.212.242.96:3306)/dummy?charset=utf8mb4",
                "schema": "dummy",
                "type": "mysql",
                "columns": [
                    {"table_name": "ATM_Transactions", "column_name": "transaction_id", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "card_number_masked", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "transaction_type", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "transaction_amount", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "currency", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "atm_id", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "location", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "timestamp", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "is_successful", "data_type": "varchar"},
                    {"table_name": "ATM_Transactions", "column_name": "error_code", "data_type": "varchar"}
                ]
            }
        ],
    )

class DataCleaningInput(UserInput):
    """Schema for data cleaning input in the ETL pipeline.
    """
    
    data_cleaning_config: dict[str, Any] = Field(
        description="Data cleaning configuration for the agent. All cleaning parameters should be included as keys in this dictionary.",
        default={},
        examples=[
            {"column_info": {"description": "User name field",
                        "actual_type": "string",
                        "quality_issues": ["Some names have extra spaces", "Mixed case formatting"],
                        "patterns": ["Full names with titles", "Mixed case"],
                        "sample_values": ["  John Doe  ", "jane smith", "ALICE BROWN"]},
            "column_name": "name",
            "user_prompt": "Clean the name column for data warehouse ingestion"}
        ]
    )

class StreamETLInput(SchemaAnalysisInput):
    """Schema for streaming ETL analysis input."""
    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )

class CleanedDataResult(BaseModel):
    """Schema for cleaned data result from the ETL pipeline."""
    original_data: List[Dict[str, Any]] = Field(
        description="Original sample data before cleaning"
    )
    cleaned_data: List[Dict[str, Any]] = Field(
        description="Cleaned sample data ready for Data Warehouse ingestion"
    )
    cleaning_code: str = Field(
        description="Generated Python/Pandas code used for data cleaning"
    )
    execution_summary: Dict[str, Any] = Field(
        description="Summary of the cleaning execution including statistics"
    )
    schema_analysis: Dict[str, Any] = Field(
        description="Schema analysis that informed the cleaning process"
    )
    data_quality_flags: Dict[str, Any] = Field(
        description="Data quality flags and scores for the cleaned data",
        default={}
    )

