import json
import requests
import aiohttp

from langgraph.types import StreamWriter

from agents.utils import send_custom_stream_data
from core.settings import logger, settings

def workflow_config_positioning(workflow: dict):
    """Auto positioning of workflow configuration in n8n.
    """
    url = "https://api.ia2s.app/webhook/workflow/magic/position"

    # Replace this with your actual workflow data
    payload = {
        "workflow": workflow,
    }

    headers = {
        "Content-Type": "application/json"
    }

    logger.info("Sending request to n8n positioning endpoint...")
    response = requests.post(url, json=payload, headers=headers)

    return json.loads(response.text)


async def aworkflow_config_positioning(workflow: dict):
    """Auto positioning of workflow configuration in n8n.
    """
    url = "https://api.ia2s.app/webhook/workflow/magic/position"

    # Replace this with your actual workflow data
    payload = {
        "workflow": workflow,
    }

    headers = {
        "Content-Type": "application/json"
    }

    logger.info("Sending request to n8n positioning endpoint...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            text = await response.text()
            return json.loads(text)

# async def get_user_features(writer: StreamWriter) -> dict:
#     """Return the release date of Langgraph."""
#     send_custom_stream_data(
#         writer,
#         type="current_state",
#         data={
#             "mode": "updates",
#             "event": {"message": "Starting reasoning process..."},
#         },
#     )
    
#     # Simulating a delay to mimic data retrieval
#     data =  {
#         "time": "2023-01-01",
#         "features": {
#             **database_connector.fetch_customer_feature_metadata(), 
#             **database_connector.fetch_product_feature_metadata(), 
#             **database_connector.fetch_adoption_log_metadata(),
#         }
#     }
    
#     feature_count = len(data["features"])
#     feature_list = ", ".join(data["features"].keys())
    
#     send_custom_stream_data(
#         writer,
#         type="current_state",
#         data={
#             "mode": "updates",
#             "event": {
#                 "message": (
#                     f"User features retrieved successfully. "
#                     f"Included {feature_count} features. \n"
#                     f"Feature list: {feature_list}"
#                 )
#             },
#         },
#     )
    
#     return data

# async def get_category_data(writer: StreamWriter, category_id: str) -> dict:
#     """Return the product data based on category_id."""
#     send_custom_stream_data(
#         writer,
#         type="current_state",
#         data={
#             "mode": "updates",
#             "event": {"message": f"Retrieving metadata data for category_id: {category_id}..."},
#         },
#     )
    
#     category_data = database_connector.fetch_category_data(category_id)
    
#     send_custom_stream_data(
#         writer,
#         type="current_state",
#         data={
#             "mode": "updates",
#             "event": {
#                 "message": (
#                     f"Metadata data of category id {category_id} retrieved successfully: \n"
#                     f"- Name: {category_data.get('name', 'Unknown Category')}, \n"
#                     f"- Description: {category_data.get('description', 'No description available.')}, \n"
#                     f"- User Portrait: {category_data.get('user_portrait', 'No target audience specified.')}"
#                 )
#             },
#         },
#     )
    
#     return category_data


def test_posisioning_workflow():
    """Test the workflow configuration positioning."""
    
    import json
    sample_workflow = json.load(open("../example_workflow/Sample_for_positioning.json", "r"))
    sample_workflow = json.loads(json.dumps(sample_workflow))  # Ensure it's a proper dict
    
    workflow_config_positioning(sample_workflow)
    
if __name__ == "__main__":
    # Example workflow configuration
    test_posisioning_workflow()
    