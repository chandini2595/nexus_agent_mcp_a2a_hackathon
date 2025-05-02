#!/bin/bash

# Set the script directory as the working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -q python-dotenv httpx starlette uvicorn openai-agents

# Make sure perplexity API key is set
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "Warning: PERPLEXITY_API_KEY environment variable is not set."
    echo "Please set this variable or add it to a .env file."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "Creating .env file. Please edit it to add your API keys."
        echo "PERPLEXITY_API_KEY=" > .env
        echo "OPENAI_API_KEY=" >> .env
    fi
fi

# Run the AWS agent server
echo "Starting AWS Agent server on port 10003..."
python run_aws_agent.py 