#!/usr/bin/env python3
"""
Temporal service for creating and managing durable workflows.
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# Import MCP
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("temporal_service")

# In-memory storage for workflows
WORKFLOWS = {
    "WF-001": {
        "id": "WF-001",
        "name": "Customer Onboarding",
        "description": "Process for onboarding new customers including verification, setup, and welcome email",
        "status": "Running",
        "startTime": "2023-09-15T10:30:45",
        "lastUpdated": "2023-09-15T11:45:22",
        "steps": [
            {
                "id": "step-001",
                "name": "Identity Verification",
                "status": "Completed",
                "startTime": "2023-09-15T10:30:45",
                "endTime": "2023-09-15T10:35:12"
            },
            {
                "id": "step-002",
                "name": "Account Setup",
                "status": "Completed",
                "startTime": "2023-09-15T10:36:00",
                "endTime": "2023-09-15T10:42:30"
            },
            {
                "id": "step-003",
                "name": "Welcome Email",
                "status": "Running",
                "startTime": "2023-09-15T10:43:10",
                "endTime": None
            }
        ],
        "retries": 0,
        "timeout": "24h"
    },
    "WF-002": {
        "id": "WF-002",
        "name": "Order Processing",
        "description": "End-to-end order processing workflow with payment, inventory check, and shipping",
        "status": "Completed",
        "startTime": "2023-09-14T14:22:10",
        "lastUpdated": "2023-09-14T16:15:32",
        "steps": [
            {
                "id": "step-001",
                "name": "Payment Processing",
                "status": "Completed",
                "startTime": "2023-09-14T14:22:10",
                "endTime": "2023-09-14T14:25:45"
            },
            {
                "id": "step-002",
                "name": "Inventory Check",
                "status": "Completed",
                "startTime": "2023-09-14T14:26:00",
                "endTime": "2023-09-14T14:27:30"
            },
            {
                "id": "step-003",
                "name": "Shipping Label Creation",
                "status": "Completed",
                "startTime": "2023-09-14T14:28:10",
                "endTime": "2023-09-14T14:30:22"
            },
            {
                "id": "step-004",
                "name": "Dispatch to Warehouse",
                "status": "Completed",
                "startTime": "2023-09-14T14:31:00",
                "endTime": "2023-09-14T16:15:32"
            }
        ],
        "retries": 1,
        "timeout": "48h"
    }
}

# Available workflow statuses
STATUSES = ["Pending", "Running", "Completed", "Failed", "Canceled"]

# Available workflow templates
WORKFLOW_TEMPLATES = [
    {
        "id": "template-001",
        "name": "Customer Onboarding",
        "description": "Process for onboarding new customers",
        "steps": ["Identity Verification", "Account Setup", "Welcome Email"],
        "estimatedDuration": "1h"
    },
    {
        "id": "template-002",
        "name": "Order Processing",
        "description": "End-to-end order processing workflow",
        "steps": ["Payment Processing", "Inventory Check", "Shipping Label Creation", "Dispatch to Warehouse"],
        "estimatedDuration": "2h"
    },
    {
        "id": "template-003",
        "name": "Content Approval",
        "description": "Multi-stage content review and approval workflow",
        "steps": ["Initial Draft", "Peer Review", "Manager Approval", "Final Publication"],
        "estimatedDuration": "3d"
    }
]


@mcp.tool()
async def test_temporal_connection(random_string: str) -> Dict:
    """Test connection with Temporal service."""
    return {
        "status": "success",
        "message": "Connection successful with Temporal service"
    }


@mcp.tool()
async def list_workflows(status: Optional[str] = None, 
                   maxResults: int = 50, startAt: int = 0) -> Dict:
    """List all workflows with optional filtering by status."""
    logger.info(f"Listing workflows with status filter: {status}")
    
    # Filter workflows by status if provided
    if status:
        filtered_workflows = [wf for wf in WORKFLOWS.values() if wf["status"].lower() == status.lower()]
    else:
        filtered_workflows = list(WORKFLOWS.values())
    
    # Apply pagination
    paginated_workflows = filtered_workflows[startAt:startAt + maxResults]
    
    return {
        "startAt": startAt,
        "maxResults": maxResults,
        "total": len(filtered_workflows),
        "workflows": paginated_workflows
    }


@mcp.tool()
async def get_workflow_details(workflowId: str) -> Dict:
    """Get detailed information about a specific workflow."""
    logger.info(f"Getting details for workflow {workflowId}")
    
    if workflowId not in WORKFLOWS:
        return {
            "status": "error",
            "message": f"Workflow {workflowId} not found"
        }
    
    return {
        "status": "success",
        "workflow": WORKFLOWS[workflowId]
    }


@mcp.tool()
async def create_workflow(templateId: str, parameters: Optional[Dict] = None) -> Dict:
    """Create a new workflow from a template."""
    logger.info(f"Creating new workflow from template {templateId}")
    
    # Find the template
    template = None
    for tmpl in WORKFLOW_TEMPLATES:
        if tmpl["id"] == templateId:
            template = tmpl
            break
    
    if not template:
        return {
            "status": "error",
            "message": f"Template {templateId} not found"
        }
    
    # Generate new workflow ID
    next_id = len(WORKFLOWS) + 1
    workflow_id = f"WF-{next_id:03d}"
    
    # Current time
    now = datetime.now().isoformat()
    
    # Create steps based on template
    steps = []
    for i, step_name in enumerate(template["steps"]):
        step_id = f"step-{i+1:03d}"
        steps.append({
            "id": step_id,
            "name": step_name,
            "status": "Pending" if i > 0 else "Running",
            "startTime": now if i == 0 else None,
            "endTime": None
        })
    
    # Create the workflow
    new_workflow = {
        "id": workflow_id,
        "name": template["name"],
        "description": template["description"],
        "status": "Running",
        "startTime": now,
        "lastUpdated": now,
        "steps": steps,
        "retries": 0,
        "timeout": "24h"  # Default timeout
    }
    
    # Add parameters if provided
    if parameters:
        new_workflow["parameters"] = parameters
    
    # Store in memory
    WORKFLOWS[workflow_id] = new_workflow
    
    return {
        "status": "success",
        "message": f"Workflow {workflow_id} created successfully",
        "workflow": new_workflow
    }


@mcp.tool()
async def update_workflow_status(workflowId: str, status: str) -> Dict:
    """Update the status of a workflow."""
    logger.info(f"Updating status of workflow {workflowId} to {status}")
    
    if workflowId not in WORKFLOWS:
        return {
            "status": "error",
            "message": f"Workflow {workflowId} not found"
        }
    
    if status not in STATUSES:
        return {
            "status": "error",
            "message": f"Status {status} is not valid. Valid statuses are: {', '.join(STATUSES)}"
        }
    
    workflow = WORKFLOWS[workflowId]
    workflow["status"] = status
    workflow["lastUpdated"] = datetime.now().isoformat()
    
    # Special handling for completed or failed workflows
    if status in ["Completed", "Failed"]:
        # Mark any running steps as completed or failed
        for step in workflow["steps"]:
            if step["status"] == "Running":
                step["status"] = status
                step["endTime"] = workflow["lastUpdated"]
    
    return {
        "status": "success",
        "message": f"Workflow {workflowId} status updated to {status}",
        "workflow": workflow
    }


@mcp.tool()
async def update_step_status(workflowId: str, stepId: str, status: str) -> Dict:
    """Update the status of a workflow step."""
    logger.info(f"Updating status of step {stepId} in workflow {workflowId} to {status}")
    
    if workflowId not in WORKFLOWS:
        return {
            "status": "error",
            "message": f"Workflow {workflowId} not found"
        }
    
    workflow = WORKFLOWS[workflowId]
    step = None
    
    # Find the step
    for s in workflow["steps"]:
        if s["id"] == stepId:
            step = s
            break
    
    if not step:
        return {
            "status": "error",
            "message": f"Step {stepId} not found in workflow {workflowId}"
        }
    
    # Update step status
    step["status"] = status
    now = datetime.now().isoformat()
    
    # Update timestamps based on status
    if status == "Running" and not step["startTime"]:
        step["startTime"] = now
    elif status in ["Completed", "Failed"] and not step["endTime"]:
        step["endTime"] = now
    
    # Update workflow lastUpdated
    workflow["lastUpdated"] = now
    
    # If this is the last step and it's completed, mark the workflow as completed
    if status == "Completed":
        all_completed = True
        for s in workflow["steps"]:
            if s["status"] != "Completed":
                all_completed = False
                break
        
        if all_completed:
            workflow["status"] = "Completed"
    
    # Check if next step should be started
    if status == "Completed":
        # Find current step index
        for i, s in enumerate(workflow["steps"]):
            if s["id"] == stepId and i < len(workflow["steps"]) - 1:
                # Start next step
                next_step = workflow["steps"][i+1]
                next_step["status"] = "Running"
                next_step["startTime"] = now
                break
    
    return {
        "status": "success",
        "message": f"Step {stepId} status updated to {status}",
        "step": step,
        "workflow": workflow
    }


@mcp.tool()
async def retry_workflow(workflowId: str) -> Dict:
    """Retry a failed workflow."""
    logger.info(f"Retrying workflow {workflowId}")
    
    if workflowId not in WORKFLOWS:
        return {
            "status": "error",
            "message": f"Workflow {workflowId} not found"
        }
    
    workflow = WORKFLOWS[workflowId]
    
    if workflow["status"] != "Failed":
        return {
            "status": "error",
            "message": f"Workflow {workflowId} is not in failed status"
        }
    
    # Update workflow status
    workflow["status"] = "Running"
    now = datetime.now().isoformat()
    workflow["lastUpdated"] = now
    workflow["retries"] += 1
    
    # Find the first failed step and mark it as running
    for step in workflow["steps"]:
        if step["status"] == "Failed":
            step["status"] = "Running"
            step["startTime"] = now
            step["endTime"] = None
            break
    
    return {
        "status": "success",
        "message": f"Workflow {workflowId} restarted",
        "workflow": workflow
    }


@mcp.tool()
async def list_workflow_templates() -> Dict:
    """List all available workflow templates."""
    logger.info("Listing workflow templates")
    
    return {
        "status": "success",
        "templates": WORKFLOW_TEMPLATES
    }


@mcp.tool()
async def get_template_details(templateId: str) -> Dict:
    """Get detailed information about a workflow template."""
    logger.info(f"Getting details for template {templateId}")
    
    # Find the template
    template = None
    for tmpl in WORKFLOW_TEMPLATES:
        if tmpl["id"] == templateId:
            template = tmpl
            break
    
    if not template:
        return {
            "status": "error",
            "message": f"Template {templateId} not found"
        }
    
    return {
        "status": "success",
        "template": template
    }


if __name__ == "__main__":
    # Start the server
    print("Starting Temporal Service MCP server...")
    mcp.run(transport="stdio")
    print("Temporal Service MCP server is running.") 