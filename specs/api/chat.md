# Chat API Endpoints

## POST /api/{user_id}/chat

**Description:** Stateless endpoint. Receives a message, processes it via OpenAI Agent, executes MCP tools, saves state to DB, and returns response.

**Request:**
```json
{
  "conversation_id": 123, (optional)
  "message": "Buy eggs"
}