import os
import json
from a2a.types import AgentCard
from a2a.client import A2ACardResolver
import httpx

class AgentDiscovery:
    """
    Disover A2A agents by reading a registry json file of URLs and 
    query each one's /.well-known/agent.json endpoint to retrieve its AgentCard.
    
    Attributes:
        registry_file (str): The path to the agent registry file.
        base_urls (List[str]): The list of base URLs of registered agents.
    """
    
    def __init__(self, registry_file: str = None):
        """
        Initialize the agent discovery with the given registry file.
        Defaults to 'agent_registry.json' in the same directory if not provided.

        Args:
            registry_file (str, optional): _description_. Defaults to None.
        """
        
        if registry_file:
            self.registry_file = registry_file
        else:
            self.registry_file = os.path.join(os.path.dirname(__file__), "agent_registry.json")
            
        self.base_urls = self._load_registry(self.registry_file)
        
    def _load_registry(self, file_path: str) -> list[str]:
        """ 
        Load the registry file and return the list of base URLs.
        
        returns:
        a list of base URLs which represent the registered agents.
        """
        try:
            with open(file_path, 'r', encoding="utf8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Registry file {file_path} not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON in registry file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error loading registry file {file_path}: {str(e)}")
        return data
        
        
    async def list_agent_cards(self) -> list[AgentCard]:
        """ 
        Query each registered agent's /.well-known/agent.json endpoint to retrieve its AgentCard.
        """
        agent_cards: list[AgentCard]= []
        async with httpx.AsyncClient(timeout=300) as httpx_client:
            for base_url in self.base_urls:
                try:
                    resolver = A2ACardResolver(base_url=base_url, httpx_client=httpx_client)
                    card  = await resolver.get_agent_card()
                    if card:
                        agent_cards.append(card)
                        print(f"🌳🌳🌳 Discovered agent: {card.name} at {base_url}")
                    else:
                        print(f"⭐️⭐️⭐️ No AgentCard found at {base_url}")
                except Exception as e:
                    print(f"💥💥💥 Error retrieving AgentCard from {base_url}: {e}")
                    
        return agent_cards