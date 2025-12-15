"""
Todo Agent

An AI agent that manages todo tasks using the TodoManagementSkill.
This agent uses OpenAI's function calling to determine when to execute
task management operations.
"""

from openai import OpenAI
from typing import Dict, List, Any
import json
from backend.database.deps import get_db_session
from backend.models.todo_models import Conversation, Message, MessageRole
from backend.app.skills.todo_skill import TodoManagementSkill
from datetime import datetime


# Tool definitions for the OpenAI function calling API
TODO_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the task"},
                    "description": {"type": "string", "description": "Optional description of the task"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks or filter by status (all, pending, completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "The ID of the task to complete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "The ID of the task to delete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's details (title, description, or status)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "The ID of the task to update"},
                    "title": {"type": "string", "description": "The new title for the task"},
                    "description": {"type": "string", "description": "The new description for the task"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "The new status for the task"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]


class TodoAgent:
    """
    AI Agent for managing todo tasks.

    This agent uses OpenAI's function calling capability to interpret user
    requests and execute appropriate task management operations via the
    TodoManagementSkill.
    """

    def __init__(self, user_id: int = 1):
        """
        Initialize the TodoAgent.

        Args:
            user_id: The ID of the user this agent is serving
        """
        self.client = OpenAI()
        self.model = "gpt-4-turbo"
        self.user_id = user_id

    def run_agent(self, user_input: str, conversation_id: int) -> Dict[str, Any]:
        """
        Run the agent with the user input and return the response.

        Args:
            user_input: The user's message
            conversation_id: The ID of the conversation

        Returns:
            Dict containing response and conversation_id
        """
        # Load conversation history
        messages = self.load_conversation_history(conversation_id)

        # Add user message to the conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Call the OpenAI API with tools
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TODO_TOOLS,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # If the model wants to call tools, execute them
                tool_results = []
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the tool using TodoManagementSkill
                    result = self.execute_tool(function_name, function_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": json.dumps(result)
                    })

                # Get the final response after tool execution
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages + [response_message] + tool_results,
                )

                final_response = second_response.choices[0].message.content
            else:
                # If no tools were called, return the direct response
                final_response = response_message.content

            # Save the interaction to the conversation
            self.save_message(conversation_id, "user", user_input)
            self.save_message(conversation_id, "assistant", final_response)

            return {
                "response": final_response,
                "conversation_id": conversation_id
            }

        except Exception as e:
            error_msg = f"Error running agent: {str(e)}"
            self.save_message(conversation_id, "assistant", error_msg)
            return {
                "response": error_msg,
                "conversation_id": conversation_id,
                "error": True
            }

    def execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function using the TodoManagementSkill.

        Args:
            function_name: The name of the function to execute
            function_args: The arguments for the function

        Returns:
            Dict containing the result of the tool execution
        """
        with get_db_session() as session:
            # Create skill instance with session and user context
            skill = TodoManagementSkill(session=session, user_id=self.user_id)

            try:
                if function_name == "add_task":
                    return skill.add_task(
                        title=function_args.get("title"),
                        description=function_args.get("description", "")
                    )
                elif function_name == "list_tasks":
                    return skill.list_tasks(
                        status=function_args.get("status", "all")
                    )
                elif function_name == "complete_task":
                    return skill.complete_task(
                        task_id=function_args.get("task_id")
                    )
                elif function_name == "delete_task":
                    return skill.delete_task(
                        task_id=function_args.get("task_id")
                    )
                elif function_name == "update_task":
                    return skill.update_task(
                        task_id=function_args.get("task_id"),
                        title=function_args.get("title"),
                        description=function_args.get("description"),
                        status=function_args.get("status")
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Unknown function: {function_name}",
                        "message": f"The function '{function_name}' is not supported."
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Error executing {function_name}: {str(e)}"
                }

    def load_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Load conversation history from the database.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            List of message dicts formatted for OpenAI API
        """
        with get_db_session() as session:
            from sqlmodel import select
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            messages = session.exec(statement).all()

            formatted_messages = []
            for msg in messages:
                role = "assistant" if msg.role == MessageRole.assistant else "user"
                formatted_messages.append({
                    "role": role,
                    "content": msg.content
                })

            return formatted_messages

    def save_message(self, conversation_id: int, role: str, content: str):
        """
        Save a message to the conversation in the database.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
        """
        with get_db_session() as session:
            message_role = MessageRole.assistant if role == "assistant" else MessageRole.user
            message = Message(
                conversation_id=conversation_id,
                role=message_role,
                content=content
            )
            session.add(message)
            session.commit()
