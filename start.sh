#!/bin/bash

# Set working directory to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Force set OPENAI_API_KEY for testing if not set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Setting placeholder OPENAI_API_KEY for testing"
    export OPENAI_API_KEY="sk-test-key-for-debugging"
fi

# Force set PERPLEXITY_API_KEY for testing if not set
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "Setting placeholder PERPLEXITY_API_KEY for testing"
    export PERPLEXITY_API_KEY="pplx-test-key-for-debugging"
fi

# Kill any previous running agents
echo "Stopping any running agents..."
pkill -f "python jira_main.py" || true
pkill -f "python order_status.py" || true
pkill -f "python aws.py" || true

# Wait a moment to ensure ports are freed
sleep 2

# Start the JIRA agent
echo "Starting JIRA agent..."
cd "$(dirname "$0")/openai-agent" 
python jira_main.py > ../jira_agent.log 2>&1 &
JIRA_PID=$!
cd ..

# Start the Order Status agent
echo "Starting Order Status agent..."
python order_status.py > order_status.log 2>&1 &
ORDER_PID=$!

# Start the AWS agent
echo "Starting AWS agent..."
python aws.py > aws_agent.log 2>&1 &
AWS_PID=$!

# Print process IDs
echo "Agent PIDs:"
echo "JIRA agent: $JIRA_PID"
echo "Order Status agent: $ORDER_PID"
echo "AWS agent: $AWS_PID"

echo "All agents started! To stop them, run:"
echo "pkill -f \"python jira_main.py\""
echo "pkill -f \"python order_status.py\""
echo "pkill -f \"python aws.py\""

echo "To check logs:"
echo "tail -f jira_agent.log"
echo "tail -f order_status.log"
echo "tail -f aws_agent.log" 