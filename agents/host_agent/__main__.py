from a2a.types import AgentSkill, AgentCard, AgentCapabilities

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agents.host_agent.agent_executor import HostAgentExecutor
from a2a.server.apps import A2AStarletteApplication
import uvicorn
import asyncio
import asyncclick as click
from config import config

@click.command()
@click.option('--host', default='localhost', help='Host for the agent server.')
@click.option('--port', default=int(config.HOST_AGENT_PORT), help='Port for the agent server.')
async def main(host: str, port: int):
    skill = AgentSkill(
        name="HostAgent",
        id="host_agent",
        description="A host agent which could use all the registered agents or MCP tools",
        tags =["host agent", "A2A", "MCP server"],
        examples=["""Use the registered sub agents or MCP tools to solve the problem"""],
    )

    card = AgentCard(
        name="HostAgent",
        description="An agent orchestrator which could use all the registered agents or MCP tools",
        skills=[skill],
        capabilities=AgentCapabilities(streaming=True, multi_turn=True),
        url=f"http://{host}:{port}/",
        version="1.0",
        default_input_modes=["text"],
        default_output_modes=["text"]
    )
    
    host_agent_executor = HostAgentExecutor()
    await host_agent_executor.create()
    
    request_handler = DefaultRequestHandler(
        agent_executor=host_agent_executor,
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler
    )
    
    config = uvicorn.Config(server.build(), host =host, port=port)
    server_instance = uvicorn.Server(config)
    await server_instance.serve()
    
if __name__ == "__main__":
    asyncio.run(main())