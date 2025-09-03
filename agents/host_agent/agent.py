import os 
from utilities.common.file_loader import load_instruction_file
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools.function_tool import FunctionTool
from collections.abc import AsyncIterable
from google.genai import types
from utilities.mcp import mcp_connect
from utilities.a2a import agent_discovery, agent_connector
from dotenv import load_dotenv
from a2a.types import AgentCard
from uuid import uuid4

load_dotenv()

class HostAgent:
    """
    Orchestrator agent.
    
    - Discover A2A agent via agent discovery
    - Discover MCP servers via MCP connectors and load the MCP tools 
    - Route the user query by picking the correct agents/tools
    """
    def __init__(self):
        """ 
        A simple website builder agent which can create a basic website page and is built with Google's Agent Development Kit.
        """
        
        file_path = os.path.dirname(__file__)
        self.SYSTEM_INSTRUCTION = load_instruction_file(file_path + "/instructions.txt")
        self.DESCRIPTION = load_instruction_file(file_path + "/description.txt")
        
        self.mcp_connector = mcp_connect.MCPConnector()
        self.agent_discovery = agent_discovery.AgentDiscovery()
        
    
    async def create(self):

        self.agent = await self.build_agent()
        self.user_id = "host_agent"
        self.runner = Runner(
            app_name=self.agent.name,
            agent = self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService())
    
    async def list_agents(self) -> list[AgentCard]:
        """
        A2A tool: return the list of agent card of A2A registered agents

        Returns:
            list[AgentCard]:
        """
        cards: list[AgentCard] = await self.agent_discovery.list_agent_cards()
        cards_info = [card.model_dump(exclude_none = True)['name'] for card in cards]
        print("🌴🌴🌴Identified agent cards:", cards_info)
        return  [card.model_dump(exclude_none = True) for card in cards]
    
    
    async def delegate_task(self, agent_name: str, message: str) -> str:
        cards: list[AgentCard] = await self.agent_discovery.list_agent_cards()
        
        matched_card = None
        for card in cards:
            if card.name.lower() == agent_name.lower():
                matched_card = card 
                break 
        
        if matched_card is None:
            return "Agent not found"
        
        connector = agent_connector.AgentConnector(matched_card)
        return await connector.send_task(message=message, 
                            session_id=str(uuid4()))
        
        
        
    async def build_agent(self) -> LlmAgent:
        mcp_tools = await self.mcp_connector.get_tools()
        await self.list_agents()
        
        return LlmAgent(
            name = "HostAgent",
            model="gemini-2.5-flash",
            instruction=self.SYSTEM_INSTRUCTION,
            description=self.DESCRIPTION,
            tools =[FunctionTool(self.delegate_task),
                    FunctionTool(self.list_agents),
                    *mcp_tools]
        )
        
    async def invoke(self, query: str, session_id: str = None) -> AsyncIterable[dict]:
        """ 
        Invoke the agent with the given query and seesion_id and return the response. 
        Return a stream of updates back to the caller as the agent processes the request.
        
        {
            "is_task_complete": bool,
            "updates": str,
            "content": str
        }
        """
        
        session  = await self.runner.session_service.get_session(
            app_name=self.agent.name,
            user_id=self.user_id,
            session_id=session_id
            )
        
        if not session:
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id=self.user_id,
                session_id=session_id
            )
        
        
        user_content = types.Content(
            role="user",
            parts = [types.Part.from_text(text=query)])
        
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session_id,
            new_message=user_content
        ):  
            
            if event.is_final_response():
                final_response = ""
                if event.content and event.content.parts and event.content.parts[-1].text:
                    final_response = event.content.parts[-1].text
                    
                yield {
                    "is_task_complete": True,
                    "content": final_response 
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "The agent is still working on your request..."
                }
            
                
        
        