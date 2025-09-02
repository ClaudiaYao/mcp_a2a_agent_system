from utilities.mcp.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from mcp import StdioServerParameters

class MCPConnector:
    def __init__(self, config_file: str = None):
        """
        Discover MCP servers from the config file.
        Config will be loaded from MCP Discovery class, then it lists each server's tools
        Cache them as MCP toolset that is compatible with Google's Agent Development Kit
        """
        
        self.discovery = MCPDiscovery(config_file)
        self.tools = []
    
    async def get_tools(self) -> list[MCPToolset]:
        await self._load_all_tools()
        return self.tools.copy()
        
    async def _load_all_tools(self):
        """ 
        Load all tools from discovered MCP servers and cache them as MCPToolset instances. 
        """
        try: 
            servers = self.discovery.list_all_servers()
            for server_name, server_info in servers.items():
                if server_info.get("command") == "streamable-http":
                    conn = StreamableHTTPServerParams(url=server_info["args"][0])
                else:
                    conn = StdioConnectionParams(
                        StdioServerParameters(command=server_info["command"], args=server_info.get("args", [])),
                        timeout = 5)
                    
                toolset = MCPToolset(connection_params=conn, name=server_name)
                tools = await toolset.get_tools()
                tool_names = [tool.name for tool in tools]
                print(f"[bold greeen]Loaded tools from {server_name}: {tool_names}")
                self.tools.append(toolset)
        except Exception as e:
            print(f"[bold red]Error loading tools: {e}[/bold red]")
        
    
    def get_tools(self) -> list[MCPToolset]:
        """ Return the list of cached MCPToolset instances. """
        return self.tools.copy()
        
            
        
            