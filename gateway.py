from fastapi import Request, Response

from config import TOOL_ROUTES, TOOLS_LIST
from proxy import forward_mcp_request

async def gateway_handler(request: Request):

    body = await request.json()
    method = body.get("method")

    # -------------------------
    # 1. initialize (HANDLE LOCALLY)
    # -------------------------
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "protocolVersion": body["params"]["protocolVersion"],
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                },
                "serverInfo": {
                    "name": "mcp-gateway",
                    "version": "1.0.0"
                }
            }
        }

    # -------------------------
    # 2. notifications/initialized (IGNORE)
    # -------------------------
    if method == "notifications/initialized":
        return Response(status_code=204)

    # -------------------------
    # 3. tools/list (AGGREGATED)
    # -------------------------
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": TOOLS_LIST
            }
        }

    # -------------------------
    # 4. tools/call (ROUTE)
    # -------------------------
    if method == "tools/call":

        tool = body["params"]["name"]
        mcp_server = TOOL_ROUTES.get(tool)

        if not mcp_server:
            return Response(
                content='{"error":"Unknown tool"}',
                status_code=404,
                media_type="application/json",
            )

        return await forward_mcp_request(mcp_server, request)

    # -------------------------
    # 5. fallback (ignore safely)
    # -------------------------
    return Response(
        content='{"error":"Unsupported method"}',
        status_code=400,
        media_type="application/json",
    )
