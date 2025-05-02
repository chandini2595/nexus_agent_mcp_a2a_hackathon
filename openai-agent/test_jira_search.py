#!/usr/bin/env python3
"""
Test script for JIRA search functionality.
"""

import asyncio
import json
import sys
import os
from agents.mcp import MCPServerStdio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search():
    """Test the search_jira_issues functionality."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jira_service_path = os.path.join(script_dir, "jira_service.py")
    
    async with MCPServerStdio(
        name="JIRA Ticket agent",
        params={
            "command": "python",
            "args": [
                jira_service_path
            ],
        },
    ) as server:
        await server.connect()
        logger.info("Connected to JIRA service")
        
        # Test direct issue ID lookup
        logger.info("Testing direct issue ID lookup...")
        result = await server.call_tool("search_jira_issues", {"jql": "JIRA-001"})
        logger.info(f"Direct ID search result: {result.result}")
        logger.info(f"Number of issues found: {len(result.result.get('issues', []))}")
        
        # Test ID lookup using JQL
        logger.info("Testing JQL ID lookup...")
        result = await server.call_tool("search_jira_issues", {"jql": "id = JIRA-001"})
        logger.info(f"Number of issues found: {len(result.result.get('issues', []))}")
        
        # Test status lookup
        logger.info("Testing status lookup...")
        result = await server.call_tool("search_jira_issues", {"jql": "status = Open"})
        logger.info(f"Number of issues found: {len(result.result.get('issues', []))}")
        
        # Test empty JQL
        logger.info("Testing empty JQL...")
        result = await server.call_tool("search_jira_issues", {"jql": ""})
        logger.info(f"Empty JQL search result: Number of issues: {len(result.result.get('issues', []))}")
        
        logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(test_search()) 