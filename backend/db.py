from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
# For Neon PostgreSQL: postgresql://username:password@ep-rough-recipe-a5q2haz7.us-east-1.aws.neon.tech/neondb?sslmode=require
# For local PostgreSQL: postgresql://postgres:your_password@localhost:5432/todo_db
# For local development without PostgreSQL, use SQLite: sqlite:///./todo.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# Create the engine
# For SQLite, we need to handle the connection differently
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session