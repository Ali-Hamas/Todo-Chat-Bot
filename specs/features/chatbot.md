# Feature: AI Chatbot (MCP & Agents)

## Goal
Enable users to manage tasks using natural language via a chat interface.

## Agent Capabilities (MCP Tools)
The Agent must have access to these tools via the MCP Server:
1.  `add_task(title, description)`: Creates a task.
2.  `list_tasks(status)`: Lists tasks (filtering by 'pending', 'completed', or 'all').
3.  `complete_task(task_id)`: Marks a task as done.
4.  `delete_task(task_id)`: Removes a task.
5.  `update_task(task_id, title)`: Updates task details.

## User Stories
- "Add a task to buy milk" -> Agent calls `add_task` -> Responds "Added task: Buy milk".
- "What do I have to do?" -> Agent calls `list_tasks` -> Summarizes pending tasks.
- "I finished task 3" -> Agent calls `complete_task` -> Confirms completion.