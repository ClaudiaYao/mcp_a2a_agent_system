from a2a.server.agent_execution import AgentExecutor,  RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_task, new_agent_text_message
from agents.host_agent.agent import HostAgent
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState
import asyncio

class HostAgentExecutor(AgentExecutor):
    def __init__(self):
        """
        An executor to run the PostDesignAgent with the provided tools.
        """
        self.agent = HostAgent()
        
    async def create(self):
        await self.agent.create()
        
        
    async def execute(self, request_context: RequestContext, event_queue: EventQueue) -> str:
        
        query = request_context.get_user_input()
        
        task = request_context.current_task
        if not task:
            task = new_task(request_context.message)
            await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        try:
            async for item in self.agent.invoke(query, task.context_id):
                is_task_complete = item.get("is_task_complete", False)
                
                # C: those returned updates are decided by the agent's invoke method design
                if not is_task_complete:
                    message = item.get("updates", "The agent is still working on your request...")
                    await updater.update_status(TaskState.working, new_agent_text_message(message, task.context_id, task.id))
                else:
                    final_result = item.get("content", "no result is received.")
                    await updater.update_status(TaskState.completed, new_agent_text_message(final_result, task.context_id, task.id))
                    return final_result
                    
                await asyncio.sleep(0.1)  # Yield control to the event loop
                
        except Exception as e:
            error_message = f"Error during agent execution: {e}"
            await updater.update_status(TaskState.failed, new_agent_text_message(error_message, task.context_id, task.id))
            raise
        
    async def cancel(self):
        """ Handle any cleanup if the execution is cancelled. """
        
        