import httpx

from fastapi import Request
from fastapi.responses import Response


HOP_BY_HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "transfer-encoding",
}


async def forward(request: Request, server: str):

    body = await request.body()

    headers = {}

    #
    # Forward ALL incoming headers
    #
    for k, v in request.headers.items():

        if k.lower() not in HOP_BY_HOP_HEADERS:
            headers[k] = v

    async with httpx.AsyncClient(timeout=None) as client:

        response = await client.post(
            server,
            content=body,
            headers=headers,
        )

    #
    # Copy ALL response headers back
    #
    out_headers = {}

    for k, v in response.headers.items():

        if k.lower() not in HOP_BY_HOP_HEADERS:
            out_headers[k] = v

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=out_headers,
        media_type=response.headers.get(
            "content-type",
            "application/json",
        ),
    )