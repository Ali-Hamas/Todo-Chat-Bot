# Database Schema - Phase III

## New Tables

### conversations
- `id`: integer (primary key)
- `user_id`: string (foreign key -> users.id)
- `created_at`: timestamp
- `updated_at`: timestamp

### messages
- `id`: integer (primary key)
- `conversation_id`: integer (foreign key -> conversations.id)
- `role`: string (enum: "user", "assistant")
- `content`: text
- `created_at`: timestamp