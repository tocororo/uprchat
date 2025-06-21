
import asyncio
import sys
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from uprchat.app.config import get_settings

settings = get_settings()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
DB_URI = f"postgres://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_db}?sslmode=disable"
async def setup():
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()

asyncio.run(setup())
