import asyncio
from contextlib import contextmanager
from mcp import Server
from backend.services.task_service import create_task, get_tasks, update_task, complete_task, delete_task
from backend.database.connection import Session, engine
from backend.models.todo_models import TaskStatus

# Create MCP server instance
server = Server("todo-mcp-server")

@contextmanager
def get_db_session():
    """
    Context manager for database sessions
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

# Define the tools that will be available to the AI agent
@server.tool("add_task")
async def add_task_tool(title: str, description: str = "") -> dict:
    """
    Add a new task to the todo list
    """
    with get_db_session() as session:
        task = create_task(session, title, description)
        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value
        }

@server.tool("list_tasks")
async def list_tasks_tool(status: str = "all") -> dict:
    """
    List all tasks or filter by status
    """
    with get_db_session() as session:
        user_id = 1  # Default user for now
        status_filter = None

        if status != "all":
            try:
                status_filter = TaskStatus(status)
            except ValueError:
                return {"error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'"}

        tasks = get_tasks(session, user_id, status_filter)

        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat()
            })

        return {
            "tasks": task_list,
            "total": len(task_list)
        }

@server.tool("complete_task")
async def complete_task_tool(task_id: int) -> dict:
    """
    Mark a task as completed
    """
    with get_db_session() as session:
        task = complete_task(session, task_id)
        if task:
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value
            }
        else:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

@server.tool("delete_task")
async def delete_task_tool(task_id: int) -> dict:
    """
    Delete a task from the todo list
    """
    with get_db_session() as session:
        success = delete_task(session, task_id)
        if success:
            return {
                "success": True,
                "task_id": task_id
            }
        else:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

@server.tool("update_task")
async def update_task_tool(task_id: int, title: str = None) -> dict:
    """
    Update a task's details
    """
    with get_db_session() as session:
        updated_task = update_task(session, task_id, title=title)
        if updated_task:
            return {
                "success": True,
                "task_id": updated_task.id,
                "title": updated_task.title,
                "description": updated_task.description,
                "status": updated_task.status.value
            }
        else:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

# Initialize the server
async def serve():
    async with server.serve_over_stdio():
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(serve())