from openai import OpenAI
from typing import Dict, List, Any
import json
from database.deps import get_db_session
from models.todo_models import Conversation, Message, MessageRole, TaskStatus
from services.task_service import create_task, get_tasks, update_task, complete_task, delete_task
from datetime import datetime
from sqlmodel import Session, select

class ConversationAgent:
    def __init__(self):
        # Initialize OpenAI client (using a mock for now, replace with actual API key handling)
        # In a real implementation, you would set the API key properly
        self.client = OpenAI(api_key="sk-...")  # This would be set from environment
        self.model = "gpt-4-turbo"  # or another appropriate model

    def run_agent(self, user_input: str, conversation_id: int) -> Dict[str, Any]:
        """
        Run the agent with the user input and return the response
        """
        # Load conversation history
        messages = self.load_conversation_history(conversation_id)

        # Add user message to the conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Define the tools that the agent can use
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The title of the task"},
                            "description": {"type": "string", "description": "The description of the task"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter tasks by status"}
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
                    "description": "Update a task's details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "The ID of the task to update"},
                            "title": {"type": "string", "description": "The new title for the task"}
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

        # Call the OpenAI API with tools
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
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

                    # Execute the actual tool function
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
        Execute the tool function with the provided arguments
        """
        with get_db_session() as session:
            try:
                if function_name == "add_task":
                    title = function_args.get("title")
                    description = function_args.get("description", "")
                    task = create_task(session, title, description)
                    return {
                        "success": True,
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status.value
                    }
                elif function_name == "list_tasks":
                    status = function_args.get("status", "all")
                    from backend.models.todo_models import TaskStatus
                    status_filter = None
                    if status != "all":
                        try:
                            status_filter = TaskStatus(status)
                        except ValueError:
                            return {"error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'"}

                    tasks = get_tasks(session, user_id=1, status=status_filter)  # Using default user_id for now
                    task_list = []
                    for task in tasks:
                        task_list.append({
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status.value,
                            "created_at": task.created_at.isoformat()
                        })

                    return {
                        "tasks": task_list,
                        "total": len(task_list)
                    }
                elif function_name == "complete_task":
                    task_id = function_args.get("task_id")
                    task = complete_task(session, task_id)
                    if task:
                        return {
                            "success": True,
                            "task_id": task.id,
                            "status": task.status.value
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Task with ID {task_id} not found"
                        }
                elif function_name == "delete_task":
                    task_id = function_args.get("task_id")
                    success = delete_task(session, task_id)
                    if success:
                        return {
                            "success": True,
                            "task_id": task_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Task with ID {task_id} not found"
                        }
                elif function_name == "update_task":
                    task_id = function_args.get("task_id")
                    title = function_args.get("title")
                    updated_task = update_task(session, task_id, title=title)
                    if updated_task:
                        return {
                            "success": True,
                            "task_id": updated_task.id,
                            "title": updated_task.title,
                            "description": updated_task.description,
                            "status": updated_task.status.value
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Task with ID {task_id} not found"
                        }
                else:
                    return {"error": f"Unknown function: {function_name}"}
            except Exception as e:
                return {"error": f"Error executing tool {function_name}: {str(e)}"}

    def load_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Load conversation history from the database
        """
        with get_db_session() as session:
            # Query messages for the conversation
            statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
            messages = session.exec(statement).all()

            # Format messages for OpenAI API
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
        Save a message to the conversation in the database
        """
        with get_db_session() as session:
            # Create a new message
            message_role = MessageRole.assistant if role == "assistant" else MessageRole.user
            message = Message(
                conversation_id=conversation_id,
                role=message_role,
                content=content
            )
            session.add(message)
            session.commit()