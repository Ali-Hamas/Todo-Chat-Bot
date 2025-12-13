from openai import OpenAI
from typing import Dict, List, Any
import json
from backend.database.deps import get_db_session
from backend.models.todo_models import Conversation, Message, MessageRole
from datetime import datetime

class TodoAgent:
    def __init__(self):
        # Initialize OpenAI client (using a mock for now, replace with actual API key handling)
        self.client = OpenAI()
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

                    # In a real implementation, you would call the actual tool functions
                    # For now, we'll simulate the result
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
        In a real implementation, this would call the actual MCP tools
        """
        # For now, we'll simulate the tool execution
        # In a real implementation, you would call the actual service functions
        print(f"Executing tool: {function_name} with args: {function_args}")

        # Mock responses for demonstration
        if function_name == "add_task":
            return {
                "success": True,
                "task_id": 1,
                "title": function_args.get("title"),
                "description": function_args.get("description", "")
            }
        elif function_name == "list_tasks":
            return {
                "tasks": [
                    {"id": 1, "title": "Sample task", "status": "pending"}
                ],
                "total": 1
            }
        elif function_name == "complete_task":
            return {
                "success": True,
                "task_id": function_args.get("task_id")
            }
        elif function_name == "delete_task":
            return {
                "success": True,
                "task_id": function_args.get("task_id")
            }
        elif function_name == "update_task":
            return {
                "success": True,
                "task_id": function_args.get("task_id"),
                "title": function_args.get("title")
            }
        else:
            return {"error": f"Unknown function: {function_name}"}

    def load_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Load conversation history from the database
        """
        with get_db_session() as session:
            # Get conversation and messages from DB
            # For now, return an empty list as a placeholder
            # In a real implementation, you would query the DB
            return []

    def save_message(self, conversation_id: int, role: str, content: str):
        """
        Save a message to the conversation in the database
        """
        with get_db_session() as session:
            # Create and save message to DB
            # For now, this is a placeholder
            # In a real implementation, you would create a Message object and save it
            pass