from fastapi import FastAPI, Request, Response

from gateway import startup
from routing import tool_routes, all_tools
from config import DEFAULT_BACKEND
from proxy import forward_tool_call

app = FastAPI()


@app.on_event("startup")
async def init():
    await startup()
    print(tool_routes)
    print(f"Total tools loaded: {len(all_tools)}")


@app.post("/mcp")
async def mcp(request: Request):

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
                "tools": all_tools
            }
        }

    # -------------------------
    # 4. tools/call (ROUTE)
    # -------------------------
    if method == "tools/call":

        tool = body["params"]["name"]
        backend = tool_routes.get(tool)

        if not backend:
            return Response(
                content='{"error":"Unknown tool"}',
                status_code=404,
                media_type="application/json",
            )

        return await forward_tool_call(request, backend)

    # -------------------------
    # 5. fallback (ignore safely)
    # -------------------------
    return Response(
        content='{"error":"Unsupported method"}',
        status_code=400,
        media_type="application/json",
    )