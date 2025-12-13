from backend.database.setup import create_tables
from backend.database.connection import engine, get_session
from backend.services.task_service import create_task, get_tasks
from backend.models.todo_models import User

def test_database():
    # Create tables
    create_tables()
    print("Tables created successfully!")

    # Test creating a task
    with next(get_session()) as session:
        # Create a user first
        user = User(email="test@example.com", name="Test User")
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created user with ID: {user.id}")

        # Create a task
        task = create_task(session, "Test Task", "This is a test task", user.id)
        print(f"Created task: {task.title}")

        # Get tasks
        tasks = get_tasks(session, user.id)
        print(f"Retrieved {len(tasks)} tasks")

        for task in tasks:
            print(f"- Task: {task.title}, Status: {task.status}")

if __name__ == "__main__":
    test_database()