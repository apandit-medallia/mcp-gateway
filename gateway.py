import asyncio
from config import BACKEND_SERVERS
from discovery import discover


async def startup():
    tasks = [discover(server) for server in BACKEND_SERVERS]
    await asyncio.gather(*tasks)