import asyncio
from contextlib import contextmanager
from mcp.server import Server
from backend.app.skills.todo_skill import TodoManagementSkill
from backend.database.connection import Session, engine

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


def get_skill(session: Session, user_id: int = 1) -> TodoManagementSkill:
    """
    Factory function to create a TodoManagementSkill instance.

    Args:
        session: Database session
        user_id: User ID for the skill context (default: 1)

    Returns:
        TodoManagementSkill instance
    """
    return TodoManagementSkill(session=session, user_id=user_id)


# Define the tools that will be available to the AI agent
@server.tool("add_task")
async def add_task_tool(title: str, description: str = "") -> dict:
    """
    Add a new task to the todo list
    """
    with get_db_session() as session:
        skill = get_skill(session)
        return skill.add_task(title, description)


@server.tool("list_tasks")
async def list_tasks_tool(status: str = "all") -> dict:
    """
    List all tasks or filter by status
    """
    with get_db_session() as session:
        skill = get_skill(session)
        return skill.list_tasks(status)


@server.tool("complete_task")
async def complete_task_tool(task_id: int) -> dict:
    """
    Mark a task as completed
    """
    with get_db_session() as session:
        skill = get_skill(session)
        return skill.complete_task(task_id)


@server.tool("delete_task")
async def delete_task_tool(task_id: int) -> dict:
    """
    Delete a task from the todo list
    """
    with get_db_session() as session:
        skill = get_skill(session)
        return skill.delete_task(task_id)


@server.tool("update_task")
async def update_task_tool(task_id: int, title: str = None, description: str = None, status: str = None) -> dict:
    """
    Update a task's details
    """
    with get_db_session() as session:
        skill = get_skill(session)
        return skill.update_task(task_id, title=title, description=description, status=status)


# Initialize the server
async def serve():
    async with server.serve_over_stdio():
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(serve())
