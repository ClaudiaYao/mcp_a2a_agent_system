from uuid import uuid4
import asyncclick as click
from utilities.a2a import agent_connector
from a2a.client import A2ACardResolver
import httpx
import asyncio
from config import config


@click.command()
@click.option("--agent_url", default=f"http://localhost:{config.HOST_AGENT_PORT}", help ="base url of A2A host agent.")
@click.option("--session", default=0, help="session ID (use 0 to generate a new ID)")
async def cli (agent_url: str, session: int):
    """
    CLI to send a message to an agent using A2A client and display the response

    Args:
        agent_url (str): _description_
        session_id (str): _description_
    """

    if not session: 
        session_id = uuid4().hex
    else:
        session_id = session 
    
    
    # C: the first step is to find host_agent_card by using the given host_agent_url. This step is not wrapped in the class, so need to define here
    host_agent_card = None
    async with httpx.AsyncClient(timeout=300) as httpx_client:
        try:
            resolver = A2ACardResolver(base_url=agent_url, httpx_client=httpx_client)
            host_agent_card  = await resolver.get_agent_card()
            if host_agent_card:
                print(f"🌳🌳🌳 Discovered agent: {host_agent_card.name} at {agent_url}")
            else:
                print(f"⭐️⭐️⭐️ No AgentCard found at {agent_url}")
        except Exception as e:
            print(f"💥💥💥 Error retrieving AgentCard from {agent_url}: {e}")
    
    # C: connect to the host agent
    connector = agent_connector.AgentConnector(host_agent_card)
    
    while True:
        prompt = click.prompt("\nwhat do you want to send the host agent (press q: or quit to exit):")
        if prompt.strip().lower() in ["q:", "quit"]:
            break 
        
        # C: send task to host agent
        response = await connector.send_task(prompt, session_id)
        print("Response 🚀🚀🚀 =>", response)
    
        
if __name__ == "__main__":
    asyncio(cli())
    
    
    
