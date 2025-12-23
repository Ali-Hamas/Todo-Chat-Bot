"""
Test script for schema_update.md compliance

This script verifies that the database schema matches the specification
in specs/database/schema_update.md
"""

import sys
from sqlmodel import Session, select

from db import engine
from models.todo_models import User, Conversation, Message, MessageRole


def test_conversation_schema():
    """Verify Conversation table matches schema_update.md"""
    print("=" * 60)
    print("TEST 1: Conversation Table Schema")
    print("=" * 60)

    # Check fields
    print("\nConversation model fields:")
    print("  - id: int (Primary Key)")
    print("  - user_id: int (Indexed, Foreign Key to Users)")
    print("  - title: str (Optional)")
    print("  - created_at: datetime")

    with Session(engine) as session:
        # Create test user
        user = User(email="conv_test@example.com", name="Conv Test", password="test")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create conversation
        conv = Conversation(user_id=user.id, title="Test Conversation")
        session.add(conv)
        session.commit()
        session.refresh(conv)

        # Verify fields exist
        assert conv.id is not None, "Conversation should have id"
        assert conv.user_id == user.id, "Conversation should have user_id"
        assert conv.title == "Test Conversation", "Conversation should have title"
        assert conv.created_at is not None, "Conversation should have created_at"

        # Verify NO updated_at field (per schema_update.md)
        assert not hasattr(conv, 'updated_at'), "Conversation should NOT have updated_at field"

        print("\n[PASS] Conversation schema matches specification")
        return conv.id


def test_message_schema(conversation_id: int):
    """Verify Message table matches schema_update.md"""
    print("\n" + "=" * 60)
    print("TEST 2: Message Table Schema")
    print("=" * 60)

    print("\nMessage model fields:")
    print("  - id: int (Primary Key)")
    print("  - conversation_id: int (Foreign Key to Conversation)")
    print("  - role: str (Enum: 'user', 'assistant', 'system', 'tool')")
    print("  - content: text")
    print("  - created_at: datetime")

    with Session(engine) as session:
        # Create messages with all role types
        test_messages = [
            Message(
                conversation_id=conversation_id,
                role=MessageRole.system,
                content="System prompt message"
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.user,
                content="User query message"
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.assistant,
                content="Assistant response message"
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.tool,
                content="Tool execution result message"
            ),
        ]

        for msg in test_messages:
            session.add(msg)
        session.commit()

        # Verify all messages saved
        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()

        assert len(messages) == 4, "Should have 4 messages"

        # Verify all role types
        roles_found = {msg.role for msg in messages}
        expected_roles = {MessageRole.system, MessageRole.user, MessageRole.assistant, MessageRole.tool}
        assert roles_found == expected_roles, f"Should have all role types: {expected_roles}"

        print("\nMessage roles verified:")
        for msg in messages:
            print(f"  - {msg.role.value}: {msg.content[:30]}...")

        print("\n[PASS] Message schema matches specification")


def test_relationships():
    """Verify relationships as specified in schema_update.md"""
    print("\n" + "=" * 60)
    print("TEST 3: Relationships")
    print("=" * 60)

    print("\nRelationship requirements:")
    print("  - A User has many Conversations")
    print("  - A Conversation has many Messages")

    with Session(engine) as session:
        # Create user with multiple conversations
        user = User(email="rel_test@example.com", name="Relationship Test", password="test")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create multiple conversations
        convs = [
            Conversation(user_id=user.id, title=f"Conversation {i}")
            for i in range(1, 4)
        ]
        for conv in convs:
            session.add(conv)
        session.commit()

        # Create messages for each conversation
        for conv in convs:
            for j in range(2):
                msg = Message(
                    conversation_id=conv.id,
                    role=MessageRole.user if j == 0 else MessageRole.assistant,
                    content=f"Message {j} in conversation {conv.id}"
                )
                session.add(msg)
        session.commit()

        # Verify User -> Conversations relationship
        user_convs = session.exec(
            select(Conversation).where(Conversation.user_id == user.id)
        ).all()
        assert len(user_convs) == 3, "User should have 3 conversations"
        print(f"\n  User has {len(user_convs)} conversations")

        # Verify Conversation -> Messages relationship
        for conv in user_convs:
            conv_msgs = session.exec(
                select(Message).where(Message.conversation_id == conv.id)
            ).all()
            assert len(conv_msgs) == 2, f"Conversation {conv.id} should have 2 messages"
            print(f"  Conversation {conv.id} has {len(conv_msgs)} messages")

        print("\n[PASS] Relationships work correctly")


def test_indexed_user_id():
    """Verify user_id is indexed in Conversation table"""
    print("\n" + "=" * 60)
    print("TEST 4: Indexed Fields")
    print("=" * 60)

    print("\nVerifying user_id index on conversations table...")

    # This is verified by the SQLModel Field definition
    # In the model: user_id: int = Field(foreign_key="users.id", index=True)

    import sqlite3
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # Check for index
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='conversations'")
    indexes = cursor.fetchall()
    conn.close()

    index_names = [idx[0] for idx in indexes]
    assert any('user_id' in name for name in index_names), "conversations.user_id should be indexed"

    print(f"  Indexes found: {', '.join(index_names)}")
    print("\n[PASS] user_id is properly indexed")


def main():
    """Run all schema compliance tests"""
    print("\n" + "=" * 60)
    print("SCHEMA UPDATE COMPLIANCE TESTS")
    print("Testing: specs/database/schema_update.md")
    print("=" * 60 + "\n")

    try:
        conv_id = test_conversation_schema()
        test_message_schema(conv_id)
        test_relationships()
        test_indexed_user_id()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nDatabase schema matches specs/database/schema_update.md")
        print("\nVerified:")
        print("  - Conversation table structure")
        print("  - Message table structure with all role types")
        print("  - User -> Conversations relationship")
        print("  - Conversation -> Messages relationship")
        print("  - Indexed user_id field")

        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
