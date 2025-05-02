#!/usr/bin/env python3
import os
import sys
import socket
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
import asyncio
from dotenv import load_dotenv

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Add openai-agent directory to path for imports
openai_agent_dir = os.path.join(current_dir, "openai-agent")
if openai_agent_dir not in sys.path:
    sys.path.append(openai_agent_dir)

# Load environment variables
load_dotenv(os.path.join(current_dir, ".env"))

# Set default API keys for testing if not present
if not os.getenv("PERPLEXITY_API_KEY"):
    os.environ["PERPLEXITY_API_KEY"] = "pplx-test-key-for-debugging"
    print("Using placeholder PERPLEXITY_API_KEY for testing")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-debugging"
    print("Using placeholder OPENAI_API_KEY for testing")

# Import after environment variables are loaded
try:
    from perplexity_agent import PerplexityAgent
except ImportError:
    print("Warning: perplexity_agent module not found")
    
try:
    from openai_agent.jira_agent import JiraAgent
except ImportError:
    print("Warning: jira_agent module not found")
    
from agents.mcp import MCPServerStdio

# Function to find an available port
def find_available_port(start_port=10003, max_attempts=10):
    port = start_port
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            print(f"Port {port} is already in use, trying next port...")
            port += 1
    
    print(f"Could not find an available port after {max_attempts} attempts.")
    return None

app = Starlette()

# Global variables to store the MCP servers
perplexity_server = None
jira_server = None
order_status_server = None
aws_server = None

@app.on_event("startup")
async def startup_event():
    global perplexity_server, jira_server, order_status_server, aws_server
    
    try:
        print("Starting Perplexity AWS Advisor agent...")
        perplexity_server = MCPServerStdio(
            name="Perplexity AWS Advisor",
            params={
                "command": sys.executable,
                "args": [os.path.join(current_dir, "perplexity.py")],
            },
        )
        await perplexity_server.connect()
        print("Perplexity AWS Advisor agent started.")
    except Exception as e:
        print(f"Error starting Perplexity agent: {str(e)}")
        perplexity_server = None
    
    try:
        print("Connecting to JIRA agent...")
        jira_server = MCPServerStdio(
            name="JIRA Ticket Assistant",
            params={
                "command": sys.executable,
                "args": [os.path.join(openai_agent_dir, "jira_service.py")],
            },
        )
        await jira_server.connect()
        print("Connected to JIRA agent.")
    except Exception as e:
        print(f"Error connecting to JIRA agent: {str(e)}")
        jira_server = None
    
    try:
        print("Connecting to Order Status agent...")
        order_status_server = MCPServerStdio(
            name="Order Status Assistant",
            params={
                "command": sys.executable,
                "args": [os.path.join(current_dir, "order_status.py")],
            },
        )
        await order_status_server.connect()
        print("Connected to Order Status agent.")
    except Exception as e:
        print(f"Error connecting to Order Status agent: {str(e)}")
        order_status_server = None
    
    try:
        print("Connecting to AWS agent...")
        aws_server = MCPServerStdio(
            name="AWS EC2 Manager",
            params={
                "command": sys.executable,
                "args": [os.path.join(current_dir, "aws.py")],
            },
        )
        await aws_server.connect()
        print("Connected to AWS agent.")
    except Exception as e:
        print(f"Error connecting to AWS agent: {str(e)}")
        aws_server = None

@app.on_event("shutdown")
async def shutdown_event():
    global perplexity_server, jira_server, order_status_server, aws_server
    
    for server, name in [
        (perplexity_server, "Perplexity AWS Advisor"),
        (jira_server, "JIRA Ticket Assistant"),
        (order_status_server, "Order Status Assistant"),
        (aws_server, "AWS EC2 Manager")
    ]:
        if server:
            print(f"Shutting down {name} agent...")
            try:
                await server.disconnect()
            except Exception as e:
                print(f"Error shutting down {name} server: {str(e)}")
            print(f"{name} agent shut down.")

@app.route("/", methods=["GET"])
async def handle_query(request):
    global perplexity_server, jira_server, order_status_server, aws_server
    
    user_query = request.query_params.get("prompt")
    service = request.query_params.get("service", "perplexity").lower()
    
    if not user_query:
        return JSONResponse({
            "error": "No prompt provided. Use ?prompt=your question here&service=[perplexity|jira|order|aws]"
        })
    
    print(f"Received query for {service}: {user_query}")
    
    try:
        if service == "jira" and jira_server:
            from openai_agent.jira_agent import JiraAgent
            agent = JiraAgent(jira_server)
            result = await agent.invoke(user_query)
            return JSONResponse({"response": result})
        elif service == "order" and order_status_server:
            # Add order status agent class if available
            # agent = OrderStatusAgent(order_status_server)
            # result = await agent.invoke(user_query)
            tools = await order_status_server.list_tools()
            result = f"Order Status tools available: {', '.join([t['name'] for t in tools])}"
            return JSONResponse({"response": result})
        elif service == "aws" and aws_server:
            # Add AWS agent class if available
            # agent = AWSAgent(aws_server)
            # result = await agent.invoke(user_query)
            tools = await aws_server.list_tools()
            result = f"AWS tools available: {', '.join([t['name'] for t in tools])}"
            return JSONResponse({"response": result})
        elif perplexity_server:
            # Default to perplexity
            from perplexity_agent import PerplexityAgent
            agent = PerplexityAgent(perplexity_server)
            result = await agent.invoke(user_query)
            return JSONResponse({"response": result})
        else:
            return JSONResponse({
                "error": f"Service '{service}' not available or not properly initialized"
            }, status_code=503)
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return JSONResponse({"error": f"Error processing query: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    # Find an available port
    port = find_available_port()
    if not port:
        print("No available ports found. Please check your network settings.")
        sys.exit(1)
        
    print(f"Starting server on http://localhost:{port}")
    
    # Add test URLs for convenience
    services = ["perplexity", "jira", "order", "aws"]
    sample_queries = {
        "perplexity": "What's the best AWS instance for a small web application?",
        "jira": "Show me information about JIRA-001",
        "order": "What's the status of order ORD001?",
        "aws": "How do I create an EC2 instance?"
    }
    
    print("You can test with:")
    for service in services:
        query = sample_queries[service]
        print(f"  {service.capitalize()}: http://localhost:{port}/?service={service}&prompt={query.replace(' ', '%20')}")
    
    uvicorn.run(app, host="0.0.0.0", port=port) 