import os
from dotenv import load_dotenv

def apply_env():
    """
    Apply environment variables from .env file to the current environment.
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Check if PERPLEXITY_API_KEY is set
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("Warning: PERPLEXITY_API_KEY environment variable is not set.")
        print("Set this in your .env file or export it to your environment.")
        
    # Check OpenAI API key (needed for agent functionality)
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Set this in your .env file or export it to your environment.")
    
    # Set default API model if not specified
    if not os.getenv("OPENAI_API_MODEL"):
        os.environ["OPENAI_API_MODEL"] = "gpt-4-turbo"


if __name__ == "__main__":
    apply_env()
    print("Environment variables applied.")
    