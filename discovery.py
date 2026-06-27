from routing import tool_routes, all_tools

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def discover(server: str):

    print(f"Discovering tools from {server}")

    async with streamablehttp_client(server) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            result = await session.list_tools()

            for tool in result.tools:

                tool_routes[tool.name] = server

                # IMPORTANT: normalize schema for Inspector compatibility
                all_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                })

            print(f"Loaded {len(result.tools)} tools from {server}")