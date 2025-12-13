from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import enum

# Define the TaskStatus enum
class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"

# User model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password: str  # Add password field
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Base model for tasks
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.pending)

# Model for creating tasks
class TaskCreate(TaskBase):
    title: str
    description: Optional[str] = None

# Model for updating tasks
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

# Model for reading tasks (with ID)
class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# Complete Task model for database
class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: User = Relationship()

# Conversation model (from specs)
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Message model (from specs)
class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Conversation = Relationship()