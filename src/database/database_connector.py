import logging
import json
import pandas as pd

from sqlalchemy import create_engine
from core.settings import settings

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self):
        self.connection_string = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        logger.info(f"Connecting to database with connection string: {self.connection_string}")
        self.engine = create_engine(
            self.connection_string
        )
        
        
    def fetch_user_feature_snapshots(self, feature_list: list[str]) -> pd.DataFrame:
        """
        Fetch user feature snapshots from the database based on the provided feature list.
        
        Args:
            feature_list (list[str]): List of features to fetch from the database.
        
        Returns:
            pd.DataFrame: DataFrame containing the user feature snapshots.
        """
        query = f"SELECT {', '.join(feature_list)} FROM tcb.user_feature_snapshot LIMIT 10;"
        df = pd.read_sql_query(query, self.engine)
        return df
    
    def save_user_feature_likelihoods(self, user_feature_likelihoods: pd.DataFrame) -> None:
        """
        Save user feature likelihoods to the database.
        
        Args:
            user_feature_likelihoods (pd.DataFrame): DataFrame containing user feature likelihoods.
        """
        logger.info("Saving user feature likelihoods to database...")
        user_feature_likelihoods["metadata"] = user_feature_likelihoods["metadata"].apply(json.dumps)
        user_feature_likelihoods.to_sql(
            'customer_product_likelihood',
            con=self.engine,
            if_exists='append',
            index=False
        )
        logger.info("User feature likelihoods saved to database.")
        
    def fetch_user_feature_likelihoods(self, user_id: str, product_id: str) -> pd.DataFrame:
        """
        Fetch user feature likelihoods from the database based on the provided product ID.
        
        Args:
            product_id (str): The ID of the product to fetch likelihoods for.
        
        Returns:
            pd.DataFrame: DataFrame containing the user feature likelihoods.
        """
        query = f"""
            SELECT * FROM customer_product_likelihood
            WHERE product_id = '{user_id}' AND product_id = '{product_id}'
            LIMIT 1;
        """
        df = pd.read_sql_query(query, self.engine)
        return df.to_dict(orient="records")
    
    async def async_fetch_user_feature_likelihoods(self, user_id: str, product_id: str) -> dict:
        """
        Asynchronously fetch user feature likelihoods from the database based on the provided product ID.
        
        Args:
            user_id (str): The ID of the user to fetch likelihoods for.
            product_id (str): The ID of the product to fetch likelihoods for.
        
        Returns:
            list[dict]: List of dictionaries containing the user feature likelihoods.
        """
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        import pandas as pd

        # Build async connection string (assuming PostgreSQL)
        async_conn_str = self.connection_string.replace('postgresql+psycopg2', 'postgresql+asyncpg')
        async_engine = create_async_engine(async_conn_str)
        query = f"""
            SELECT * FROM customer_product_likelihood
            WHERE user_id = '{user_id}' AND product_id = '{product_id}';
        """
        async with async_engine.connect() as conn:
            result = await conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
        return df.to_dict(orient="records")[0] if not df.empty else {} # limit to one record
    
    def fetch_product_data(self, product_id: str) -> pd.DataFrame:
        """
        Fetch product data from the database based on the provided product ID.
        
        Args:
            product_id (str): The ID of the product to fetch data for.
        
        Returns:
            pd.DataFrame: DataFrame containing the product data.
        """
        query = f"SELECT * FROM tcb.product_data WHERE product_id = '{product_id}';"
        df = pd.read_sql_query(query, self.engine)
        return df
    
    def fetch_interaction_data(self, product_id: str, date: str) -> pd.DataFrame:
        """
        Fetch user interaction data with a specific product from the database.
        
        Args:
            product_id (str): The ID of the product.
        
        Returns:
            list[pd.DataFrame]: DataFrame containing the user interaction data.
        """
        query = f"""
        SELECT * FROM tcb.user_interaction
        WHERE product_id = '{product_id}';
        """
        df = pd.read_sql_query(query, self.engine)
        return df
    
database_connector = DatabaseConnector()