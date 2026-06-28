from fastapi import Request, Response
from httpx import AsyncClient

from discovery import streamable_http_client, ClientSession


async def forward_mcp_request(mcp_server: str, request: Request):

    body = await request.body()

    headers = {
        k: v
        for k, v in request.headers.items()
    }

    async with streamable_http_client(mcp_server) as (read, write, mcp_session):
        async with ClientSession(read, write) as session:

            await session.initialize()

            headers["Mcp-Session-Id"] = mcp_session()

            async with AsyncClient(timeout=None) as client:
                resp = await client.post(
                    mcp_server,
                    content=body,
                    headers=headers,
                )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )
