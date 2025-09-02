import os 
from utilities.common.file_loader import load_instruction_file
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from collections.abc import AsyncIterable
from google.genai import types 
from dotenv import load_dotenv

load_dotenv()

class PostDesignAgent:
    def __init__(self):
        """ 
        A simple website builder agent which can create a basic website page and is built with Google's Agent Development Kit.
        """
        
        file_path= os.path.dirname(__file__)
        self.SYSTEM_INSTRUCTION = load_instruction_file(file_path + "/instructions.txt")
        self.DESCRIPTION = load_instruction_file(file_path + "/description.txt")
        self.agent = self.build_agent()
        self.user_id = "post_design_agent"
        self.runner = Runner(
            app_name=self.agent.name,
            agent = self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService())
        
    def build_agent(self) -> LlmAgent:
        return LlmAgent(
            name = "PostDesignAgent",
            model="gemini-2.5-flash",
            instruction=self.SYSTEM_INSTRUCTION,
            description=self.DESCRIPTION,
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
            parts = types.Part.from_text(text=query))
        
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session_id,
            new_message=[user_content]
        ):
            if event.is_final_response:
                final_response = ""
                if event.content and event.content.parts and event.conten.parts[-1].text:
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
            
                
        
        