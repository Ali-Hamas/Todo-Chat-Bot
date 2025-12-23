"""
MCP Server & Tools Implementation

This module implements the FastMCP server with tools for task management.
Based on specs/api/mcp-tools.md
"""

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select
from typing import Optional
import json

from db import engine
from models.todo_models import Task, TaskCreate, TaskUpdate, TaskStatus

# Initialize FastMCP server
mcp = FastMCP("Todo MCP Server")


def get_db_session():
    """Get a database session"""
    return Session(engine)


@mcp.tool()
def add_task(title: str, description: str = None, user_id: int = 1) -> str:
    """
    Adds a new task to the database for the current user.

    Args:
        title: The task title
        description: Optional task description
        user_id: The user ID (passed from chat context)

    Returns:
        JSON string with the new task ID and status
    """
    with get_db_session() as db:
        task = Task(
            title=title,
            description=description,
            status=TaskStatus.pending,
            user_id=user_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        result = {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "status": task.status.value,
            "message": f"Task '{title}' added successfully"
        }
        return json.dumps(result)


@mcp.tool()
def list_tasks(status: str = "all", user_id: int = 1) -> str:
    """
    List tasks with strict filter. If user asks for "unfinished" or "pending",
    pass "pending". If "done" or "finished", pass "completed".

    Args:
        status: Filter by status - "all", "pending", or "completed"
        user_id: The user ID (passed from chat context)

    Returns:
        A JSON list of tasks including ID, title, and status
    """
    with get_db_session() as db:
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status != "all":
            # Normalize status strings
            if status.lower() in ["unfinished", "pending"]:
                query = query.where(Task.status == TaskStatus.pending)
            elif status.lower() in ["done", "finished", "completed"]:
                query = query.where(Task.status == TaskStatus.completed)

        tasks = db.exec(query).all()

        # Format tasks for return
        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        result = {
            "success": True,
            "count": len(task_list),
            "tasks": task_list,
            "filter": status
        }
        return json.dumps(result)


@mcp.tool()
def complete_task(task_id: int, user_id: int = 1) -> str:
    """
    Marks a specific task as completed.

    Args:
        task_id: The ID of the task to complete
        user_id: The user ID (passed from chat context)

    Returns:
        Success message with the task title
    """
    with get_db_session() as db:
        # Get the task
        query = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = db.exec(query).first()

        if not task:
            result = {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }
            return json.dumps(result)

        # Mark as completed
        task.status = TaskStatus.completed
        db.add(task)
        db.commit()
        db.refresh(task)

        result = {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "status": task.status.value,
            "message": f"Task '{task.title}' marked as completed"
        }
        return json.dumps(result)


@mcp.tool()
def delete_task(task_id: int, user_id: int = 1) -> str:
    """
    Permanently removes a task.

    Args:
        task_id: The ID of the task to delete
        user_id: The user ID (passed from chat context)

    Returns:
        Confirmation message
    """
    with get_db_session() as db:
        # Get the task
        query = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = db.exec(query).first()

        if not task:
            result = {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }
            return json.dumps(result)

        # Store title before deletion
        task_title = task.title

        # Delete the task
        db.delete(task)
        db.commit()

        result = {
            "success": True,
            "task_id": task_id,
            "title": task_title,
            "message": f"Task '{task_title}' has been permanently deleted"
        }
        return json.dumps(result)


# Function to get tool definitions for OpenAI
def get_tool_definitions():
    """
    Get OpenAI-compatible tool definitions for function calling

    Returns:
        List of tool definitions in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Adds a new task to the database for the current user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks. Use 'pending' for unfinished/pending tasks, 'completed' for done/finished tasks, or 'all' for all tasks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter by status: 'all', 'pending', or 'completed'"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Marks a specific task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Permanently removes a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]


# Function to execute tools (for OpenAI function calling)
def execute_tool(tool_name: str, arguments: dict, user_id: int) -> str:
    """
    Execute a tool by name with the given arguments

    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        user_id: The user ID for context

    Returns:
        JSON string result from the tool
    """
    # Add user_id to arguments
    arguments["user_id"] = user_id

    # Map tool names to functions
    tools = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task
    }

    if tool_name not in tools:
        return json.dumps({
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        })

    # Execute the tool
    try:
        return tools[tool_name](**arguments)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error executing {tool_name}: {str(e)}"
        })


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
