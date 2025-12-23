# Feature: AI Agent & Chatbot History

## Goal
Implement a "Stateless AI Agent" that understands natural language (NLP) and persists chat history in the Neon PostgreSQL database.

## Database Schema (History)
We need two new tables in `models.py`:
1.  **Conversation**: `id` (int), `user_id` (str), `title` (str), `created_at`.
2.  **Message**: `id` (int), `conversation_id` (FK), `role` (str: "user" or "assistant"), `content` (str).

## The Chat Logic (POST /api/chat)
The endpoint must follow this **exact logic flow** to ensure NLP works:

1.  **Identify User**: Extract `user_id` from the JWT token (Better Auth).
2.  **Load History**: Fetch the last 10 messages for this `conversation_id` from the database.
3.  **Prepare AI Context**:
    -   Create a list of messages: `System Prompt` + `Chat History` + `New User Message`.
    -   **System Prompt**: "You are a helpful Todo Assistant. You have access to tools to manage tasks. ALWAYS use a tool if the user intends to modify or query their list."
4.  **Call OpenAI**:
    -   Use `client.chat.completions.create`.
    -   **Crucial**: Pass the `tools` definitions (derived from our MCP tools).
5.  **Tool Execution Loop**:
    -   If OpenAI returns a `tool_calls` parameter:
        -   Execute the corresponding Python function (e.g., `add_task`).
        -   Feed the tool result *back* to OpenAI as a "tool" role message.
        -   Get the final natural language response.
6.  **Persist**: Save the User's message and the Assistant's final response to the `Message` table.
7.  **Return**: The final natural language string to the frontend.

## Requirements
- **No Regex**: Do not use `if "add" in message`. Rely entirely on OpenAI Function Calling.
- **Multilingual**: The System Prompt should allow replying in the user's language (e.g., Urdu if asked).