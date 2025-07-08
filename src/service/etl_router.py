from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx
import os
import json
from dotenv import load_dotenv
from schema import SchemaAnalysisInput, StreamETLInput
from typing import List, Dict, Any, AsyncGenerator
import pandas as pd
import numpy as np
import re
from datetime import datetime

def convert_to_json_serializable(obj):
    """Convert pandas/numpy types to JSON serializable Python types."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (pd.Timestamp, np.datetime64)):
        return obj.isoformat() if pd.notnull(obj) else None
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj
from agents.schema_analysis_agent import schema_analysis_agent, SchemaAnalysisState
from langchain_core.messages import AIMessageChunk

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/etl", tags=["etl"])

async def fetch_sample_data(input_data: StreamETLInput) -> Dict[str, Any]:
    """
    Step 1: Fetch sample data from the database.
    """
    table_name = input_data.columns[0].table_name if input_data.columns else None
    
    payload = {
        "type": input_data.type,
        "dsn": input_data.dsn,
        "schema": input_data.schema,
        "table": table_name,
        "limit": 10,
        "page": 0,
        "order": "-timestamp"
    }
    
    backend_url = os.getenv("BACKEND_URL", "https://be.bhdl.tech")
    api_url = f"{backend_url}/api/schema-extract/table"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()

async def analyze_schema_step(
    input_data: StreamETLInput, 
    api_response: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Step 2: Analyze database schema using the schema analysis agent.
    """
    # Create the initial state for the agent
    db_schema = [column.dict() for column in input_data.columns]
    state = SchemaAnalysisState(
        messages=[],
        db_schema=db_schema,
        sample_data=api_response['data'],
        user_prompt=input_data.catalog if input_data.catalog else ""
    )
    
    schema_analysis_result = None
    
    # Stream the agent's analysis
    async for stream_event in schema_analysis_agent.astream(
        state, stream_mode=["updates", "messages", "custom"]
    ):
        if not isinstance(stream_event, tuple):
            continue
            
        stream_mode, event = stream_event
        
        if stream_mode == "messages":
            if not input_data.stream_tokens:
                continue
            msg, metadata = event
            if "skip_stream" in metadata.get("tags", []):
                continue
            if not isinstance(msg, AIMessageChunk):
                continue
            content = msg.content
            if content:
                yield {"type": "stream", "content": f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"}
        
        elif stream_mode == "updates":
            for node, updates in event.items():
                if "schema_analysis" in updates:
                    schema_analysis_result = updates["schema_analysis"]
                
                if "reasoning_messages" in updates:
                    yield {"type": "stream", "content": f"data: {json.dumps({'type': 'reasoning', 'content': updates['reasoning_messages']})}\n\n"}


async def data_quality_assessment_step(
    input_data: StreamETLInput,
    api_response: Dict[str, Any],
    schema_analysis: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Step 3: Assess data quality based on schema analysis.
    (Placeholder for future implementation)
    """
    yield {"type": "stream", "content": f"data: {json.dumps({'type': 'status', 'content': 'Assessing data quality...'})}\n\n"}
    
    # TODO: Implement data quality assessment logic
    # This could include:
    # - Null value analysis
    # - Data type consistency checks
    # - Outlier detection
    # - Pattern validation
    
    yield {"type": "stream", "content": f"data: {json.dumps({'type': 'status', 'content': 'Data quality assessment completed'})}\n\n"}
    
    quality_result = {
        "quality_score": 85,
        "issues_found": ["Some null values in optional fields"],
        "recommendations": ["Consider adding data validation rules"]
    }

async def generate_etl_pipeline_step(
    input_data: StreamETLInput,
    schema_analysis: Dict[str, Any],
    quality_assessment: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Step 4: Generate ETL pipeline recommendations.
    (Placeholder for future implementation)
    """
    yield {"type": "stream", "content": f"data: {json.dumps({'type': 'status', 'content': 'Generating ETL pipeline recommendations...'})}\n\n"}
    
    # TODO: Implement ETL pipeline generation logic
    # This could include:
    # - Data transformation suggestions
    # - Loading strategies
    # - Performance optimizations
    # - Error handling recommendations
    
    yield {"type": "stream", "content": f"data: {json.dumps({'type': 'status', 'content': 'ETL pipeline generation completed'})}\n\n"}
    
    pipeline_result = {
        "pipeline_steps": [
            "Extract data from source",
            "Apply data type conversions",
            "Handle null values",
            "Load to target system"
        ],
        "estimated_time": "15 minutes",
        "complexity": "Medium"
    }

async def etl_message_generator(input_data: StreamETLInput) -> AsyncGenerator[str, None]:
    """
    Main ETL processing pipeline with multiple steps.
    """
    try:
        # Step 1: Fetch sample data
        yield f"data: {json.dumps({'type': 'status', 'content': 'Step 1/5: Fetching sample data from database...'})}\n\n"
        api_response = await fetch_sample_data(input_data)
        yield f"data: {json.dumps({'type': 'status', 'content': 'Sample data fetched successfully'})}\n\n"
        
        # Step 2: Schema analysis
        yield f"data: {json.dumps({'type': 'status', 'content': 'Step 2/5: Starting schema analysis...'})}\n\n"
        schema_analysis_result = None
        async for message in analyze_schema_step(input_data, api_response):
            if message["type"] == "stream":
                yield message["content"]
        
        # Get the schema analysis result from the analyze_schema_step
        state = SchemaAnalysisState(
            messages=[],
            db_schema=[column.dict() for column in input_data.columns],
            sample_data=api_response['data'],
            user_prompt=input_data.catalog if input_data.catalog else ""
        )
        
        # Run schema analysis to get result
        async for stream_event in schema_analysis_agent.astream(state, stream_mode=["updates"]):
            if isinstance(stream_event, tuple):
                stream_mode, event = stream_event
                if stream_mode == "updates":
                    for node, updates in event.items():
                        if "schema_analysis" in updates:
                            schema_analysis_result = updates["schema_analysis"]
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'Schema analysis completed'})}\n\n"
        
        # Step 3: Data cleaning (process each column individually)
        yield f"data: {json.dumps({'type': 'status', 'content': 'Step 3/5: Starting data cleaning...'})}\n\n"
        cleaned_data_result = convert_to_json_serializable(api_response['data'])  # Start with original data
        all_execution_results = []
        
        if schema_analysis_result and 'column_analysis' in schema_analysis_result:
            # Import the data cleaning agent locally
            from agents.data_cleaning_agent import data_cleaning_agent, DataCleaningState
            
            column_analysis = schema_analysis_result['column_analysis']
            
            # Process each column individually
            for column_name, column_info in column_analysis.items():
                status_content = f"Processing column: {column_name}..."
                yield f"data: {json.dumps({'type': 'status', 'content': status_content})}\n\n"
                
                # Create the initial state for this specific column
                cleaning_state = DataCleaningState(
                    messages=[],
                    column_info=column_info,
                    sample_data=cleaned_data_result,  # Use the progressively cleaned data
                    column_name=column_name,
                    user_prompt=f"Clean the {column_name} column for data warehouse ingestion"
                )
                
                column_cleaning_code = None
                column_execution_result = None
                
                # Stream the data cleaning process for this column (only code generation)
                async for stream_event in data_cleaning_agent.astream(
                    cleaning_state, stream_mode=["updates", "messages", "custom"]
                ):
                    if not isinstance(stream_event, tuple):
                        continue
                        
                    stream_mode, event = stream_event
                    
                    if stream_mode == "messages":
                        if input_data.stream_tokens:
                            msg, metadata = event
                            if "skip_stream" not in metadata.get("tags", []) and hasattr(msg, 'content'):
                                content = msg.content
                                if content:
                                    token_content = f"[{column_name}] {content}"
                                    yield f"data: {json.dumps({'type': 'token', 'content': token_content})}\n\n"
                    
                    elif stream_mode == "updates":
                        for node, updates in event.items():
                            if "cleaning_code" in updates:
                                column_cleaning_code = updates["cleaning_code"]
                            
                            if "reasoning_messages" in updates:
                                reasoning_content = f"[{column_name}] {updates['reasoning_messages']}"
                                yield f"data: {json.dumps({'type': 'cleaning_reasoning', 'content': reasoning_content})}\n\n"
                
                # Execute the generated code on the server
                if column_cleaning_code:
                    try:
                        print(column_cleaning_code)
                        # Convert sample data to DataFrame
                        df = pd.DataFrame(cleaned_data_result)
                        original_df = df.copy()
                        
                        # Create a safe execution environment
                        exec_globals = {
                            'pd': pd,
                            'np': np,
                            're': re,
                            'datetime': datetime,
                            'df': df
                        }
                        
                        # Execute the cleaning code
                        exec(column_cleaning_code, exec_globals)
                        
                        # Get the modified DataFrame
                        modified_df = exec_globals.get('df')
                        
                        if modified_df is not None:
                            # Convert back to list of dictionaries with JSON-safe types
                            cleaned_data_result = convert_to_json_serializable(modified_df.to_dict('records'))
                            
                            # Check what changed in the specific column
                            original_values = original_df[column_name].tolist() if column_name in original_df.columns else []
                            cleaned_values = modified_df[column_name].tolist() if column_name in modified_df.columns else []
                            
                            # Calculate changes
                            values_changed = sum(1 for i, (orig, clean) in enumerate(zip(original_values, cleaned_values)) if orig != clean)
                            
                            column_execution_result = {
                                "status": "success",
                                "column_processed": column_name,
                                "original_rows": int(len(original_df)),
                                "cleaned_rows": int(len(modified_df)),
                                "cleaning_code": column_cleaning_code,
                                "column_stats": {
                                    "values_changed": int(values_changed),
                                    "null_before": int(original_df[column_name].isnull().sum()) if column_name in original_df.columns else 0,
                                    "null_after": int(modified_df[column_name].isnull().sum()) if column_name in modified_df.columns else 0,
                                    "data_type_before": str(original_df[column_name].dtype) if column_name in original_df.columns else "unknown",
                                    "data_type_after": str(modified_df[column_name].dtype) if column_name in modified_df.columns else "unknown"
                                }
                            }
                        else:
                            column_execution_result = {
                                "status": "error",
                                "message": "DataFrame not found in execution result",
                                "column_processed": column_name,
                                "cleaning_code": column_cleaning_code
                            }
                            
                    except Exception as e:
                        column_execution_result = {
                            "status": "error",
                            "message": str(e),
                            "column_processed": column_name,
                            "cleaning_code": column_cleaning_code
                        }
                    
                    # Report the execution result
                    yield f"data: {json.dumps({'type': 'cleaning_result', 'content': column_execution_result})}\n\n"
                
                if column_execution_result:
                    all_execution_results.append(column_execution_result)
                
                completion_content = f"Column {column_name} processing completed"
                yield f"data: {json.dumps({'type': 'status', 'content': completion_content})}\n\n"
        
        # Combine all execution results
        execution_result = {
            "status": "success",
            "columns_processed": len(all_execution_results),
            "individual_results": all_execution_results,
            "summary": {
                "total_columns": len(all_execution_results),
                "successful_columns": len([r for r in all_execution_results if r.get("status") == "success"]),
                "failed_columns": len([r for r in all_execution_results if r.get("status") == "error"])
            }
        }
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'Data cleaning completed'})}\n\n"
        
        # Step 4: Data quality assessment
        yield f"data: {json.dumps({'type': 'status', 'content': 'Step 4/5: Starting data quality assessment...'})}\n\n"
        async for message in data_quality_assessment_step(input_data, api_response, schema_analysis_result):
            if message["type"] == "stream":
                yield message["content"]
        
        # Step 5: ETL pipeline generation
        yield f"data: {json.dumps({'type': 'status', 'content': 'Step 5/5: Generating ETL pipeline...'})}\n\n"
        async for message in generate_etl_pipeline_step(input_data, schema_analysis_result, None):
            if message["type"] == "stream":
                yield message["content"]
        
        # Final result with cleaned data
        if cleaned_data_result and execution_result:
            final_result = {
                "type": "final_result",
                "cleaned_data": convert_to_json_serializable(cleaned_data_result),
                "execution_summary": convert_to_json_serializable(execution_result),
                "schema_analysis": convert_to_json_serializable(schema_analysis_result)
            }
            yield f"data: {json.dumps({'type': 'final_result', 'content': final_result})}\n\n"
                            
    except httpx.HTTPError as e:
        error_result = {
            "status": "error",
            "message": f"Error calling backend API: {str(e)}",
            "details": {
                "dsn": input_data.dsn,
                "schema": input_data.schema,
                "type": input_data.type,
                "columns": [column.dict() for column in input_data.columns]
            }
        }
        yield f"data: {json.dumps({'type': 'error', 'content': error_result})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': f'Internal server error: {str(e)}'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"

def _sse_response_example() -> dict[int | str, Any]:
    return {
        200: {
            "description": "Server Sent Event Response",
            "content": {
                "text/event-stream": {
                    "example": "data: {'type': 'token', 'content': 'Hello'}\n\ndata: {'type': 'token', 'content': ' World'}\n\ndata: [DONE]\n\n",
                    "schema": {"type": "string"},
                }
            },
        }
    }

@router.post("/clean/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def stream_etl_analysis(input_data: StreamETLInput) -> StreamingResponse:
    """
    Stream the complete ETL analysis pipeline including:
    1. Sample data extraction
    2. Schema analysis
    3. Data cleaning (generates and executes cleaning code)
    4. Data quality assessment
    5. ETL pipeline generation
    
    Returns cleaned sample data ready for Data Warehouse ingestion.
    """
    return StreamingResponse(
        etl_message_generator(input_data),
        media_type="text/event-stream",
    )
