from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime

# Define a simple User model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create engine
engine = create_engine("sqlite:///./test_todo.db", echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

print("Tables created successfully!")

# Test inserting a user
with Session(engine) as session:
    user = User(
        email="test@example.com",
        name="Test User",
        password="hashed_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)  # Refresh to get the generated ID
    print(f"User created with ID: {user.id}")