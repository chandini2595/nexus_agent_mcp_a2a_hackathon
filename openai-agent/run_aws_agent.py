#!/usr/bin/env python3
import os
import sys
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse, PlainTextResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import asyncio
from dotenv import load_dotenv

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
load_dotenv()

# Check for required environment variables
if not os.getenv("PERPLEXITY_API_KEY"):
    print("Error: PERPLEXITY_API_KEY environment variable is not set.")
    print("Please set this in your .env file or environment variables.")
    sys.exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set this in your .env file or environment variables.")
    sys.exit(1)

# Import after environment variables are loaded
from aws_agent import AwsAgent
from agents.mcp import MCPServerStdio

# Global variable to store the MCP server
server = None

async def startup():
    global server
    print("Starting AWS Assistant agent...")
    server = MCPServerStdio(
        name="AWS Assistant",
        params={
            "command": sys.executable,
            "args": [os.path.join(current_dir, "aws.py")],
        },
    )
    await server.connect()
    print("AWS Assistant agent started.")

async def shutdown():
    global server
    if server:
        print("Shutting down AWS Assistant agent...")
        try:
            await server.disconnect()
        except Exception as e:
            print(f"Error shutting down: {str(e)}")
        print("AWS Assistant agent shut down.")

async def handle_query(request):
    global server
    user_query = request.query_params.get("prompt")
    
    if not user_query:
        return JSONResponse({"error": "No prompt provided. Use ?prompt=your question here"})
    
    print(f"Received query: {user_query}")
    
    try:
        aws_agent = AwsAgent(server)
        result = await aws_agent.invoke(user_query)
        return JSONResponse({"response": result})
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return JSONResponse({"error": f"Error processing query: {str(e)}"}, status_code=500)

# Create route for agent response
main_routes = [
    Route("/", handle_query, methods=["GET"]),
]

# Create well-known routes manually as fallback
async def get_agent_json(request):
    return FileResponse(os.path.join(current_dir, '.well-known', 'agent.json'))

async def get_server_info_json(request):
    return FileResponse(os.path.join(current_dir, '.well-known', 'server_info.json'))

async def get_service_json(request):
    return FileResponse(os.path.join(current_dir, '.well-known', 'service.json'))

async def get_openapi_yaml(request):
    return FileResponse(os.path.join(current_dir, '.well-known', 'openapi.yaml'), media_type='application/x-yaml')

async def get_agent_definition_json(request):
    return FileResponse(os.path.join(current_dir, '.well-known', 'agent-definition.json'))

# Create well-known routes
well_known_routes = [
    Route("/agent.json", get_agent_json),
    Route("/agent-info.json", get_agent_json),
    Route("/agent-definition.json", get_agent_definition_json),
    Route("/server_info.json", get_server_info_json),
    Route("/service.json", get_service_json),
    Route("/openapi.yaml", get_openapi_yaml),
]

# Main app with all routes
app = Starlette(
    debug=True,
    routes=[
        *main_routes,
        Mount("/.well-known", StaticFiles(directory=os.path.join(current_dir, ".well-known")), name="static"),
        Mount("/.well-known", routes=well_known_routes),  # Fallback routes
    ],
    on_startup=[startup],
    on_shutdown=[shutdown]
)

if __name__ == "__main__":
    port = 10003
    print(f"Starting server on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 