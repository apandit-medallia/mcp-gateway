from fastapi import Request, Response

from config import RATE_LIMITER, TOOL_ROUTES, TOOL_LIST
from proxy import forward_mcp_request


async def handle_authentication_error(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {
            "code": 401,
            "message": "Authentication Error",
        },
    }


async def handle_authorization_error(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {
            "code": 403,
            "message": "Authorization Error",
        },
    }


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
            "tools": TOOL_LIST
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


async def handle_quota_exceeded(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {
            "code": -32001,
            "message": "Tools call quota exceeded."
        }
    }


async def handle_rate_limit_exceeded(body: dict):
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {
            "code": 429,
            "message": "Rate limit exceeded",
            "data": {
                "retry_after_seconds": round(RATE_LIMITER.reset_in, 2)
            }
        }
    }


async def handle_unsupported_method():
    return Response(
        content='{"error":"Unsupported method"}',
        status_code=400,
        media_type="application/json",
    )
