import os
import sys
import contextlib
from typing import AsyncIterator, TypedDict

from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse, PlainTextResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from aws_agent import AwsAgent
from agents.mcp import MCPServer, MCPServerStdio
from agents import gen_trace_id, trace


class State(TypedDict):
    mcp_server: MCPServer


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[State]:
    """
    This lifespan function is called during the startup of starlette app and yields all values until all
    Yield statement. Once the starlette app shuts down, it executes the statement after the Yield statement

    This function starts the MCP server with below command locally and closes it once the starlette server shuts down
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    async with MCPServerStdio(
        name="AWS Assistant",
        params={
            "command": "python",
            "args": [
                os.path.join(current_dir, "aws.py"),
            ],
        },
    ) as server:
        yield {"mcp_server": server}
        print("shutting down...")


async def get_agent_json(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    agent_json_path = os.path.join(current_dir, '.well-known', 'agent.json')
    return FileResponse(agent_json_path)


async def get_openapi_yaml(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    openapi_path = os.path.join(current_dir, '.well-known', 'openapi.yaml')
    return FileResponse(openapi_path, media_type='application/x-yaml')


async def handle_query(request):
    mcp_server = request.app.state.mcp_server
    user_query = request.query_params.get("prompt")
    print(f"User query: {user_query}")
    
    aws_agent = AwsAgent(mcp_server)
    result = await aws_agent.invoke(user_query)
    
    return JSONResponse({"response": result})


class AwsAssistantServer:
    def __init__(self, host="0.0.0.0", port=10003):
        self.host = host
        self.port = port
        
        routes = [
            Route("/", handle_query, methods=["GET"]),
            Route("/.well-known/agent.json", get_agent_json, methods=["GET"]),
            Route("/.well-known/openapi.yaml", get_openapi_yaml, methods=["GET"]),
        ]
        
        self.app = Starlette(
            debug=True,
            lifespan=lifespan,
            routes=routes
        )

    def start(self):
        import uvicorn
        print(f"Starting AWS Assistant server on port {self.port}...")
        uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = AwsAssistantServer()
    server.start() 