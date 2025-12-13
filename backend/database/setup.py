from sqlmodel import SQLModel
from .connection import engine

def create_tables():
    """
    Create all database tables
    """
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")