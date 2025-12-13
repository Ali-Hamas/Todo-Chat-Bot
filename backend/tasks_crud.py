from sqlmodel import Session, select
from typing import List, Optional
from models import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus, Message, MessageRole
from datetime import datetime

def get_user_tasks(db: Session, user_id: str, status_filter: str = "all") -> List[TaskRead]:
    """
    Get all tasks for a user, optionally filtered by status
    """
    query = select(Task).where(Task.user_id == user_id)

    if status_filter != "all":
        try:
            status_enum = TaskStatus(status_filter)
            query = query.where(Task.status == status_enum)
        except ValueError:
            # Invalid status, return empty list or all tasks
            pass

    tasks = db.exec(query).all()
    return [TaskRead.from_orm(task) if hasattr(TaskRead, 'from_orm') else
            TaskRead(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                user_id=task.user_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            ) for task in tasks]

def get_task_by_id(db: Session, task_id: int, user_id: str) -> Optional[Task]:
    """
    Get a specific task by ID for a user
    """
    query = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
    return db.exec(query).first()

def create_task_for_user(db: Session, task_data: TaskCreate, user_id: str) -> TaskRead:
    """
    Create a new task for a user
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=TaskStatus.pending,
        user_id=user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

def update_task(db: Session, task_id: int, user_id: str, task_update: TaskUpdate) -> Optional[TaskRead]:
    """
    Update a task for a user
    """
    task = get_task_by_id(db, task_id, user_id)
    if not task:
        return None

    # Update only the fields that are provided
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status

    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

def delete_task(db: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a task for a user
    """
    task = get_task_by_id(db, task_id, user_id)
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True