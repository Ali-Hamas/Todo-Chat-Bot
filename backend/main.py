from fastapi import FastAPI, Depends, HTTPException, status, Form, Body
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
import os
import asyncio

from db import get_session, engine
from models.todo_models import Task, TaskCreate, TaskUpdate, TaskRead, User, Conversation, Message, MessageRole
from tasks_crud import get_user_tasks, get_task_by_id, create_task_for_user, update_task, delete_task
from auth import get_current_user
from sqlmodel import SQLModel

app = FastAPI(title="Todo API", version="1.0.0")

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://localhost:3000", "https://127.0.0.1:3000", "http://127.0.0.1:8000", "http://localhost:8000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# JWT and password hashing setup
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_tables():
    """
    Create all database tables
    """
    # Drop all existing tables and recreate them to ensure correct schema
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def create_default_users(db: Session):
    """
    Create default/pre-existing users if they don't exist
    """
    default_users = [
        {
            "email": "admin@example.com",
            "name": "Admin User",
            "password": "admin123"  # This will be hashed
        },
        {
            "email": "demo@example.com",
            "name": "Demo User",
            "password": "demo123"  # This will be hashed
        },
        {
            "email": "test@example.com",
            "name": "Test User",
            "password": "test123"  # This will be hashed
        }
    ]

    # Process each user individually to ensure proper ID assignment
    for user_data in default_users:
        existing_user = db.exec(select(User).where(User.email == user_data["email"])).first()

        if not existing_user:
            # Hash the password
            hashed_password = get_password_hash(user_data["password"])

            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password=hashed_password
            )

            db.add(user)
            db.commit()  # Commit each user individually to trigger ID generation
            db.refresh(user)  # Refresh to get the generated ID
            print(f"Created default user: {user_data['email']}")
        else:
            print(f"Default user already exists: {user_data['email']}")

    print("Default users setup completed")

def on_startup():
    # Create tables
    create_tables()

    # Create default users
    with Session(engine) as session:
        create_default_users(session)


# Register the startup event
@app.on_event("startup")
def startup_event():
    on_startup()

# Define Pydantic models for request body
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    """Request model for the chat endpoint per spec."""
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str
    conversation_id: int

@app.post("/auth/register", response_model=dict)
def register_user(
    register_data: RegisterRequest,
    db: Session = Depends(get_session)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.exec(select(User).where(User.email == register_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(register_data.password)

    # Create new user
    user = User(
        email=register_data.email,
        name=register_data.name,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "name": user.name}}


@app.post("/auth/login", response_model=dict)
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_session)
):
    """Authenticate user and return access token."""
    # Find user by email
    user = db.exec(select(User).where(User.email == login_data.email)).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "name": user.name}}

@app.get("/api/tasks", response_model=List[TaskRead])
def list_tasks(
    status_filter: str = "all",
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """List all tasks for authenticated user."""
    tasks = get_user_tasks(db, current_user_id, status_filter)
    return tasks


@app.post("/api/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Create a new task."""
    task = create_task_for_user(db, task_data, current_user_id)
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: int,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Update a task."""
    task = update_task(db, task_id, current_user_id, task_update)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete a task."""
    success = delete_task(db, task_id, current_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return



@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Todo API is running!"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_assistant(
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Stateless chat endpoint that processes messages via OpenAI Agent.

    Per spec: Receives a message, processes it via OpenAI Agent,
    executes MCP tools, saves state to DB, and returns response.

    The endpoint is stateless - all conversation history is persisted
    to Neon DB and loaded fresh for each request.
    """
    user_message = chat_request.message
    conversation_id = chat_request.conversation_id

    # Validate user_id
    try:
        user_id_int = int(current_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    # If no conversation_id is provided, create a new conversation
    if not conversation_id:
        conversation = Conversation(user_id=user_id_int)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
    else:
        # Verify conversation exists and belongs to user
        conversation = db.exec(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id_int)
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    # Process via OpenAI Agent (stateless - agent loads history from DB)
    try:
        result = await run_agent_for_chat(
            user_id=user_id_int,
            user_message=user_message,
            conversation_id=conversation_id,
            db=db
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"]
        )
    except Exception as e:
        # Fallback to simple processing if agent fails
        response_text = process_user_message_fallback(user_message, current_user_id, db)

        # Save messages to DB
        save_chat_messages(db, conversation_id, user_message, response_text)

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id
        )


async def run_agent_for_chat(
    user_id: int,
    user_message: str,
    conversation_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Run the OpenAI Agent for chat processing.

    This function is stateless - it loads conversation history from DB,
    runs the agent, and saves the result back to DB.
    """
    # Import agent components (lazy import to avoid circular deps)
    from agent import TodoAgentRunner

    # Create runner (stateless - no server state held)
    runner = TodoAgentRunner(user_id=user_id)

    # Run the agent asynchronously
    result = await runner.run(user_message, conversation_id)

    return result


def save_chat_messages(db: Session, conversation_id: int, user_message: str, assistant_response: str):
    """Save user and assistant messages to the database."""
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.user,
        content=user_message
    )
    db.add(user_msg)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.assistant,
        content=assistant_response
    )
    db.add(assistant_msg)
    db.commit()


def process_user_message_fallback(message: str, user_id: str, db: Session) -> str:
    """
    Fallback message processor when OpenAI Agent is unavailable.
    Uses simple pattern matching for basic task operations.
    """
    message_lower = message.lower()

    # Handle task-related commands
    if "add task" in message_lower or "create task" in message_lower:
        task_title = message_lower.replace("add task", "").replace("create task", "").strip()
        if not task_title:
            return "Please specify what task you'd like to add. For example: 'Add task Buy groceries'"

        task_data = TaskCreate(title=task_title, description="Added via chat")
        task = create_task_for_user(db, task_data, user_id)
        return f"Task '{task.title}' has been added successfully!"

    elif "list task" in message_lower or "show task" in message_lower or "my task" in message_lower:
        tasks = get_user_tasks(db, user_id, "all")
        if not tasks:
            return "You don't have any tasks yet. Try adding one!"

        task_list = []
        for task in tasks:
            status_emoji = "✅" if task.status.value == "completed" else "⏳"
            task_list.append(f"{status_emoji} {task.id}. {task.title}")

        return "Here are your tasks:\n" + "\n".join(task_list)

    elif "complete task" in message_lower or "finish task" in message_lower:
        import re
        task_id_match = re.search(r'\d+', message)
        if task_id_match:
            task_id = int(task_id_match.group())
            task = get_task_by_id(db, task_id, user_id)
            if task:
                task_update = TaskUpdate(status="completed")
                updated_task = update_task(db, task_id, user_id, task_update)
                if updated_task:
                    return f"Task '{updated_task.title}' has been marked as completed!"
                return f"Failed to update task {task_id}."
            return f"Task {task_id} not found or you don't have permission to access it."
        return "Please specify which task to complete. For example: 'Complete task 1'"

    elif "delete task" in message_lower or "remove task" in message_lower:
        import re
        task_id_match = re.search(r'\d+', message)
        if task_id_match:
            task_id = int(task_id_match.group())
            task = get_task_by_id(db, task_id, user_id)
            if task:
                success = delete_task(db, task_id, user_id)
                if success:
                    return f"Task '{task.title}' has been deleted successfully!"
                return f"Failed to delete task {task_id}."
            return f"Task {task_id} not found or you don't have permission to access it."
        return "Please specify which task to delete. For example: 'Delete task 1'"

    elif "help" in message_lower:
        return ("I can help you manage your tasks! Try commands like:\n"
                "- 'Add task [task name]' to create a new task\n"
                "- 'List tasks' to see your tasks\n"
                "- 'Show my tasks' to see your tasks\n"
                "- 'Complete task [id]' to mark a task as completed\n"
                "- 'Delete task [id]' to remove a task")

    else:
        return f"I received your message: '{message}'. I can help you manage your tasks. Type 'help' to see what I can do!"


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)