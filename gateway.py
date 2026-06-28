from fastapi import Request, Response

from config import TOOL_ROUTES, TOOLS_LIST
from proxy import forward_mcp_request


async def handle_initialize(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "result": {
            "protocolVersion": body["params"]["protocolVersion"],
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "mcp-gateway",
                "version": "1.0.0",
            },
        },
    }


async def handle_initialized_notification():
    return Response(status_code=204)


async def handle_tools_list(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "result": {
            "tools": TOOLS_LIST
        },
    }


async def handle_tool_call(request: Request):
    body = await request.json()
    tool = body["params"]["name"]
    mcp_server = TOOL_ROUTES.get(tool)

    if not mcp_server:
        return Response(
            content='{"error":"Unknown tool"}',
            status_code=404,
            media_type="application/json",
        )

    return await forward_mcp_request(mcp_server, request)


async def handle_unsupported_method():
    return Response(
        content='{"error":"Unsupported method"}',
        status_code=400,
        media_type="application/json",
    )
