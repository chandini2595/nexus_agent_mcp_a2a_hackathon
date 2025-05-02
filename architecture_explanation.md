# OpenAI Agent Architecture

## Architecture Overview

The OpenAI Agent system is built using a layered architecture that provides a flexible framework for creating AI agents that can interact with various services. The architecture follows a modular design pattern, with clear separation of concerns between different components. Below is a detailed explanation of each layer and component.

### Client Layer
- **Web Client/User**: The entry point for user interactions. Clients make HTTP requests to various service endpoints.

### A2A Layer (Agent-to-Agent Communication)
- **A2A Server Interface**: The base interface for Agent-to-Agent (A2A) communication.
- **JiraA2AServer/AwsA2AServer/OrderA2AServer/TemporalA2AServer**: Specialized server implementations that handle specific service domains (JIRA, AWS, Order management, and Workflow orchestration respectively).

### Task Management Layer
- **Common Task Manager**: Base implementation for task management.
- **JiraTaskManager/AwsTaskManager/OrderTaskManager/TemporalTaskManager**: Domain-specific task managers that handle routing tasks to the appropriate agent and managing the lifecycle of these tasks.

### Agent Layer
- **Generic Agent**: Base agent class providing common functionality.
- **JiraAgent/AwsAgent/OrderAgent/TemporalAgent**: Specialized agents that understand specific domains and can interact with corresponding MCP servers.

### MCP (Message Communication Protocol) Layer
- **MCPServer**: Interface for MCP server communication.
- **MCPServerStdio**: Implementation of MCP server that communicates over stdin/stdout.

### Service Layer
- **FastMCP**: A framework for creating MCP-compatible services.
- **JiraService/AwsService/OrderService/TemporalService**: Domain-specific services that implement business logic and expose functionality through MCP tools.

### Storage Layer
- **In-memory Ticket Storage**: For JIRA service, a simple in-memory storage for ticket data.
- **In-memory Workflow Storage**: For Temporal service, a simple in-memory storage for workflow data.

## Data Flow

1. A client sends a request to one of the A2A servers.
2. The A2A server delegates the task to its corresponding task manager.
3. The task manager invokes the appropriate agent to handle the request.
4. The agent uses the MCP server to communicate with the service.
5. The MCP server launches the service process (if not already running).
6. The service processes the request and sends a response back through the MCP server.
7. The response follows the reverse path back to the client.

## JIRA Service Implementation

The JIRA service is a dummy implementation that mimics a real JIRA ticket system:

1. It maintains an in-memory storage of tickets.
2. It exposes various tools for ticket management through FastMCP:
   - `test_jira_auth`: Test authentication with JIRA API
   - `search_jira_issues`: Search for JIRA issues using JQL
   - `create_jira_issue`: Create a new JIRA issue
   - `update_jira_issue`: Update an existing JIRA issue
   - `get_jira_comments`: Get comments for a JIRA issue
   - `add_jira_comment`: Add a comment to a JIRA issue
   - `get_jira_transitions`: Get available transitions for a JIRA issue
   - `transition_jira_status`: Transition the status of a JIRA issue
   - `transition_jira_status_by_name`: Transition the status by name

3. Special handling is implemented for the "JIRA-001" issue to always return a static response when queried.

## Temporal Service Implementation

The Temporal service implements a workflow orchestration system that mimics Temporal's durable execution:

1. It maintains an in-memory storage of workflows and workflow templates.
2. It exposes various tools for workflow management through FastMCP:
   - `test_temporal_connection`: Test connection with Temporal service
   - `list_workflows`: List all workflows with optional filtering
   - `get_workflow_details`: Get detailed information about a workflow
   - `create_workflow`: Create a new workflow from a template
   - `update_workflow_status`: Update the status of a workflow
   - `update_step_status`: Update the status of a workflow step
   - `retry_workflow`: Retry a failed workflow
   - `list_workflow_templates`: List all available workflow templates
   - `get_template_details`: Get details about a workflow template

3. The service implements workflow state transitions and handles step sequencing automatically.

## Key Design Patterns

1. **Dependency Injection**: Agents accept MCP servers as optional parameters.
2. **Factory Pattern**: The `run_agent` function acts as a factory for creating agent instances.
3. **Repository Pattern**: Services act as repositories for their respective data (tickets, workflows).
4. **Adapter Pattern**: MCP servers adapt between different communication protocols.
5. **Command Pattern**: Each MCP tool is essentially a command that can be executed.
6. **State Machine**: The Temporal service implements a state machine for workflow execution.

## Extension Points

The architecture supports easy extension through:

1. Creating new agents for different domains
2. Implementing new services that expose tools through FastMCP
3. Adding new A2A servers for new communication channels
4. Extending existing services with additional tools

This modular design allows for scalable development and easy integration of new capabilities. 