from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
# For Neon PostgreSQL: postgresql://username:password@ep-rough-recipe-a5q2haz7.us-east-1.aws.neon.tech/neondb?sslmode=require
# For local PostgreSQL: postgresql://username:password@localhost:5432/tododb
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/tododb")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session