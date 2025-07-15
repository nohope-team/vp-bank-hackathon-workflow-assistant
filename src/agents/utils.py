import json
from typing import Any

from langchain_core.messages import ChatMessage
from langgraph.types import StreamWriter
from pydantic import BaseModel, Field


class CustomData(BaseModel):
    "Custom data being sent by an agent"

    data: dict[str, Any] = Field(description="The custom data")

    def to_langchain(self) -> ChatMessage:
        return ChatMessage(content=[json.dumps(self.data, ensure_ascii=False)], role="custom")

    def dispatch(self, writer: StreamWriter) -> None:
        writer(self.to_langchain())


def send_custom_stream_data(
    writer: StreamWriter, data: dict[str, Any], type: str = "current_state"
) -> None:
    """
    Put custom data into the stream writer.
    
    Args:
        writer (StreamWriter): The stream writer to dispatch the custom data.
        data (dict[str, Any]): The custom data to be sent.
        type (str): The type of the custom data, default is "current_state".
    """
    custom_data = CustomData(data=data)
    custom_data.dispatch(writer)
    

class CustomDataAI(BaseModel):
    "Custom data being sent by an agent"

    data: dict[str, Any] = Field(description="The custom data")

    def to_langchain(self, role: str = "workflow_config") -> ChatMessage:
        return ChatMessage(content=[json.dumps(self.data, ensure_ascii=False)], role=role)

    def dispatch(self, writer: StreamWriter, role: str = "workflow_config") -> None:
        writer(self.to_langchain(role=role))


def send_custom_stream_data_workflow_config(
    writer: StreamWriter, data: dict[str, Any]
) -> None:
    """
    Put custom data into the stream writer.
    
    Args:
        writer (StreamWriter): The stream writer to dispatch the custom data.
        data (dict[str, Any]): The custom data to be sent.
        type (str): The type of the custom data, default is "current_state".
    """
    custom_data = CustomDataAI(data=data)
    custom_data.dispatch(writer, role="workflow_config")
    
def send_custom_stream_data_workflow_plan(
    writer: StreamWriter, data: dict[str, Any]
) -> None:
    """
    Put custom data into the stream writer.
    
    Args:
        writer (StreamWriter): The stream writer to dispatch the custom data.
        data (dict[str, Any]): The custom data to be sent.
        type (str): The type of the custom data, default is "current_state".
    """
    custom_data = CustomDataAI(data=data)
    custom_data.dispatch(writer, role="workflow_plan")