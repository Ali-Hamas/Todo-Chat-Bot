from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime

# Define a simple User model
from backend.models.todo_models import User

# Create engine
engine = create_engine("sqlite:///./test_todo.db", echo=True)

def test_create_user():
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Test inserting a user
    with Session(engine) as session:
        # Check if user exists first to avoid uniqueness error
        existing = session.exec(select(User).where(User.email == "test@example.com")).first()
        if existing:
            session.delete(existing)
            session.commit()
            
        user = User(
            email="test@example.com",
            name="Test User",
            password="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)  # Refresh to get the generated ID
        print(f"User created with ID: {user.id}")

if __name__ == "__main__":
    test_create_user()