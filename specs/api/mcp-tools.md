# MCP Server & Tools Specification

## Overview
We need an MCP (Model Context Protocol) server running within our FastAPI backend. This server exposes "Tools" that the AI Agent can call.

## The MCP Server
- **Library**: Use `mcp.server.fastmcp`.
- **Integration**: The MCP server should be mountable or callable from the main FastAPI app.

## Tools to Implement
The following Python functions must be decorated as MCP tools:

1.  **`add_task(title: str, description: str = None)`**
    -   **Description**: Adds a new task to the database for the current user.
    -   **Returns**: JSON string with the new task ID and status.

2.  **`list_tasks(status: str = "all")`**
    -   **Description**: strict filter. If user asks for "unfinished" or "pending", pass "pending". If "done" or "finished", pass "completed".
    -   **Returns**: A JSON list of tasks including ID, title, and status.

3.  **`complete_task(task_id: int)`**
    -   **Description**: Marks a specific task as completed.
    -   **Returns**: Success message with the task title.

4.  **`delete_task(task_id: int)`**
    -   **Description**: Permanently removes a task.
    -   **Returns**: Confirmation message.

## Technical Context
- These tools must interact with the `SQLModel` database session.
- They must be stateless (fetch user context from the function arguments).