# Skill: Todo List Management (MCP Server)

## Purpose
[cite_start]This skill provides Model Context Protocol (MCP) tools that allow an AI agent to perform CRUD operations on the user's todo list[cite: 414].

## Tool Definitions
[cite_start]The following tools must be implemented using the Official MCP SDK and SQLModel[cite: 421, 422].

### 1. add_task
- **Purpose:** Create a new task.
- **Parameters:**
  - `user_id` (string, required)
  - `title` (string, required)
  - `description` (string, optional)
- [cite_start]**Returns:** JSON object containing `task_id`, `status`, and `title` [cite: 450-451].

### 2. list_tasks
- **Purpose:** Retrieve tasks from the list.
- **Parameters:**
  - `user_id` (string, required)
  - `status` (string, optional: "all", "pending", "completed")
- [cite_start]**Returns:** Array of task objects [cite: 455-456].

### 3. update_task
- **Purpose:** Modify task title or description.
- **Parameters:**
  - `user_id` (string, required)
  - `task_id` (integer, required)
  - `title` (string, optional)
  - `description` (string, optional)
- [cite_start]**Returns:** JSON object with `status: "updated"` [cite: 461-462].

### 4. complete_task
- **Purpose:** Mark a task as complete.
- **Parameters:** `user_id`, `task_id`
- [cite_start]**Returns:** JSON object with `status: "completed"` [cite: 457-458].

### 5. delete_task
- **Purpose:** Remove a task.
- **Parameters:** `user_id`, `task_id`
- [cite_start]**Returns:** JSON object with `status: "deleted"` [cite: 459-460].