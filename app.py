from asyncio import gather
from fastapi import FastAPI, Request
from json import dumps

from config import MCP_SERVERS, QOUTA_COUNTER, RATE_LIMITER, TOOL_ROUTES, TOOL_LIST
from discovery import discover
import auth
import gateway


app = FastAPI()


@app.on_event("startup")
async def init():
    mcp_server_details = [discover(mcp_server) for mcp_server in MCP_SERVERS]
    await gather(*mcp_server_details)
    print(dumps(TOOL_ROUTES, indent=4))
    print(f"Total tools loaded: {len(TOOL_LIST)}")


@app.post("/mcp")
async def mcp(request: Request):

    body = await request.json()

    try:
        method = body.get("method")

        auth.authenticate_and_authorize(request, required_capability=method)

        if method == "initialize":
            return await gateway.handle_initialize(body)
        
        if method == "notifications/initialized":
            return await gateway.handle_initialized_notification()
        
        if method == "tools/list":
            return await gateway.handle_tools_list(body)
        
        if method == "tools/call":

            rate_limit_exceeded = await RATE_LIMITER.check_rate_limit()
            if rate_limit_exceeded:
                return await gateway.handle_rate_limit_exceeded(body)


            quota_exceeded = QOUTA_COUNTER.check_qouta()
            if quota_exceeded:
                return await gateway.handle_quota_exceeded(body)
            

            return await gateway.handle_tool_call(request)
        
        return await gateway.handle_unsupported_method()
    
    except auth.AuthenticationError as ex:
        return await gateway.handle_authentication_error(body)

    except auth.AuthorizationError as ex:
        return await gateway.handle_authorization_error(body)

