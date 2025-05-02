# Nexus Agent: MCP & A2A Integration

A multi-agent system demonstrating seamless integration between Agent-to-Agent (A2A) protocol and Model Context Protocol (MCP) for intelligent cloud management and service automation.

## 🌟 Overview

This project showcases a powerful integration between OpenAI Agents, A2A (Agent-to-Agent) protocol, and MCP (Model Context Protocol) to create intelligent agents that can:

- Manage AWS EC2 instances
- Track and update order statuses
- Handle JIRA tickets
- Provide AWS advisory services via Perplexity

The system demonstrates how multiple specialized agents can work together through standardized protocols to solve complex tasks.


## 🏗️ Architecture

This project implements a layered architecture:

```
┌───────────────┐
│  Client Layer │ User interfaces and API endpoints
└───────┬───────┘
        │
┌───────┴───────┐
│   A2A Layer   │ Agent-to-Agent communication protocol
└───────┬───────┘
        │
┌───────┴───────┐
│ Task Managers │ Route and manage tasks for appropriate agents
└───────┬───────┘
        │
┌───────┴───────┐
│  Agent Layer  │ Specialized intelligent agents (JIRA, AWS, Order, etc.)
└───────┬───────┘
        │
┌───────┴───────┐
│   MCP Layer   │ Model Context Protocol for tool execution
└───────┬───────┘
        │
┌───────┴───────┐
│ Service Layer │ Core implementation of business logic and tools
└───────────────┘
```

## 🧩 Components

### 1. AWS EC2 Manager

Allows creation and termination of AWS EC2 instances through natural language commands.

**Tools:**
- `initiate_aws_ec2_instance`: Creates a new AWS EC2 instance
- `terminate_aws_ec2_instance`: Terminates an EC2 instance by ID

### 2. Order Status Manager

Tracks and manages order statuses in a SQLite database.

**Tools:**
- `get_order_status`: Fetch status of a specific order
- `list_all_orders`: List all orders in the system
- `update_order_status`: Update an order's status

### 3. JIRA Ticket Assistant

Manages JIRA tickets in a simulated environment.

**Tools:**
- Ticket creation and management
- Status updates
- Comment handling

### 4. Perplexity AWS Advisor

Provides AWS recommendations and best practices using the Perplexity API.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- AWS credentials (for AWS EC2 functionality)
- OpenAI API key

### Environment Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/nexus_agent_mcp_a2a_hackathon.git
   cd nexus_agent_mcp_a2a_hackathon
   ```

2. Create a `.env` file with the following variables:
   ```
   # OpenAI credentials
   OPENAI_API_KEY=your_openai_api_key
   
   # AWS credentials
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=your_aws_region
   
   # AWS EC2 configuration
   AMI_ID=your_ami_id
   INSTANCE_TYPE=t2.micro
   KEY_NAME=your_key_name
   SECURITY_GROUP_IDS=your_security_group_id
   
   # Optional: Perplexity API key
   PERPLEXITY_API_KEY=your_perplexity_api_key
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

Start the main server that coordinates all agents:

```bash
python run_agent.py
```

This will start a server that initializes all agent services:
- AWS EC2 Manager
- Order Status Manager
- JIRA Ticket Assistant
- Perplexity AWS Advisor

The server will provide URLs for testing each service.

### Running with A2A Client

To use the A2A client interface:

1. Clone the A2A repository in the project root:
   ```bash
   git clone https://github.com/google/A2A.git
   ```

2. Run the UI client:
   ```bash
   cd A2A/demo/ui
   pip install -r requirements.txt
   python main.py
   ```

3. In the client, use natural language to interact with the agents:
   - "Create an EC2 instance"
   - "What's the status of order ORD001?"
   - "Create a JIRA ticket for a bug I found"
   - "What's the best AWS instance for running a web server?"

## 🛠️ Project Structure

- `openai-agent/`: OpenAI agent implementation
- `perplexity-agent/`: Perplexity agent implementation
- `aws.py`: AWS EC2 service implementation
- `order_status.py`: Order management service
- `helper.py`: Utilities for AWS integration
- `run_agent.py`: Main entry point for running all agents


## 📚 Resources

- [A2A Protocol Repository](https://github.com/google/A2A)
- [OpenAI Agents Documentation](https://platform.openai.com/docs/assistants/overview)
- [MCP Protocol Documentation](https://github.com/microsoft/mcp)



