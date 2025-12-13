from typing import Generator
from contextlib import contextmanager
from sqlmodel import Session
from .connection import engine

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency that can be used with FastAPI
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()