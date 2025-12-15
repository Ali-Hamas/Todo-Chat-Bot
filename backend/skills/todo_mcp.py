"""
Todo List Management MCP Server

This module implements the Model Context Protocol (MCP) server for todo list management.
It provides tools for CRUD operations on tasks using the Official MCP SDK and SQLModel.

Spec Reference: specs/skills/todo_management.md
"""

import asyncio
from contextlib import contextmanager
from typing import Optional, List, Any
from datetime import datetime

from mcp import Server
from sqlmodel import Session, select

from backend.database.connection import engine
from backend.models.todo_models import Task, TaskStatus


# Create MCP server instance
mcp_server = Server("todo-skill-mcp-server")


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


def _get_task_for_user(session: Session, task_id: int, user_id: str) -> Optional[Task]:
    """
    Retrieve a task by ID ensuring it belongs to the specified user.

    Args:
        session: Database session
        task_id: The ID of the task
        user_id: The ID of the user (as string per spec)

    Returns:
        Task if found and owned by user, None otherwise
    """
    try:
        user_id_int = int(user_id)
    except ValueError:
        return None

    task = session.get(Task, task_id)
    if task and task.user_id == user_id_int:
        return task
    return None


# =============================================================================
# MCP Tool Implementations (per spec)
# =============================================================================

@mcp_server.tool("add_task")
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Create a new task.

    Args:
        user_id: The ID of the user (required)
        title: The title of the task (required)
        description: Optional description of the task

    Returns:
        JSON object containing task_id, status, and title
    """
    with get_db_session() as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {
                "error": f"Invalid user_id: {user_id}",
                "status": "error"
            }

        try:
            task = Task(
                title=title,
                description=description if description else None,
                user_id=user_id_int,
                status=TaskStatus.pending
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": task.status.value,
                "title": task.title
            }
        except Exception as e:
            session.rollback()
            return {
                "error": str(e),
                "status": "error"
            }


@mcp_server.tool("list_tasks")
async def list_tasks(user_id: str, status: str = "all") -> dict:
    """
    Retrieve tasks from the list.

    Args:
        user_id: The ID of the user (required)
        status: Filter by status - "all", "pending", or "completed" (optional)

    Returns:
        Array of task objects
    """
    with get_db_session() as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {
                "error": f"Invalid user_id: {user_id}",
                "tasks": []
            }

        try:
            query = select(Task).where(Task.user_id == user_id_int)

            # Apply status filter if not "all"
            if status != "all":
                try:
                    status_enum = TaskStatus(status)
                    query = query.where(Task.status == status_enum)
                except ValueError:
                    return {
                        "error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'",
                        "tasks": []
                    }

            tasks = session.exec(query).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })

            return {"tasks": task_list}

        except Exception as e:
            return {
                "error": str(e),
                "tasks": []
            }


@mcp_server.tool("update_task")
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Modify task title or description.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to update (required)
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        JSON object with status: "updated"
    """
    with get_db_session() as session:
        task = _get_task_for_user(session, task_id, user_id)

        if not task:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "updated",
                "task_id": task.id,
                "title": task.title,
                "description": task.description
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "error",
                "error": str(e)
            }


@mcp_server.tool("complete_task")
async def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to complete (required)

    Returns:
        JSON object with status: "completed"
    """
    with get_db_session() as session:
        task = _get_task_for_user(session, task_id, user_id)

        if not task:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            task.status = TaskStatus.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            return {
                "status": "completed",
                "task_id": task.id
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "error",
                "error": str(e)
            }


@mcp_server.tool("delete_task")
async def delete_task(user_id: str, task_id: int) -> dict:
    """
    Remove a task.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to delete (required)

    Returns:
        JSON object with status: "deleted"
    """
    with get_db_session() as session:
        task = _get_task_for_user(session, task_id, user_id)

        if not task:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            session.delete(task)
            session.commit()

            return {
                "status": "deleted",
                "task_id": task_id
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "error",
                "error": str(e)
            }


# =============================================================================
# Server Entry Point
# =============================================================================

async def serve():
    """
    Start the MCP server over stdio.

    This function runs the server indefinitely, handling incoming
    tool requests from connected clients.
    """
    async with mcp_server.serve_over_stdio():
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(serve())
