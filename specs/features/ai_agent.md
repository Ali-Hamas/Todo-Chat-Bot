# Feature: AI Agent with MCP Tools

## Core Logic (The "Brain")
The `/api/chat` endpoint must NOT use simple string matching. It must use the `OpenAI Agents SDK` or standard `openai.chat.completions` with **Tool Calling**.

## MCP Tools Integration
We must define an MCP Server that exposes these Python functions as tools to the AI:
1.  `add_task(title, description)`
2.  `list_tasks(status)`
3.  `complete_task(task_id)`
4.  `delete_task(task_id)`

## The Request Flow (Step-by-Step)
When the backend receives a POST request at `/api/chat`:
1.  **Authenticate**: Validate the User via Better Auth.
2.  **Retrieve Context**: Fetch the last 10 messages from the `Message` table for this conversation.
3.  **System Prompt**: "You are a helpful Todo Assistant. You act on behalf of the user. If the user wants to add, view, or modify tasks, you MUST call the provided tools. Do not ask for confirmation unless necessary."
4.  **AI Decision**: Send the User Message + History + Tools to OpenAI.
5.  **Tool Execution**:
    -   **CRITICAL**: If OpenAI returns a `tool_call` (e.g., `add_task`), the backend must execute that Python function immediately.
    -   Capture the result of the function.
    -   Send the result back to OpenAI to generate the final natural language response.
6.  **Persist**: Save the User message and the final Assistant response to the DB.