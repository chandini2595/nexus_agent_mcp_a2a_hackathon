#!/usr/bin/env python3
"""
Dummy JIRA service for creating and managing JIRA tickets.
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

# Fix the import for expose
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("jira_service")

# In-memory storage for tickets
TICKETS = {
    "JIRA-001": {
        "id": "JIRA-001",
        "summary": "Fix login page bug",
        "description": "Users are unable to login when using special characters in passwords",
        "status": "Open",
        "priority": "High",
        "assignee": "john.doe",
        "reporter": "jane.smith",
        "created": "2023-09-15T10:30:45",
        "updated": "2023-09-15T10:30:45",
        "comments": [
            {
                "id": "comment-001",
                "author": "jane.smith",
                "body": "This is a blocker for our release",
                "created": "2023-09-15T10:31:22"
            }
        ],
        "type": "Bug"
    },
    "JIRA-002": {
        "id": "JIRA-002",
        "summary": "Add password reset feature",
        "description": "Implement password reset functionality with email verification",
        "status": "In Progress",
        "priority": "Medium",
        "assignee": "jane.smith",
        "reporter": "john.doe",
        "created": "2023-09-16T14:22:10",
        "updated": "2023-09-17T09:15:32",
        "comments": [],
        "type": "Feature"
    }
}

# Available statuses
STATUSES = ["Open", "In Progress", "In Review", "Done", "Closed"]

# Available priorities
PRIORITIES = ["Critical", "High", "Medium", "Low"]

# Available issue types
ISSUE_TYPES = ["Bug", "Feature", "Task", "Story", "Epic"]


@mcp.tool()
async def test_jira_auth(random_string: str) -> Dict:
    """Test authentication with JIRA API."""
    return {
        "status": "success",
        "message": "Authentication successful with dummy JIRA service"
    }


@mcp.tool()
async def search_jira_issues(jql: str, fields: Optional[List[str]] = None, 
                      maxResults: int = 50, startAt: int = 0) -> Dict:
    """Search for JIRA issues using JQL (JIRA Query Language)."""
    logger.info(f"Searching for issues with JQL: {jql}")
    
    # Specific static response for JIRA-001 regardless of JQL
    if "JIRA-001" in jql:
        issue = TICKETS["JIRA-001"]
        formatted_ticket = {
            "id": issue["id"],
            "key": issue["id"],
            "self": f"https://jira.example.com/rest/api/2/issue/{issue['id']}",
            "fields": issue
        }
        
        return {
            "startAt": 0,
            "maxResults": maxResults,
            "total": 1,
            "issues": [formatted_ticket]
        }
    
    # Parse JQL (simple implementation)
    filtered_tickets = list(TICKETS.values())
    
    # Handle direct issue ID lookup (no JQL)
    if jql and jql.strip() in TICKETS:
        issue_id = jql.strip()
        logger.info(f"Direct issue lookup for ID: {issue_id}")
        if issue_id in TICKETS:
            filtered_tickets = [TICKETS[issue_id]]
        else:
            filtered_tickets = []
    # Handle empty JQL - return all tickets
    elif not jql or jql.strip() == "":
        logger.info("Empty JQL query - returning all issues")
    # Parse specific JQL conditions
    else:
        # Check for issue ID in JQL
        if "id =" in jql.lower() or "key =" in jql.lower() or "issue =" in jql.lower():
            # Extract the issue ID from the JQL
            for term in ["id =", "key =", "issue ="]:
                if term in jql.lower():
                    issue_id = jql.lower().split(term)[1].strip().strip('"\'')
                    filtered_tickets = [t for t in filtered_tickets if t["id"].lower() == issue_id.lower()]
                    break
        
        if "status =" in jql.lower():
            status = jql.split("status =")[1].strip().strip('"\'')
            filtered_tickets = [t for t in filtered_tickets if t["status"].lower() == status.lower()]
        
        if "priority =" in jql.lower():
            priority = jql.split("priority =")[1].strip().strip('"\'')
            filtered_tickets = [t for t in filtered_tickets if t["priority"].lower() == priority.lower()]
        
        if "assignee =" in jql.lower():
            assignee = jql.split("assignee =")[1].strip().strip('"\'')
            filtered_tickets = [t for t in filtered_tickets if t["assignee"].lower() == assignee.lower()]
    
    # Apply pagination
    paginated_tickets = filtered_tickets[startAt:startAt + maxResults]
    
    # Format the tickets properly for JIRA-like response
    formatted_tickets = []
    for ticket in paginated_tickets:
        formatted_ticket = {
            "id": ticket["id"],
            "key": ticket["id"],
            "self": f"https://jira.example.com/rest/api/2/issue/{ticket['id']}",
            "fields": ticket
        }
        formatted_tickets.append(formatted_ticket)
    
    return {
        "startAt": startAt,
        "maxResults": maxResults,
        "total": len(filtered_tickets),
        "issues": formatted_tickets
    }


@mcp.tool()
async def create_jira_issue(fields: Dict) -> Dict:
    """Create a new JIRA issue."""
    logger.info(f"Creating new issue: {fields}")
    
    # Generate new ID
    next_id = len(TICKETS) + 1
    issue_id = f"JIRA-{next_id:03d}"
    
    # Create issue
    now = datetime.now().isoformat()
    
    # Handle required fields and provide defaults if missing
    issue_type = fields.get("issuetype", {}).get("name", "Task")
    if issue_type not in ISSUE_TYPES:
        issue_type = "Task"
    
    project_key = fields.get("project", {}).get("key", "JIRA")
    summary = fields.get("summary", "Untitled Issue")
    description = fields.get("description", "")
    
    priority = fields.get("priority", {}).get("name", "Medium")
    if priority not in PRIORITIES:
        priority = "Medium"
    
    assignee = fields.get("assignee", {}).get("name", "unassigned")
    
    # Create the issue
    new_issue = {
        "id": issue_id,
        "summary": summary,
        "description": description,
        "status": "Open",
        "priority": priority,
        "assignee": assignee,
        "reporter": "current.user",
        "created": now,
        "updated": now,
        "comments": [],
        "type": issue_type
    }
    
    # Store in memory
    TICKETS[issue_id] = new_issue
    
    return {
        "id": issue_id,
        "key": issue_id,
        "self": f"https://jira.example.com/rest/api/2/issue/{issue_id}",
        "fields": new_issue
    }


@mcp.tool()
async def update_jira_issue(issueIdOrKey: str, fields: Optional[Dict] = None) -> Dict:
    """Update an existing JIRA issue."""
    logger.info(f"Updating issue {issueIdOrKey} with {fields}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    issue = TICKETS[issueIdOrKey]
    now = datetime.now().isoformat()
    
    # Update fields if provided
    if fields:
        if "summary" in fields:
            issue["summary"] = fields["summary"]
        
        if "description" in fields:
            issue["description"] = fields["description"]
        
        if "priority" in fields and "name" in fields["priority"]:
            priority = fields["priority"]["name"]
            if priority in PRIORITIES:
                issue["priority"] = priority
        
        if "assignee" in fields and "name" in fields["assignee"]:
            issue["assignee"] = fields["assignee"]["name"]
        
        if "status" in fields and "name" in fields["status"]:
            status = fields["status"]["name"]
            if status in STATUSES:
                issue["status"] = status
    
    # Update the updated timestamp
    issue["updated"] = now
    
    return {
        "id": issueIdOrKey,
        "key": issueIdOrKey,
        "self": f"https://jira.example.com/rest/api/2/issue/{issueIdOrKey}",
        "fields": issue
    }


@mcp.tool()
async def get_jira_comments(issueIdOrKey: str, maxResults: int = 50, startAt: int = 0) -> Dict:
    """Get comments for a JIRA issue."""
    logger.info(f"Getting comments for issue {issueIdOrKey}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    issue = TICKETS[issueIdOrKey]
    comments = issue.get("comments", [])
    
    # Apply pagination
    paginated_comments = comments[startAt:startAt + maxResults]
    
    return {
        "startAt": startAt,
        "maxResults": maxResults,
        "total": len(comments),
        "comments": paginated_comments
    }


@mcp.tool()
async def add_jira_comment(issueIdOrKey: str, comment: Dict) -> Dict:
    """Add a comment to a JIRA issue."""
    logger.info(f"Adding comment to issue {issueIdOrKey}: {comment}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    issue = TICKETS[issueIdOrKey]
    now = datetime.now().isoformat()
    
    # Create comment
    comment_body = comment.get("body", "")
    comment_id = f"comment-{uuid.uuid4().hex[:6]}"
    
    new_comment = {
        "id": comment_id,
        "author": "current.user",
        "body": comment_body,
        "created": now
    }
    
    # Add visibility if provided
    if "visibility" in comment:
        new_comment["visibility"] = comment["visibility"]
    
    # Add to comments
    if "comments" not in issue:
        issue["comments"] = []
    
    issue["comments"].append(new_comment)
    
    # Update the issue's updated timestamp
    issue["updated"] = now
    
    return new_comment


@mcp.tool()
async def get_jira_transitions(issueIdOrKey: str) -> Dict:
    """Get available transitions for a JIRA issue."""
    logger.info(f"Getting transitions for issue {issueIdOrKey}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    issue = TICKETS[issueIdOrKey]
    current_status = issue["status"]
    
    # Generate available transitions based on current status
    transitions = []
    transition_id = 1
    
    for status in STATUSES:
        if status != current_status:
            transitions.append({
                "id": str(transition_id),
                "name": status,
                "to": {
                    "id": str(STATUSES.index(status) + 1),
                    "name": status
                }
            })
            transition_id += 1
    
    return {
        "transitions": transitions
    }


@mcp.tool()
async def transition_jira_status(issueIdOrKey: str, transitionId: str, 
                         comment: Optional[str] = None,
                         resolution: Optional[Dict] = None) -> Dict:
    """Transition the status of a JIRA issue by applying a transition."""
    logger.info(f"Transitioning issue {issueIdOrKey} with transition ID {transitionId}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    # Get available transitions
    transitions_result = await get_jira_transitions(issueIdOrKey)
    transitions = transitions_result.get("transitions", [])
    
    # Find transition by ID
    target_transition = None
    for transition in transitions:
        if transition["id"] == transitionId:
            target_transition = transition
            break
    
    if not target_transition:
        return {
            "status": "error",
            "message": f"Transition ID {transitionId} not found for issue {issueIdOrKey}"
        }
    
    # Apply transition
    issue = TICKETS[issueIdOrKey]
    new_status = target_transition["to"]["name"]
    issue["status"] = new_status
    issue["updated"] = datetime.now().isoformat()
    
    # Add comment if provided
    if comment:
        await add_jira_comment(issueIdOrKey, {"body": comment})
    
    return {
        "id": issueIdOrKey,
        "key": issueIdOrKey,
        "status": new_status,
        "success": True
    }


@mcp.tool()
async def transition_jira_status_by_name(issueIdOrKey: str, statusName: str,
                                comment: Optional[str] = None,
                                resolution: Optional[Dict] = None) -> Dict:
    """Transition the status of a JIRA issue by specifying the target status name."""
    logger.info(f"Transitioning issue {issueIdOrKey} to status {statusName}")
    
    if issueIdOrKey not in TICKETS:
        return {
            "status": "error",
            "message": f"Issue {issueIdOrKey} not found"
        }
    
    if statusName not in STATUSES:
        return {
            "status": "error",
            "message": f"Status {statusName} is not a valid status"
        }
    
    # Apply transition directly
    issue = TICKETS[issueIdOrKey]
    issue["status"] = statusName
    issue["updated"] = datetime.now().isoformat()
    
    # Add comment if provided
    if comment:
        await add_jira_comment(issueIdOrKey, {"body": comment})
    
    return {
        "id": issueIdOrKey,
        "key": issueIdOrKey,
        "status": statusName,
        "success": True
    }


if __name__ == "__main__":
    # Start the server
    print("Starting JIRA Service MCP server...")
    mcp.run(transport="stdio")
    print("JIRA Service MCP server is running.") 