import asyncio

from config import BACKEND_SERVERS
from discovery import discover

async def startup():

    tasks = []

    for server in BACKEND_SERVERS:
        tasks.append(discover(server))

    await asyncio.gather(*tasks)