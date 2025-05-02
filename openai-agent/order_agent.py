from apply_env import apply_env
from agents import Agent, Runner
from agents.mcp import MCPServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderAgent:
    """Agent to track and manage order status"""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, mcp_server: MCPServer = None):
        self.mcp_server = mcp_server
        apply_env()

    async def invoke(self, query) -> str:
        """Execute the order status agent"""
        return await run_agent(query, self.mcp_server)


async def run_agent(user_query=None, mcp_server: MCPServer = None) -> str:
    """
    This function runs the agent along with the mcp servers
    """
    if mcp_server is not None:
        agent = Agent(
            name="OrderAssistant",
            instructions="Use the mcp server and its tools to check order status, list orders, and update order status.",
            mcp_servers=[mcp_server],
        )
    else:
        agent = Agent(
            name="OrderAssistant",
            instructions="Use the mcp server and its tools to check order status, list orders, and update order status.",
        )

    result = await Runner.run(starting_agent=agent, input=user_query)

    return result.final_output 