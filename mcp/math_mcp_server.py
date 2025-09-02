import asyncio
import logging
import os

from fastmcp import FastMCP 
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

class ArithmaticInput(BaseModel):
    a: float = Field(..., description="The first number.")
    b: float = Field(..., description="The second number.")
    
class ArithmaticOutput(BaseModel):
    result: float = Field(..., description="The result of the operation.")      
    expression: str = Field(..., description="The expression that was evaluated.")
    

mcp = FastMCP("demo_math_mcp")

@mcp.tool()
def add(input: ArithmaticInput) -> ArithmaticOutput:
    """Use this to add two numbers together.
    
    Args:
        input(ArithmaticInput): The input containing two numbers to add.
    
    Returns:
        output(ArithmaticOutput): The output containing the result and expression.
    """
    result = input.a + input.b
    expression = f"🏃‍♀️‍➡️🏃‍♀️‍➡️🏃‍♀️‍➡️ {input.a} + {input.b} = {result}"
    logger.info(f">>> Tool: 'add' called with numbers '{input.a}' and '{input.b}'")
    return ArithmaticOutput(result=result, expression=expression)


@mcp.tool()
def subtract(input: ArithmaticInput) -> ArithmaticOutput:
    """Use this to subtract two numbers.
    
    Args:
        input(ArithmaticInput): The input containing two numbers to subtract.
    
    Returns:
        output(ArithmaticOutput): The output containing the result and expression.
    """
    result = input.a - input.b
    expression = f"👏👏👏 {input.a} - {input.b} = {result}"
    logger.info(f">>> Tool: 'subtract' called with numbers '{input.a}' and '{input.b}'")
    return ArithmaticOutput(result=result, expression=expression)

@mcp.tool() 
def multiply(input: ArithmaticInput) -> ArithmaticOutput:
    """Use this to multiply two numbers together.
    
    Args:
        input(ArithmaticInput): The input containing two numbers to multiply.
    
    Returns:
        output(ArithmaticOutput): The output containing the result and expression.
    """
    result = input.a * input.b
    expression = f"🤖🤖🤖 {input.a} * {input.b} = {result}"
    logger.info(f">>> Tool: 'multiply' called with numbers '{input.a}' and '{input.b}'")
    return ArithmaticOutput(result=result, expression=expression)

@mcp.tool() 
def divide(input: ArithmaticInput) -> ArithmaticOutput:
    """Use this to divide two numbers.
    
    Args:
        input(ArithmaticInput): The input containing two numbers to divide.
    
    Returns:
        output(ArithmaticOutput): The output containing the result and expression.
    """
    if input.b == 0:
        raise ValueError("Division by zero is not allowed.")
    result = input.a / input.b
    expression = f"🎃🎃🎃 {input.a} / {input.b} = {result}"
    logger.info(f">>> Tool: 'divide' called with numbers '{input.a}' and '{input.b}'")
    return ArithmaticOutput(result=result, expression=expression)

if __name__ == "__main__":
    logger.info(f" MCP server started on port {os.getenv('PORT', 10001)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="streamable-http", 
            host="0.0.0.0", 
            port=os.getenv("PORT", 10001),
        )
    )