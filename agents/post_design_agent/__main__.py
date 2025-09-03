from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import click
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agents.post_design_agent.agent_executor import PostDesignAgentExecutor
from a2a.server.apps import A2AStarletteApplication
import uvicorn
from config import config


@click.command()
@click.option('--host', default='localhost', help='Host for the agent server.')
@click.option('--port', default=int(config.POST_DESIGN_AGENT_PORT), help='Port for the agent server.')
def main(host: str, port: int):
    skill = AgentSkill(
        name="PostDesignAgent",
        id="post_design_agent",
        description="A simple post design agent which can create a post title, subtitle, highlight and is built with Google's Agent Development Kit.",
        tags =["post design", "google adk", "llm agent"],
        examples=["""create a post for a school activity which organize primary school students to attend coding lessons""",
                """create a post for a travel blog about visiting Japan"""],
    )

    card = AgentCard(
        name="PostDesignAgent",
        description="A simple post design agent which can create a post title, subtitle, highlight and is built with Google's Agent Development Kit.",
        skills=[skill],
        capabilities=AgentCapabilities(streaming=True, multi_turn=True),
        url=f"http://{host}:{port}/",
        version="1.0",
        default_input_modes=["text"],
        default_output_modes=["text"]
    )
    
    request_handler = DefaultRequestHandler(
        agent_executor=PostDesignAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler
    )
    
    uvicorn.run(server.build(), host=host, port=port)
    
if __name__ == "__main__":
    main()