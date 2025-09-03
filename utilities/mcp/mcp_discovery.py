import os 
import json

class MCPDiscovery:
    """   
    Discover available MCP servers and their capabilities by reading a configuration file.
    
    Attributes:
        config_path (str): The path to the MCP configuration file.
        config (Dict[str, any]): The loaded configuration data.
    """
    def __init__(self, config_file: str = None):
        
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), "mcp_config.py") 
            self.config_path = config_file
        else:
            self.config_path = config_file
            
        self.config = self._load_config()
            
        
    def _load_config(self) -> dict[str, any]:
        try:
            with open(self.config_path, 'r', encoding="utf8") as file:
                data = json.load(file)
                
                if not isinstance(data, dict):
                    raise ValueError(f"Configuration file {self.config_path} must contain a JSON object.")
                
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")
        except Exception as e:
            raise ValueError(f"Error parsing JSON in configuration file {self.config_path}: {str(e)}")
        
    def list_all_servers(self) -> dict[str, any]:
        """List all available MCP servers from the configuration."""
        if "mcpservers" not in self.config:
            raise KeyError(f"'mcpservers' key not found in configuration file {self.config_path}.")
        return self.config.get("mcpservers", {})