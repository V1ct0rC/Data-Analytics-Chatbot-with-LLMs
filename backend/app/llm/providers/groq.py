"""
Groq LLM Provider. Groq is a cloud-based LLM provider that offers several models for generating text responses.
"""
import json
from groq import Groq
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional

from backend.app.llm.providers.base import LLMProvider
from backend.app.llm.agent_functions import (
    query_database, generate_chart, list_tables,
    query_database_declaration, generate_chart_declaration, list_tables_declaration
)
from backend.app.llm.prompt_templates import GROQ_PROMPT_TEMPLATE

from backend.app.db.models import ChatMessage
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_operations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """Groq provider implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        self.available_models = [
            "llama-3.3-70b-versatile", "qwen-qwq-32b", "deepseek-r1-distill-llama-70b"
        ]

        # Define tools for function calling in Groq format
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": query_database_declaration["name"],
                    "description": query_database_declaration["description"],
                    "parameters": query_database_declaration["parameters"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": generate_chart_declaration["name"],
                    "description": generate_chart_declaration["description"],
                    "parameters": generate_chart_declaration["parameters"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": list_tables_declaration["name"],
                    "description": list_tables_declaration["description"],
                    "parameters": list_tables_declaration["parameters"]
                }
            }
        ]

        self.available_functions = {
            "query_database": query_database,
            "generate_chart": generate_chart,
            "list_tables": list_tables
        }
    
    def generate_response(self, prompt: str, messages: List[ChatMessage], model: str = "llama-3.3-70b-versatile",
                          temperature: float = 0.2, top_p: float = 0.95, top_k: int = 30) -> Dict[str, Any]:
        """Generate a response using Groq API"""
        logger.info(f"Generating response with model: {model}, temperature: {temperature}, top_p: {top_p}, top_k: {top_k}")

        # Format messages for Groq API
        formatted_messages = []
        # Add system message
        formatted_messages.append({
            "role": "system",
            "content": GROQ_PROMPT_TEMPLATE
        })
        for msg in messages:
            formatted_messages.append({
                "role": "user" if msg.role == "user" else "assistant",
                "content": msg.content
            })

        # Just a fallback to ensure the last user message is included and to keep working on Gemini
        if not messages or messages[-1].role != "user" or messages[-1].content != prompt:
            formatted_messages.append({
                "role": "user",
                "content": prompt
            })

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1024,
                temperature=temperature,
                top_p=top_p
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call functions
            chart_data = None
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                # Add the response with tool calls to messages
                formatted_messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls
                })
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = self.available_functions.get(function_name)
                    
                    if function_to_call:
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                            function_response = function_to_call(**function_args)
                            
                            # If this is a chart generation function, save the chart data
                            if function_name == "generate_chart" and isinstance(function_response, dict) and function_response.get("success"):
                                chart_data = function_response
                            
                            # Add tool response to messages
                            formatted_messages.append({
                                "role": "tool",
                                "content": json.dumps(function_response),
                                "tool_call_id": tool_call.id
                            })
                        except Exception as e:
                            # If function execution fails, return error
                            formatted_messages.append({
                                "role": "tool",
                                "content": json.dumps({"error": str(e)}),
                                "tool_call_id": tool_call.id
                            })
                
                # Make a second request with function results
                final_response = self.client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    max_tokens=1024,
                    temperature=temperature,
                    top_p=top_p
                )
                
                response_text = final_response.choices[0].message.content
            else:
                # No tool calls, just use the initial response
                response_text = response_message.content
            
            return {
                "response": response_text,
                "chart_data": chart_data
            }
            
        except Exception as e:
            logger.error(f"Error generating response with Groq: {str(e)}")
            logger()
            
            # TODO: Handle specific exceptions if needed. Stop sending the error to the frontend.
            return {
                "response": f"Error with Groq model {model}: {str(e)}",
                "chart_data": None,
            }
    
    def get_available_models(self) -> List[str]:
        """Return available Groq models with descriptions"""
        return self.available_models