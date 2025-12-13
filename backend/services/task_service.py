from sqlmodel import Session, select
from typing import List, Optional
from backend.models.todo_models import Task, TaskStatus
from datetime import datetime

def create_task(session: Session, title: str, description: Optional[str] = None, user_id: int = 1) -> Task:
    """
    Create a new task in the database
    """
    task = Task(
        title=title,
        description=description,
        user_id=user_id,
        status=TaskStatus.pending
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_tasks(session: Session, user_id: int = 1, status: Optional[TaskStatus] = None) -> List[Task]:
    """
    Get all tasks for a user, optionally filtered by status
    """
    query = select(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)

    tasks = session.exec(query).all()
    return tasks

def update_task(session: Session, task_id: int, title: Optional[str] = None,
                description: Optional[str] = None, status: Optional[TaskStatus] = None) -> Optional[Task]:
    """
    Update an existing task
    """
    task = session.get(Task, task_id)
    if not task:
        return None

    # Update only the fields that are provided
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def complete_task(session: Session, task_id: int) -> Optional[Task]:
    """
    Mark a task as completed
    """
    task = session.get(Task, task_id)
    if not task:
        return None

    task.status = TaskStatus.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def delete_task(session: Session, task_id: int) -> bool:
    """
    Delete a task from the database
    """
    task = session.get(Task, task_id)
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True