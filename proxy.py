import httpx
from fastapi import Request
from fastapi.responses import Response

from discovery import streamablehttp_client, ClientSession

HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "transfer-encoding",
}


async def forward_tool_call(request: Request, server: str):

    body = await request.body()

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in HOP_HEADERS and k.lower() != "mcp-session-id"
    }

    async with streamablehttp_client(server) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:

            # 🔥 ALWAYS re-init session (no reuse)
            await session.initialize()

            # inject fresh session
            headers["Mcp-Session-Id"] = get_session_id()

            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post(
                    server,
                    content=body,
                    headers=headers,
                )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )