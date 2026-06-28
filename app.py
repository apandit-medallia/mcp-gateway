from asyncio import gather
from fastapi import FastAPI, Request
from json import dumps

from config import MCP_SERVERS, TOOL_ROUTES, TOOLS_LIST
from discovery import discover
import gateway


app = FastAPI()


@app.on_event("startup")
async def init():
    mcp_server_details = [discover(mcp_server) for mcp_server in MCP_SERVERS]
    await gather(*mcp_server_details)
    print(dumps(TOOL_ROUTES, indent=4))
    print(f"Total tools loaded: {len(TOOLS_LIST)}")


@app.post("/mcp")
async def mcp(request: Request):

    body = await request.json()
    method = body.get("method")

    if method == "initialize":
        return await gateway.handle_initialize(body)
    
    if method == "notifications/initialized":
        return await gateway.handle_initialized_notification()
    
    if method == "tools/list":
        return await gateway.handle_tools_list(body)
    
    if method == "tools/call":
        return await gateway.handle_tool_call(request)
    
    return await gateway.handle_unsupported_method()
