from apply_env import apply_env
from agents import Agent, Runner
from agents.mcp import MCPServer
import logging
import asyncio
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemporalAgent:
    """Remote agent that utilizes Temporal for workflow orchestration"""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, mcp_server: MCPServer = None):
        self.mcp_server = mcp_server
        apply_env()

    async def invoke(self, query) -> str:
        """Execute the Temporal workflow agent"""
        return await run_agent(query, self.mcp_server)


async def run_agent(user_query=None, mcp_server: MCPServer = None) -> str:
    """
    This function runs the agent along with the mcp servers
    """
    if mcp_server is not None:
        agent = Agent(
            name="TemporalAssistant",
            instructions="""You are a workflow automation expert that uses Temporal.
            Use the mcp server and its tools to create, monitor, and manage durable workflows.
            Help users understand how to create fault-tolerant, long-running business processes.""",
            mcp_servers=[mcp_server],
        )
    else:
        agent = Agent(
            name="TemporalAssistant",
            instructions="""You are a workflow automation expert that uses Temporal.
            Use the mcp server and its tools to create, monitor, and manage durable workflows.
            Help users understand how to create fault-tolerant, long-running business processes.""",
        )

    result = await Runner.run(starting_agent=agent, input=user_query)

    return result.final_output 