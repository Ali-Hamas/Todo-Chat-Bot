"""
Todo Management Skill

A reusable skill set that allows an AI agent to manage a user's todo list.
This skill encapsulates all CRUD operations and logic for task management,
making it portable to any agent.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime

from backend.models.todo_models import Task, TaskStatus


class TodoManagementSkill:
    """
    A skill class that encapsulates all todo management operations.

    This class provides methods for:
    - add_task: Creates a new task with title and optional description
    - list_tasks: Retrieves tasks, supporting filtering by status
    - update_task: Modifies existing tasks
    - complete_task: Marks a task as done
    - delete_task: Removes a task
    """

    def __init__(self, session: Session, user_id: int):
        """
        Initialize the TodoManagementSkill with a database session and user context.

        Args:
            session: SQLModel database session
            user_id: The ID of the user performing operations (for safety verification)
        """
        self._session = session
        self._user_id = user_id

    @property
    def user_id(self) -> int:
        """Get the current user ID."""
        return self._user_id

    def _verify_task_ownership(self, task: Optional[Task]) -> bool:
        """
        Verify that a task belongs to the current user.

        Args:
            task: The task to verify

        Returns:
            True if the task belongs to the user, False otherwise
        """
        if task is None:
            return False
        return task.user_id == self._user_id

    def _get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID, ensuring it belongs to the current user.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task if found and owned by user, None otherwise
        """
        task = self._session.get(Task, task_id)
        if task and self._verify_task_ownership(task):
            return task
        return None

    def add_task(self, title: str, description: str = "") -> Dict[str, Any]:
        """
        Add a new task to the todo list.

        Args:
            title: The title of the task
            description: Optional description of the task

        Returns:
            A structured JSON response confirming the action
        """
        try:
            task = Task(
                title=title,
                description=description,
                user_id=self._user_id,
                status=TaskStatus.pending
            )
            self._session.add(task)
            self._session.commit()
            self._session.refresh(task)

            return {
                "success": True,
                "action": "add_task",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "message": f"Task '{task.title}' has been created successfully."
            }
        except Exception as e:
            self._session.rollback()
            return {
                "success": False,
                "action": "add_task",
                "error": str(e),
                "message": f"Failed to create task: {str(e)}"
            }

    def list_tasks(self, status: str = "all") -> Dict[str, Any]:
        """
        List all tasks or filter by status.

        Args:
            status: Filter status - 'all', 'pending', or 'completed'

        Returns:
            A structured JSON response with the list of tasks
        """
        try:
            query = select(Task).where(Task.user_id == self._user_id)

            status_filter = None
            if status != "all":
                try:
                    status_filter = TaskStatus(status)
                    query = query.where(Task.status == status_filter)
                except ValueError:
                    return {
                        "success": False,
                        "action": "list_tasks",
                        "error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'",
                        "message": f"Invalid status filter '{status}'. Please use 'all', 'pending', or 'completed'."
                    }

            tasks = self._session.exec(query).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })

            filter_desc = f" with status '{status}'" if status != "all" else ""
            return {
                "success": True,
                "action": "list_tasks",
                "tasks": task_list,
                "total": len(task_list),
                "filter": status,
                "message": f"Found {len(task_list)} task(s){filter_desc}."
            }
        except Exception as e:
            return {
                "success": False,
                "action": "list_tasks",
                "error": str(e),
                "message": f"Failed to retrieve tasks: {str(e)}"
            }

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a task's details.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status - 'pending' or 'completed' (optional)

        Returns:
            A structured JSON response confirming the action
        """
        try:
            task = self._get_task_by_id(task_id)

            if not task:
                return {
                    "success": False,
                    "action": "update_task",
                    "task_id": task_id,
                    "error": f"Task with ID {task_id} not found",
                    "message": f"Could not find task with ID {task_id}. Please check the ID and try again."
                }

            # Track what was updated
            updates = []

            if title is not None:
                task.title = title
                updates.append("title")
            if description is not None:
                task.description = description
                updates.append("description")
            if status is not None:
                try:
                    task.status = TaskStatus(status)
                    updates.append("status")
                except ValueError:
                    return {
                        "success": False,
                        "action": "update_task",
                        "task_id": task_id,
                        "error": f"Invalid status: {status}",
                        "message": f"Invalid status '{status}'. Please use 'pending' or 'completed'."
                    }

            task.updated_at = datetime.utcnow()
            self._session.add(task)
            self._session.commit()
            self._session.refresh(task)

            return {
                "success": True,
                "action": "update_task",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "updated_fields": updates,
                "message": f"Task '{task.title}' has been updated. Changed: {', '.join(updates)}."
            }
        except Exception as e:
            self._session.rollback()
            return {
                "success": False,
                "action": "update_task",
                "task_id": task_id,
                "error": str(e),
                "message": f"Failed to update task: {str(e)}"
            }

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete

        Returns:
            A structured JSON response confirming the action
        """
        try:
            task = self._get_task_by_id(task_id)

            if not task:
                return {
                    "success": False,
                    "action": "complete_task",
                    "task_id": task_id,
                    "error": f"Task with ID {task_id} not found",
                    "message": f"Could not find task with ID {task_id}. Please check the ID and try again."
                }

            # Check if already completed
            if task.status == TaskStatus.completed:
                return {
                    "success": True,
                    "action": "complete_task",
                    "task_id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "message": f"Task '{task.title}' was already marked as completed."
                }

            task.status = TaskStatus.completed
            task.updated_at = datetime.utcnow()
            self._session.add(task)
            self._session.commit()
            self._session.refresh(task)

            return {
                "success": True,
                "action": "complete_task",
                "task_id": task.id,
                "title": task.title,
                "status": task.status.value,
                "message": f"Task '{task.title}' has been marked as completed."
            }
        except Exception as e:
            self._session.rollback()
            return {
                "success": False,
                "action": "complete_task",
                "task_id": task_id,
                "error": str(e),
                "message": f"Failed to complete task: {str(e)}"
            }

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Delete a task from the todo list.

        Args:
            task_id: The ID of the task to delete

        Returns:
            A structured JSON response confirming the action
        """
        try:
            task = self._get_task_by_id(task_id)

            if not task:
                return {
                    "success": False,
                    "action": "delete_task",
                    "task_id": task_id,
                    "error": f"Task with ID {task_id} not found",
                    "message": f"Could not find task with ID {task_id}. Please check the ID and try again."
                }

            task_title = task.title
            self._session.delete(task)
            self._session.commit()

            return {
                "success": True,
                "action": "delete_task",
                "task_id": task_id,
                "title": task_title,
                "message": f"Task '{task_title}' has been deleted successfully."
            }
        except Exception as e:
            self._session.rollback()
            return {
                "success": False,
                "action": "delete_task",
                "task_id": task_id,
                "error": str(e),
                "message": f"Failed to delete task: {str(e)}"
            }
