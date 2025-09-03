import os
from dotenv import load_dotenv

# Load environment variables from .env into os.environ
load_dotenv()

class Config:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    HOST_AGENT_PORT: int = os.getenv("DB_URL", 8080)
    POST_DESIGN_AGENT_PORT: int = os.getenv("POST_DESIGN_AGENT_PORT", 10000)
    MATH_MCP_SERVER_PORT: int = os.getenv("MATH_MCP_SERVER_PORT", 10001)
    
# You can create a global instance if you like
config = Config()
