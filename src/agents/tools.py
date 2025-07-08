from langgraph.types import StreamWriter

from agents.utils import send_custom_stream_data

from database.fake_database_connector import database_connector

async def get_user_features(writer: StreamWriter) -> dict:
    """Return the release date of Langgraph."""
    send_custom_stream_data(
        writer,
        type="current_state",
        data={
            "mode": "updates",
            "event": {"message": "Starting reasoning process..."},
        },
    )
    
    # Simulating a delay to mimic data retrieval
    data =  {
        "time": "2023-01-01",
        "features": {
            **database_connector.fetch_customer_feature_metadata(), 
            **database_connector.fetch_product_feature_metadata(), 
            **database_connector.fetch_adoption_log_metadata(),
        }
    }
    
    feature_count = len(data["features"])
    feature_list = ", ".join(data["features"].keys())
    
    send_custom_stream_data(
        writer,
        type="current_state",
        data={
            "mode": "updates",
            "event": {
                "message": (
                    f"User features retrieved successfully. "
                    f"Included {feature_count} features. \n"
                    f"Feature list: {feature_list}"
                )
            },
        },
    )
    
    return data

async def get_category_data(writer: StreamWriter, category_id: str) -> dict:
    """Return the product data based on category_id."""
    send_custom_stream_data(
        writer,
        type="current_state",
        data={
            "mode": "updates",
            "event": {"message": f"Retrieving metadata data for category_id: {category_id}..."},
        },
    )
    
    category_data = database_connector.fetch_category_data(category_id)
    
    send_custom_stream_data(
        writer,
        type="current_state",
        data={
            "mode": "updates",
            "event": {
                "message": (
                    f"Metadata data of category id {category_id} retrieved successfully: \n"
                    f"- Name: {category_data.get('name', 'Unknown Category')}, \n"
                    f"- Description: {category_data.get('description', 'No description available.')}, \n"
                    f"- User Portrait: {category_data.get('user_portrait', 'No target audience specified.')}"
                )
            },
        },
    )
    
    return category_data