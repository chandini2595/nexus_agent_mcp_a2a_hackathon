# 🚀 Multi-Agent System: A2A & MCP Integration POC

POC: Integrating A2A, MCP, and OpenAI Agents for AWS Tasks 🖥️✨


---

## 🎥 Demo Video

Watch the demo video to see MCP-AWS in action! 🚀

[![Watch the Demo](https://img.youtube.com/vi/FeGmKmsYcRc/0.jpg)](https://youtu.be/FeGmKmsYcRc)

---


## 🌟 Features

1. 🚀 **Seamless Protocol Integration**: Demonstrates the successful integration of the Agent-to-Agent (A2A) protocol with a Model Context Protocol (MCP) server for robust multi-agent communication.

2. 🧠 **Leverages OpenAI Agents SDK**: Built upon the powerful OpenAI Agents SDK to create intelligent agents capable of understanding and acting on user prompts.

3. ☁️ **Automated Cloud Management**: Enables direct provisioning and termination of AWS EC2 instances through simple user interactions, showcasing practical tool execution via the MCP.

---

## 🛠️ Tools in the MCP Server

The MCP server is a custom server with two tools:
1. **`initiate_aws_ec2_instance`**: Creates an AWS EC2 instance.
2. **`terminate_aws_ec2_instance`**: Terminates an AWS EC2 instance by its ID.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.12+** (for local setup) or **Docker** (for containerized setup)
2. **AWS IAM Role**: Create an IAM role with the necessary permissions to manage EC2 instances.
3. **Environment Variables**: Prepare a `.env` file with the following variables:
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    - `AWS_DEFAULT_REGION`
    - `OPENAI_API_KEY`
    - `AMI_ID`
    - `INSTANCE_TYPE`
    - `KEY_NAME`
    - `SECURITY_GROUP_IDS`
    - `AWS_REGION`

### 🏃‍♂️ Running the App
1. Clone the repository at the root:
     ```bash
     git clone https://github.com/anirban1592/google_openai_mcp.git
     cd google_openai_mcp
     ```
2. Create `.env` file as shown in prerequisites

3. Run the remote agent example:
     ```bash
     cd openai-agent/
     uv run .     
     ```
3. Clone the A2A client code(by google) at the root dir:
     ```bash
     git clone https://github.com/google/A2A.git
     cd demo/ui
     ```
4. Create an environment file with your API key or enter it directly in the UI when prompted:
     ```bash
     echo "GOOGLE_API_KEY=your_api_key_here" >> .env
     ```
5. Run the front end example:
     ```bash
    uv run main.py
     ```
6. Refer to the attached video to see it in action

### 💬 Using the AI Agent

1. To create an EC2 instance:
    ```
    Enter your command: Create an EC2 instance
    ```

2. To terminate an EC2 instance:
    ```
    Enter your command: Terminate EC2 instance with ID <instance-id>
    ```

## ⚠️ Word of Caution

- **IAM Role and Credentials**: Please create AWS IAM roles and credentials at your own risk. Ensure you follow AWS best practices for security.
- **Billing and Security**: This app is a proof of concept (POC) and is intended for learning purposes only. We are not responsible for any billing issues or security incidents.

## 📚 Learnings

This project demonstrates:
1. How to integrate MCP servers with OpenAI Agents SDK
2. How to build a simple AI-driven application for AWS resource management

Enjoy exploring the power of AI and MCP servers! 🌟

# A2A Agents Demo with MCP

This repository contains a collection of A2A (Agent-to-Agent) remote agents that demonstrate the use of the MCP (Model Completion Provider) framework.

## Prerequisites

- Python 3.10 or higher
- Poetry or uv for dependency management
- OpenAI API key

## Setup

1. Clone the repository
2. Install dependencies using uv or Poetry:

```
uv venv
uv pip install -r requirements.txt
```

or

```
poetry install
```

3. Set up your environment variables:

```
export OPENAI_API_KEY=your_openai_api_key
```

For AWS EC2 agent:
```
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_key
export AWS_REGION=your_aws_region
export AMI_ID=your_ami_id
export INSTANCE_TYPE=t2.micro
export KEY_NAME=your_key_name
export SECURITY_GROUP_IDS=your_security_group_id
```

## Available Agents

### 1. AWS EC2 Instance Manager

This agent allows you to create and terminate AWS EC2 instances.

**Features:**
- Create a new EC2 instance with predefined configuration
- Terminate an existing EC2 instance by ID

**Run the agent:**
```
cd openai-agent
python __main__.py --host localhost --port 10001
```

Example queries:
- "Create an EC2 instance for me"
- "Terminate EC2 instance i-1234567890abcdef0"

### 2. Order Status Agent

This agent allows you to track and manage order statuses stored in a local SQLite database.

**Features:**
- Check the status of a specific order
- List all orders in the system
- Update the status of an existing order

**Run the agent:**
```
cd openai-agent
python order_main.py --host localhost --port 10002
```

Example queries:
- "What's the status of order ORD001?"
- "List all my orders"
- "Update the status of order ORD002 to Delivered"

### 3. Perplexity AWS Advisor Agent

This agent provides AWS recommendations and general knowledge using the Perplexity API.

**Features:**
- Get EC2 instance recommendations based on workload description
- Compare specific AWS EC2 instance types
- Get AWS cost optimization tips
- Ask general questions about AWS services
- Get AWS architecture recommendations

**Run the agent:**
```
python perplexity_server.py --host localhost --port 10003
```

**Additional setup:**
Add your Perplexity API key to the .env file:
```
PERPLEXITY_API_KEY=your_perplexity_api_key
```

Example queries:
- "What's the best AWS instance for running a high-traffic web application with MySQL database?"
- "Compare t3.large, m5.xlarge, and c5.2xlarge instances"
- "How can I optimize my AWS costs?"
- "What architecture would you recommend for a serverless e-commerce platform?"

## Architecture

Each agent follows a similar architecture:
1. An MCP server that provides the core functionality (order_status.py, aws.py)
2. An Agent class that integrates with the OpenAI API
3. A Task Manager that handles incoming requests
4. A main entry point to start the server

## Contributing

Feel free to contribute to this project by adding new agents or improving existing ones.
