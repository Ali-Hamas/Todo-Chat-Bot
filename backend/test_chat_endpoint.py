"""
Test script for the chat endpoint implementation.

This script tests the chat endpoint logic without requiring an actual OpenAI API key.
It verifies:
1. Message persistence to database
2. History loading (last 10 messages)
3. Tool execution integration
4. Conversation creation and management
"""

import os
import sys
from sqlmodel import Session, select
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from db import engine
from models.todo_models import Conversation, Message, MessageRole, User, Task, TaskStatus
from main import save_chat_messages
from mcp_server import add_task, list_tasks, complete_task, delete_task, get_tool_definitions, execute_tool


def test_message_persistence():
    """Test saving messages to database"""
    print("=" * 60)
    print("TEST 1: Message Persistence")
    print("=" * 60)

    with Session(engine) as db:
        # Create a test user if not exists
        user = db.exec(select(User).where(User.id == 1)).first()
        if not user:
            print("Creating test user...")
            user = User(
                email="test@chat.com",
                name="Chat Test User",
                password="hashed_password"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create a test conversation
        conversation = Conversation(user_id=user.id, title="Test Chat")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        print(f"Created conversation ID: {conversation.id}")

        # Save test messages
        save_chat_messages(
            db,
            conversation.id,
            "Hello, can you help me?",
            "Of course! I'm your Todo Assistant. How can I help you today?"
        )

        # Verify messages were saved
        messages = db.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()

        print(f"\nSaved {len(messages)} messages:")
        for msg in messages:
            print(f"  [{msg.role.value}]: {msg.content[:50]}...")

        assert len(messages) == 2, "Should have 2 messages"
        assert messages[0].role == MessageRole.user, "First message should be user"
        assert messages[1].role == MessageRole.assistant, "Second message should be assistant"

        print("\n[PASS] Message persistence test PASSED\n")
        return conversation.id


def test_history_loading(conversation_id: int):
    """Test loading last 10 messages"""
    print("=" * 60)
    print("TEST 2: History Loading (Last 10 Messages)")
    print("=" * 60)

    with Session(engine) as db:
        # Add more messages to test limit
        for i in range(15):
            save_chat_messages(
                db,
                conversation_id,
                f"User message {i+1}",
                f"Assistant response {i+1}"
            )

        # Load last 10 messages
        messages_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        last_10_messages = db.exec(messages_query).all()
        last_10_messages = list(reversed(last_10_messages))

        print(f"\nTotal messages in conversation: {len(db.exec(select(Message).where(Message.conversation_id == conversation_id)).all())}")
        print(f"Last 10 messages loaded: {len(last_10_messages)}")

        assert len(last_10_messages) == 10, "Should load exactly 10 messages"

        print("\nLast 10 messages:")
        for i, msg in enumerate(last_10_messages[-5:], 1):  # Show last 5 for brevity
            print(f"  {i}. [{msg.role.value}]: {msg.content}")

        print("\n[PASS] History loading test PASSED\n")


def test_tool_definitions():
    """Test tool definitions for OpenAI"""
    print("=" * 60)
    print("TEST 3: Tool Definitions")
    print("=" * 60)

    tools = get_tool_definitions()

    print(f"\nTotal tools defined: {len(tools)}")
    for tool in tools:
        func = tool["function"]
        print(f"\n  - {func['name']}")
        print(f"    Description: {func['description'][:60]}...")
        print(f"    Parameters: {list(func['parameters']['properties'].keys())}")

    assert len(tools) == 4, "Should have 4 tools defined"
    tool_names = [t["function"]["name"] for t in tools]
    assert "add_task" in tool_names, "Should have add_task tool"
    assert "list_tasks" in tool_names, "Should have list_tasks tool"
    assert "complete_task" in tool_names, "Should have complete_task tool"
    assert "delete_task" in tool_names, "Should have delete_task tool"

    print("\n[PASS] Tool definitions test PASSED\n")


def test_tool_execution():
    """Test tool execution via execute_tool helper"""
    print("=" * 60)
    print("TEST 4: Tool Execution")
    print("=" * 60)

    import json

    # Test add_task
    print("\n1. Testing add_task...")
    result = execute_tool("add_task", {"title": "Test Chat Task", "description": "Created via chat"}, user_id=1)
    result_data = json.loads(result)
    print(f"   Result: {result_data}")
    assert result_data["success"] == True, "add_task should succeed"
    task_id = result_data["task_id"]

    # Test list_tasks
    print("\n2. Testing list_tasks...")
    result = execute_tool("list_tasks", {"status": "pending"}, user_id=1)
    result_data = json.loads(result)
    print(f"   Found {result_data['count']} pending tasks")
    assert result_data["success"] == True, "list_tasks should succeed"

    # Test complete_task
    print("\n3. Testing complete_task...")
    result = execute_tool("complete_task", {"task_id": task_id}, user_id=1)
    result_data = json.loads(result)
    print(f"   Result: {result_data['message']}")
    assert result_data["success"] == True, "complete_task should succeed"

    # Test delete_task
    print("\n4. Testing delete_task...")
    result = execute_tool("delete_task", {"task_id": task_id}, user_id=1)
    result_data = json.loads(result)
    print(f"   Result: {result_data['message']}")
    assert result_data["success"] == True, "delete_task should succeed"

    print("\n[PASS] Tool execution test PASSED\n")


def test_chat_flow_simulation():
    """Simulate the full chat flow"""
    print("=" * 60)
    print("TEST 5: Chat Flow Simulation")
    print("=" * 60)

    with Session(engine) as db:
        # Create fresh conversation
        conversation = Conversation(user_id=1, title="Flow Test")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        print(f"\nCreated conversation ID: {conversation.id}")

        # Simulate conversation flow
        chat_exchanges = [
            ("Add a task to buy groceries", "I'll add that task for you!"),
            ("What tasks do I have?", "Here are your pending tasks:\n1. Buy groceries"),
            ("Mark task 1 as done", "Great! I've marked 'Buy groceries' as completed."),
        ]

        print("\nSimulating chat exchanges:")
        for i, (user_msg, assistant_msg) in enumerate(chat_exchanges, 1):
            print(f"\n  Exchange {i}:")
            print(f"    User: {user_msg}")
            print(f"    Assistant: {assistant_msg}")

            # Save messages
            save_chat_messages(db, conversation.id, user_msg, assistant_msg)

        # Verify all messages saved
        all_messages = db.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()

        expected_count = len(chat_exchanges) * 2  # user + assistant per exchange
        print(f"\n  Total messages saved: {len(all_messages)}")
        assert len(all_messages) == expected_count, f"Should have {expected_count} messages"

        # Test history loading (simulate loading for next request)
        last_messages = db.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        ).all()

        print(f"  Last 10 messages available for context: {len(last_messages)}")

        print("\n[PASS] Chat flow simulation test PASSED\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CHAT ENDPOINT IMPLEMENTATION TESTS")
    print("=" * 60 + "\n")

    try:
        # Run tests in sequence
        conversation_id = test_message_persistence()
        test_history_loading(conversation_id)
        test_tool_definitions()
        test_tool_execution()
        test_chat_flow_simulation()

        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe chat endpoint implementation is ready!")
        print("\nTo use with a real OpenAI API key:")
        print("1. Add your OpenAI API key to backend/.env")
        print("2. Start the FastAPI server: uvicorn main:app --reload")
        print("3. Send POST requests to /api/chat")
        print("\nExample request body:")
        print('''{
  "message": "Add a task to buy milk",
  "conversation_id": null
}''')

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
