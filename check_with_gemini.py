# /// script
# dependencies = [
#   "mcp[cli]",
# ]
# ///

import asyncio
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("check_with_gemini")

@mcp.tool()
async def check_with_gemini(prompt: str, content: str) -> str:
    """
    A flexible tool to solicit feedback from Gemini on any topic or content. Supports 
    code reviews, validation, alternative approaches, best practices, and general feedback.
    
    Args:
        prompt: The task or question for Gemini to perform
        content: The text content for Gemini to analyze
    
    Returns:
        Gemini's response to the prompt and content
    
    Examples:
        - Code Review: 
          prompt="Review this Python function for best practices and potential issues"
          content="def calculate_sum(nums): return sum(nums)"
          
        - Security Check:
          prompt="Analyze this code for security vulnerabilities"
          content="[code snippet]"
          
        - Alternative Implementation:
          prompt="Suggest a more efficient algorithm for this sorting function"
          content="[current implementation]"
          
        - Architecture Validation:
          prompt="Evaluate this system design for scalability"
          content="[architecture description]"
          
        - General Feedback:
          prompt="What are your thoughts on this approach?"
          content="[approach description]"
    """
    # Validate inputs
    if not prompt.strip():
        return "Error: prompt cannot be empty"
    
    # Format the complete prompt for Gemini
    formatted_prompt = f"""{prompt}

Content:
{content}"""
    
    try:
        # Create subprocess to call gemini CLI
        process = await asyncio.create_subprocess_exec(
            "gemini",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Communicate with timeout of 30 seconds
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=formatted_prompt.encode()),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Gemini request timed out after 30 seconds"
        
        if process.returncode != 0:
            return f"Error calling gemini tool: {stderr.decode()}"
        
        return stdout.decode()
        
    except FileNotFoundError:
        return "Error: 'gemini' CLI tool not found. Please ensure it is installed and in PATH"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
