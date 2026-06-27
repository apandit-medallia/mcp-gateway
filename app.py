import asyncio
from fastapi import FastAPI, Request

from config import MCP_SERVERS, TOOL_ROUTES, TOOLS_LIST
from discovery import discover
from gateway import gateway_handler


app = FastAPI()


@app.on_event("startup")
async def init():
    mcp_server_details = [discover(mcp_server) for mcp_server in MCP_SERVERS]
    await asyncio.gather(*mcp_server_details)
    print(TOOL_ROUTES)
    print(f"Total tools loaded: {len(TOOLS_LIST)}")


@app.post("/mcp")
async def mcp(request: Request):
    return await gateway_handler(request)
