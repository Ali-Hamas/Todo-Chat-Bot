# Database Schema for Chat History

## New Tables
We need to persist chat history. Update `models.py` to include:

1.  **Table: Conversation**
    -   `id`: int (Primary Key)
    -   `user_id`: str (Indexed, Foreign Key to Users)
    -   `title`: str (Optional, auto-generated summary)
    -   `created_at`: datetime

2.  **Table: Message**
    -   `id`: int (Primary Key)
    -   `conversation_id`: int (Foreign Key to Conversation)
    -   `role`: str (Enum: "user", "assistant", "system", "tool")
    -   `content`: text
    -   `created_at`: datetime

## Relationships
- A `User` has many `Conversations`.
- A `Conversation` has many `Messages`.