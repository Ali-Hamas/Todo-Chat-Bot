from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Column, Integer
from typing import Optional
from datetime import datetime

# Define a simple User model with explicit autoincrement
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True))
    email: str = Field(unique=True, index=True)
    name: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create engine
engine = create_engine("sqlite:///./test_explicit_todo.db", echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

print("Tables created successfully with explicit autoincrement!")

# Check the schema
import sqlite3
conn = sqlite3.connect('test_explicit_todo.db')
cursor = conn.cursor()

# Get table info for users
cursor.execute("PRAGMA table_info(users);")
table_info = cursor.fetchall()

print("\nUsers table schema:")
for column in table_info:
    print(f"  {column}")

# Also check the SQL used to create the table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
create_sql = cursor.fetchone()
if create_sql:
    print(f"\nCREATE statement for users table:")
    print(create_sql[0])
else:
    print("\nUsers table not found in sqlite_master")

conn.close()