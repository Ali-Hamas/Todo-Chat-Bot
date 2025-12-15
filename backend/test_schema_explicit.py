from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Column, Integer
from typing import Optional
from datetime import datetime

from backend.models.todo_models import User

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