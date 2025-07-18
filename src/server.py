import asyncio
import sys

import uvicorn
from dotenv import load_dotenv

from core import settings

load_dotenv()

if __name__ == "__main__":
    # Set Compatible event loop policy on Windows Systems.
    # On Windows systems, the default ProactorEventLoop can cause issues with
    # certain async database drivers like psycopg (PostgreSQL driver).
    # The WindowsSelectorEventLoopPolicy provides better compatibility and prevents
    # "RuntimeError: Event loop is closed" errors when working with database connections.
    # This needs to be set before running the application server.
    # Refer to the documentation for more information.
    # https://www.psycopg.org/psycopg3/docs/advanced/async.html#asynchronous-operations
    uvicorn.run("service:app", host=settings.HOST, port=settings.PORT, reload=settings.is_dev())
