import asyncio
from typing import Dict, List

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from routing import tool_routes, all_tools

# backend -> session_id
backend_sessions: Dict[str, str] = {}


async def discover(server: str):
    print(f"Discovering tools from {server}")

    async with streamablehttp_client(server) as (
        read_stream,
        write_stream,
        get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as session:

            # MCP handshake (backend session created here)
            await session.initialize()

            session_id = get_session_id()
            backend_sessions[server] = session_id

            print(f"[{server}] session = {session_id}")

            # fetch tools
            result = await session.list_tools()

            for tool in result.tools:
                tool_routes[tool.name] = server

                all_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                })

            print(f"Loaded {len(result.tools)} tools from {server}")