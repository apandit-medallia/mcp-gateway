from fastapi import FastAPI, Request, Response

from gateway import startup
from proxy import forward
from routing import tool_routes, all_tools
from config import DEFAULT_BACKEND

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
    # tools/list → AGGREGATED
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
    # tools/call → routed
    # -------------------------
    if method == "tools/call":

        tool = body["params"]["name"]
        backend = tool_routes.get(tool)

        if backend is None:
            return Response(
                content='{"error":"Unknown tool"}',
                status_code=404,
                media_type="application/json",
            )

        return await forward(request, backend)

    # -------------------------
    # everything else → default backend
    # -------------------------
    return await forward(request, DEFAULT_BACKEND)