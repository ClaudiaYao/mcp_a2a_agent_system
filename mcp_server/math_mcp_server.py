import logging
import os

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from config import config

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

class ArithmaticInput(BaseModel):
    a: float = Field(..., description="The first number.")
    b: float = Field(..., description="The second number.")
    
class ArithmaticOutput(BaseModel):
    result: float = Field(..., description="The result of the operation.")      
    expression: str = Field(..., description="The expression that was evaluated.")
    

mcp = FastMCP("math_server",
               host ="localhost",
               port = config.MATH_MCP_SERVER_PORT,
               stateless_http = True)

@mcp.tool(name = "add_two_numbers")
def add_numbers(input: ArithmaticInput) -> ArithmaticOutput:
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


@mcp.tool(name = "subtract_two_numbers")
def subtract_numbers(input: ArithmaticInput) -> ArithmaticOutput:
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

@mcp.tool(name = "multiply_two_numbers") 
def multiply_numbers(input: ArithmaticInput) -> ArithmaticOutput:
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

@mcp.tool(name = "divide_two_numbers") 
def divide_numbers(input: ArithmaticInput) -> ArithmaticOutput:
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
    logger.info(f"MCP server started on port {os.getenv('PORT', int(config.MATH_MCP_SERVER_PORT))}")
    mcp.run(transport="streamable-http")