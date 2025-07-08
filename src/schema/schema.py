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
    
    category_config: dict[str, Any] = Field(
        description="Category configuration to pass through to the agent",
        default={},
        examples=[{"category_id": "CreditCard"}],
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

class UserInputExplainModelAgent(UserInput):
    """User input for explaining a model in the agent."""

    model_explain_config: dict[str, Any] = Field(
        description="Configuration for the model explanation.",
        default={},
        examples=[
            {
                "user_id": "37a72d0d-460e-44e0-b398-61b9ba5745c4",
                "product_id": "13387e14-30ea-48db-b996-d2e5e4de7f28",
            }
        ]
    )
    
class UserInputTrainModelAgent(UserInput):
    """User input for training a model in the agent."""

    category_config: dict[str, Any] = Field(
        description="Product configuration to pass through to the agent",
        default={},
        examples=[{"category_id": "CreditCard"}],
    )
    
    # Model training parameters
    model_training_config: dict[str, Any] = Field(
        description="Parameters for training the model.",
        default={
            "feature_list": [
                'user_id',
                'age',
                'occupation',
                'income_tier',
                'marital_status',
                'household_size',
                'preferred_language',
                'products',
                'tenure_years',
                'avg_balance',
                'cc_limit_util',
                'mortgage_outstanding',
                'investments_aum',
                'monthly_salary',
                'top_mcc',
                'ecom_pos_ratio',
                'overseas_share',
                'avg_bill_pay_amt',
                'cash_wd_freq',
                'mobile_login_freq',
                'days_since_push',
                'preferred_channel',
                'offer_ctr',
                'offer_accepts',
                'offer_fatigue'
            ],
            "max_depth": 5,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
        },
        examples=[
            {
                "feature_list": [
                    'user_id',
                    'age',
                    'occupation',
                    'income_tier',
                    'marital_status',
                    'household_size',
                    'preferred_language',
                    'products',
                    'tenure_years',
                    'avg_balance',
                    'cc_limit_util',
                    'mortgage_outstanding',
                    'investments_aum',
                    'monthly_salary',
                    'top_mcc',
                    'ecom_pos_ratio',
                    'overseas_share',
                    'avg_bill_pay_amt',
                    'cash_wd_freq',
                    'mobile_login_freq',
                    'days_since_push',
                    'preferred_channel',
                    'offer_ctr',
                    'offer_accepts',
                    'offer_fatigue'
                ],
                "max_depth": 5,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
            }
        ],
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

    type: Literal["human", "ai", "tool", "custom", "model_training_result"] = Field(
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
        description="Agent ID to filter the chat history. Includes select_feature_agent, train_model_agent, and other agent IDs.",
        default="select_feature_agent",
        examples=["select_feature_agent"],
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

