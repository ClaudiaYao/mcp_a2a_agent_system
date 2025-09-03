from a2a.types import AgentCard, SendMessageRequest, MessageSendParams
from a2a.client import A2AClient
import httpx
from uuid import uuid4
from a2a.types import TextPart, Message, Part
import traceback

# logging.basicConfig(level=logging.DEBUG)  # show all logs
# logger = logging.getLogger("a2a")  # capture logs from a2a
# logger.setLevel(logging.DEBUG)


class AgentConnector:
    """
    Connect to remote A2A agents using their AgentCard information and create a unified interface to interact with them.
    """
    
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        
    async def send_task(self, message: str = "", session_id: str = "") -> str:
        """
        Send a request to the remote agent and return the response.
        
        Args:
            user_input (str): The input message to send to the agent.
            
        Returns:
            str: The response from the agent.
        """
        
        async with httpx.AsyncClient(timeout=300) as httpx_client:
            a2a_client = A2AClient(
                httpx_client=httpx_client,
                agent_card = self.agent_card,
            )
            
            send_message_payload = {
                    "role": "user",
                    "message_id": str(uuid4()),
                    "parts": [Part(root=TextPart(text=message))],
                }

            request = SendMessageRequest(
                id = str(uuid4()),
                params = MessageSendParams(
                    message=Message(**send_message_payload))
            )
            
            response = await a2a_client.send_message(request)
            response_data = response.model_dump(mode="json", exclude_none=True)   

            try:
                agent_response = response_data["result"]['status']['message']['parts'][0]['text']
            except (KeyError, IndexError):
                print("💥💥💥 response_data error:", response)
                agent_response = "No response received from the agent." 
                print("❌ A2A Error:")
                traceback.print_exc()
            
            return agent_response
            
