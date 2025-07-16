import inspect
import json
import logging
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any, Union
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain_core._api import LangChainBetaWarning
from langchain_core.messages import AIMessage, AIMessageChunk, AnyMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.pregel import Pregel
from langgraph.types import Command, Interrupt
from langsmith import Client as LangsmithClient

from agents import DEFAULT_AGENT, get_agent, get_all_agent_info
from core import settings
from memory import initialize_database, initialize_store
from database.inmem_database import InMemoryDatabase
from schema import (
    ChatHistory,
    ChatHistoryInput,
    ChatMessage,
    Feedback,
    FeedbackResponse,
    ServiceMetadata,
    UserInput,
    UserInputSelectFeatureAgent,
    ModelInferenceInput,
    UserInputExplainWorkflowAgent,
    UserInputWorkflowConfigGeneratorAgent,
    SchemaAnalysisInput,
    DataCleaningInput
)
from service.utils import (
    convert_message_content_to_string,
    langchain_to_chat_message,
    remove_tool_calls,
)

warnings.filterwarnings("ignore", category=LangChainBetaWarning)
logger = logging.getLogger(__name__)


def verify_bearer(
    http_auth: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(HTTPBearer(description="Please provide AUTH_SECRET api key.", auto_error=False)),
    ],
) -> None:
    if not settings.AUTH_SECRET:
        return
    auth_secret = settings.AUTH_SECRET.get_secret_value()
    if not http_auth or http_auth.credentials != auth_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Configurable lifespan that initializes the appropriate database checkpointer and store
    based on settings.
    """
    try:
        # Initialize both checkpointer (for short-term memory) and store (for long-term memory)
        async with initialize_database() as saver, initialize_store() as store:
            # Set up both components
            if hasattr(saver, "setup"):  # ignore: union-attr
                await saver.setup()
            # Only setup store for Postgres as InMemoryStore doesn't need setup
            if hasattr(store, "setup"):  # ignore: union-attr
                await store.setup()

            # Configure agents with both memory components
            agents = get_all_agent_info()
            for a in agents:
                agent = get_agent(a.key)
                # Set checkpointer for thread-scoped memory (conversation history)
                agent.checkpointer = saver
                # Set store for long-term memory (cross-conversation knowledge)
                agent.store = store
            yield
    except Exception as e:
        logger.error(f"Error during database/store initialization: {e}")
        raise


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(dependencies=[Depends(verify_bearer)])
inmem_store = InMemoryDatabase(file_path=settings.INMEMORY_STORE_FILE_PATH)

@router.get("/info")
async def info() -> ServiceMetadata:
    models = list(settings.AVAILABLE_MODELS)
    models.sort()
    return ServiceMetadata(
        agents=get_all_agent_info(),
        models=models,
        default_agent=DEFAULT_AGENT,
        default_model=settings.DEFAULT_MODEL,
    )


async def _handle_input(user_input: Union[UserInput, UserInputSelectFeatureAgent, UserInputExplainWorkflowAgent, UserInputWorkflowConfigGeneratorAgent, SchemaAnalysisInput, DataCleaningInput], agent: Pregel) -> tuple[dict[str, Any], UUID]:
    """
    Parse user input and handle any required interrupt resumption.
    Returns kwargs for agent invocation and the run_id.
    """
    run_id = uuid4()
    thread_id = user_input.thread_id or str(uuid4())
    user_id = user_input.user_id or str(uuid4())

    # save thread_id for user_id in in-memory store
    thread_id_for_user_id: list[str] = inmem_store.get(user_id)
    if not (thread_id in thread_id_for_user_id):
        thread_id_for_user_id.append(thread_id)
    inmem_store.set(user_id, thread_id_for_user_id)
    
    configurable = {"thread_id": thread_id, "model": user_input.model, "user_id": user_id}

    if user_input.agent_config:
        if overlap := configurable.keys() & user_input.agent_config.keys():
            raise HTTPException(
                status_code=422,
                detail=f"agent_config contains reserved keys: {overlap}",
            )
        configurable.update(user_input.agent_config)
    logger.info(f"user_input {user_input}")
    # Merge product_config and model_config safely, defaulting to empty dicts if None
    category_config = user_input.category_config if hasattr(user_input, "category_config") else {}
    workflow_json_data = user_input.workflow_json_data if hasattr(user_input, "workflow_json_data") else {}
    clean_etl_config = user_input.schemas_analysis_config if hasattr(user_input, "clean_etl_config") else {}
    data_cleaning_config = user_input.data_cleaning_config if hasattr(user_input, "data_cleaning_config") else {}
    
    # Handle workflow config generator specific fields
    workflow_config_data = {}
    if hasattr(user_input, "workflow_plan") and user_input.workflow_plan:
        workflow_config_data["workflow_plan"] = user_input.workflow_plan
    
    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
        metadata={**category_config, **workflow_json_data, **clean_etl_config, **data_cleaning_config, **workflow_config_data},
    )
    
    # Check for interrupts that need to be resumed
    state = await agent.aget_state(config=config)
    interrupted_tasks = [
        task for task in state.tasks if hasattr(task, "interrupts") and task.interrupts
    ]

    input: Command | dict[str, Any]
    if interrupted_tasks:
        # assume user input is response to resume agent execution from interrupt
        input = Command(resume=user_input.message)
    else:
        input = {"messages": [HumanMessage(content=user_input.message)]}

    kwargs = {
        "input": input,
        "config": config,
    }

    return kwargs, run_id


async def message_generator(
    user_input: UserInput, agent_id: str = DEFAULT_AGENT
) -> AsyncGenerator[str, None]:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    agent: Pregel = get_agent(agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)

    try:
        # Process streamed events from the graph and yield messages over the SSE stream.
        async for stream_event in agent.astream(
            **kwargs, stream_mode=["updates", "messages", "custom"]
        ):
            if not isinstance(stream_event, tuple):
                continue
            stream_mode, event = stream_event
            new_messages = []
            if stream_mode == "updates":
                for node, updates in event.items():
                    # A simple approach to handle agent interrupts.
                    # In a more sophisticated implementation, we could add
                    # some structured ChatMessage type to return the interrupt value.
                    if node == "__interrupt__":
                        interrupt: Interrupt
                        for interrupt in updates:
                            new_messages.append(AIMessage(content=interrupt.value))
                        continue
                    updates = updates or {}
                    update_messages = updates.get("messages", [])
                    # special cases for using langgraph-supervisor library
                    if node == "supervisor":
                        # Get only the last AIMessage since supervisor includes all previous messages
                        ai_messages = [msg for msg in update_messages if isinstance(msg, AIMessage)]
                        if ai_messages:
                            update_messages = [ai_messages[-1]]
                    if node in ("research_expert", "math_expert", "feature_extraction"):
                        # By default the sub-agent output is returned as an AIMessage.
                        # Convert it to a ToolMessage so it displays in the UI as a tool response.
                        msg = ToolMessage(
                            content=update_messages[0].content,
                            name=node,
                            tool_call_id="",
                        )
                        update_messages = [msg]
                    new_messages.extend(update_messages)

            if stream_mode == "custom":
                new_messages = [event]

            # LangGraph streaming may emit tuples: (field_name, field_value)
            # e.g. ('content', <str>), ('tool_calls', [ToolCall,...]), ('additional_kwargs', {...}), etc.
            # We accumulate only supported fields into `parts` and skip unsupported metadata.
            # More info at: https://langchain-ai.github.io/langgraph/cloud/how-tos/stream_messages/
            processed_messages = []
            current_message: dict[str, Any] = {}
            for message in new_messages:
                if isinstance(message, tuple):
                    key, value = message
                    # Store parts in temporary dict
                    current_message[key] = value
                else:
                    # Add complete message if we have one in progress
                    if current_message:
                        processed_messages.append(_create_ai_message(current_message))
                        current_message = {}
                    processed_messages.append(message)

            # Add any remaining message parts
            if current_message:
                processed_messages.append(_create_ai_message(current_message))

            for message in processed_messages:
                try:
                    chat_message = langchain_to_chat_message(message)
                    chat_message.run_id = str(run_id)
                except Exception as e:
                    logger.error(f"Error parsing message: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
                    continue
                # LangGraph re-sends the input message, which feels weird, so drop it
                if chat_message.type == "human" and chat_message.content == user_input.message:
                    continue
                yield f"data: {json.dumps({'type': 'message', 'content': chat_message.model_dump()})}\n\n"

            if stream_mode == "messages":
                if not user_input.stream_tokens:
                    continue
                msg, metadata = event
                if "skip_stream" in metadata.get("tags", []):
                    continue
                # For some reason, astream("messages") causes non-LLM nodes to send extra messages.
                # Drop them.
                if not isinstance(msg, AIMessageChunk):
                    continue
                content = remove_tool_calls(msg.content)
                if content:
                    # Empty content in the context of OpenAI usually means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content.
                    yield f"data: {json.dumps({'type': 'token', 'content': convert_message_content_to_string(content)})}\n\n"
    except Exception as e:
        logger.error(f"Error in message generator: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Internal server error'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


def _create_ai_message(parts: dict) -> AIMessage:
    sig = inspect.signature(AIMessage)
    valid_keys = set(sig.parameters)
    filtered = {k: v for k, v in parts.items() if k in valid_keys}
    return AIMessage(**filtered)


def _sse_response_example() -> dict[int | str, Any]:
    return {
        status.HTTP_200_OK: {
            "description": "Server Sent Event Response",
            "content": {
                "text/event-stream": {
                    "example": "data: {'type': 'token', 'content': 'Hello'}\n\ndata: {'type': 'token', 'content': ' World'}\n\ndata: [DONE]\n\n",
                    "schema": {"type": "string"},
                }
            },
        }
    }


@router.post("/simple_chatbot/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def simple_chatbot(
    user_input: UserInputSelectFeatureAgent,
) -> StreamingResponse:
    """
    Stream the response from the select feature agent.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id="simple_chatbot"),
        media_type="text/event-stream",
    )
    
@router.post("/workflow_explain_chatbot/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def workflow_explain_chatbot(
    user_input: UserInputExplainWorkflowAgent,
) -> StreamingResponse:
    """
    Stream the response from the workflow explain chatbot agent.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id="workflow_explain_chatbot"),
        media_type="text/event-stream",
    )
    
@router.post("/workflow_planner_chatbot/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def workflow_planner_chatbot(
    user_input: UserInput,
) -> StreamingResponse:
    """
    Stream the response from the workflow planner chatbot agent.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id="workflow_planner_chatbot"),
        media_type="text/event-stream",
    )

@router.post("/workflow_config_generator/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def workflow_config_generator(
    user_input: UserInputWorkflowConfigGeneratorAgent,
) -> StreamingResponse:
    """
    Stream the response from the workflow config generator agent.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id="workflow_config_generator"),
        media_type="text/event-stream",
    )

@router.post("/feedback")
async def feedback(feedback: Feedback) -> FeedbackResponse:
    """
    Record feedback for a run to LangSmith.

    This is a simple wrapper for the LangSmith create_feedback API, so the
    credentials can be stored and managed in the service rather than the client.
    See: https://api.smith.langchain.com/redoc#tag/feedback/operation/create_feedback_api_v1_feedback_post
    """
    client = LangsmithClient()
    kwargs = feedback.kwargs or {}
    client.create_feedback(
        run_id=feedback.run_id,
        key=feedback.key,
        score=feedback.score,
        **kwargs,
    )
    return FeedbackResponse()


@router.post("/history")
def history(input: ChatHistoryInput) -> ChatHistory:
    """
    Get chat history.
    Agent_id list: ["workflow_explain_chatbot"].
    """
    try:
        agent: Pregel = get_agent(input.agent_id)
        state_snapshot = agent.get_state(
            config=RunnableConfig(configurable={"thread_id": input.thread_id})
        )
        messages: list[AnyMessage] = state_snapshot.values["messages"]
        chat_messages: list[ChatMessage] = [langchain_to_chat_message(m) for m in messages]
        return ChatHistory(messages=chat_messages)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=404, detail="Thread not found or no messages available.")

@router.get("/user_id/")
def get_user_id(
) -> list[str]:
    """
    Get all thread IDs for a given user ID.
    """
    user_id = inmem_store.keys()
    if not user_id:
        raise HTTPException(status_code=404, detail="Can not found any user ID.")
    return user_id

@router.get("/thread_id/{user_id}")
def get_thread_id(user_id: str) -> list[str]:
    """
    Get all thread IDs for a given user ID.
    """
    thread_ids = inmem_store.get(user_id)
    if not thread_ids:
        raise HTTPException(status_code=404, detail="Thread IDs not found for the given user ID.")
    return thread_ids

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

    
app.include_router(router)