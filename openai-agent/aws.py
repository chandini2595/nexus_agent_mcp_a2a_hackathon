from mcp.server.fastmcp import FastMCP
import httpx
import os
import sys
from dotenv import load_dotenv
import json

# Initialize FastMCP server
mcp = FastMCP("aws-assistant")

# Load environment variables
load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

if not API_KEY:
    print("Error: PERPLEXITY_API_KEY environment variable is not set.")
    print("Please set this in your .env file or environment variables.")

# Perplexity API endpoint
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

async def query_perplexity(prompt: str, model: str = "mixtral-8x7b-instruct"):
    """
    Send a query to the Perplexity API.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use, defaults to mixtral-8x7b-instruct
        
    Returns:
        str: The response from the API
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "options": {
            "temperature": 0.7
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"Error: API returned status code {response.status_code}. {response.text}"
                print(error_msg)
                # Fall back to a simple response when API fails
                return f"I'm sorry, I encountered an error when trying to answer your question about AWS. Error details: {error_msg}. Please try simplifying your question or try again later."
    except Exception as e:
        error_msg = f"Error querying Perplexity API: {str(e)}"
        print(error_msg)
        return f"I'm sorry, I encountered an error when trying to answer your question about AWS. Error details: {error_msg}. Please try again later."

@mcp.tool()
async def get_aws_service_info(service_name: str):
    """
    Get detailed information about a specific AWS service.
    
    Args:
        service_name (str): Name of the AWS service (e.g., "EC2", "S3", "Lambda")
            
    Returns:
        str: Detailed information about the service including features, use cases, and best practices
    """
    prompt = f"""
    Please provide detailed information about the AWS {service_name} service, including:
    
    1. What is AWS {service_name} and its primary purpose
    2. Key features and capabilities 
    3. Common use cases and scenarios
    4. Pricing model and considerations
    5. Best practices for implementation and optimization
    6. Integration with other AWS services
    7. Limitations or service quotas to be aware of
    8. Security best practices specific to this service
    """
    
    return await query_perplexity(prompt)

@mcp.tool()
async def compare_aws_services(services: str):
    """
    Compare specific AWS services to help with decision making.
    
    Args:
        services (str): Comma-separated list of AWS services to compare
            Example: "DynamoDB,MongoDB Atlas,Aurora"
            
    Returns:
        str: Detailed comparison of the specified services
    """
    prompt = f"""
    Please provide a detailed comparison of the following AWS or cloud services: {services}
    
    For each service, include:
    1. Core functionality and purpose
    2. Performance characteristics
    3. Scalability and reliability features
    4. Pricing model and cost considerations
    5. Use cases where this service excels
    6. Limitations or service constraints
    7. Integration capabilities with other services
    8. Management overhead and operational considerations
    """
    
    return await query_perplexity(prompt)

@mcp.tool()
async def get_aws_architecture_pattern(use_case: str):
    """
    Get AWS architecture pattern recommendations for a specific use case.
    
    Args:
        use_case (str): Description of the use case or application type
            Examples: "serverless web application", "data lake", "microservices"
        
    Returns:
        str: Recommended AWS architecture pattern with detailed explanation
    """
    prompt = f"""
    As an AWS solution architect, please recommend a well-architected solution for the following use case:
    
    {use_case}
    
    Your recommendation should include:
    1. A high-level architecture overview
    2. Specific AWS services to use and their roles
    3. How the components connect and interact
    4. Security considerations and implementation
    5. Scaling approach and high availability design
    6. Cost optimization strategies
    7. Deployment and operational best practices
    8. Trade-offs and alternative approaches to consider
    """
    
    return await query_perplexity(prompt)

@mcp.tool()
async def get_aws_cli_examples(task: str):
    """
    Get AWS CLI command examples for specific tasks.
    
    Args:
        task (str): Description of the AWS task you want to accomplish
            Example: "create an S3 bucket with versioning enabled"
        
    Returns:
        str: AWS CLI commands with explanation and examples
    """
    prompt = f"""
    Please provide AWS CLI command examples for the following task:
    
    {task}
    
    Include:
    1. The complete AWS CLI commands with syntax
    2. Explanation of each parameter and option
    3. Common variations of the command for different scenarios
    4. How to validate that the command succeeded
    5. Any related commands that might be needed for the complete workflow
    6. Best practices when using these commands
    """
    
    return await query_perplexity(prompt)

@mcp.tool()
async def answer_aws_question(question: str):
    """
    Answer any general question about AWS services, features, and best practices.
    
    Args:
        question (str): The question about AWS to answer
        
    Returns:
        str: Detailed answer to the AWS question
    """
    prompt = f"""
    As an AWS cloud expert, please answer the following question thoroughly and accurately:
    
    {question}
    
    Include relevant technical details, best practices, and examples where appropriate.
    """
    
    return await query_perplexity(prompt)

if __name__ == "__main__":
    # Start the FastMCP server
    print("Starting AWS Assistant FastMCP server...")
    mcp.run(transport="stdio")
    print("AWS Assistant FastMCP server is running.") 