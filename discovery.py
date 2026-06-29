from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from config import TOOL_ROUTES, TOOL_LIST


async def discover(mcp_server: str):

    async with streamable_http_client(mcp_server) as (read_stream, write_stream, mcp_session):
        
        async with ClientSession(read_stream, write_stream) as session:

            # MCP handshake (backend session created here)
            await session.initialize()
            # fetch tools
            result = await session.list_tools()

            for tool in result.tools:
                TOOL_ROUTES[tool.name] = mcp_server
                TOOL_LIST.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                })

            print(f"Loaded {len(result.tools)} tools from {mcp_server}")
