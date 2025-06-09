"""
Google Gemini LLM Provider Implementation. This module implements the GeminiProvider class, which interacts with the 
Google Gemini API to generate responses based on user prompts and conversation history.
"""
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional

from backend.app.llm.providers.base import LLMProvider
from backend.app.llm.agent_functions import query_database, generate_chart, list_tables
from backend.app.llm.prompt_templates import GEMINI_PROMPT_TEMPLATE

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

class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.available_models = [
            "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash",
        ]

    def generate_response(self, prompt: str, messages: List[ChatMessage], model: str = "gemini-2.0-flash",
                          temperature: float = 0.2, top_p: float = 0.95, top_k: int = 30) -> Dict[str, Any]:
        """Generate a response using Google Gemini"""
        
        logger.info(f"Generating response with model: {model}, temperature: {temperature}, top_p: {top_p}, top_k: {top_k}")
        config = types.GenerateContentConfig(
            system_instruction=GEMINI_PROMPT_TEMPLATE,
            tools=[query_database, generate_chart, list_tables],
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        # Create a conversation history in Gemini format
        history = []
        for msg in messages:
            content = types.Content(
                role="user" if msg.role == "user" else "model",
                parts=[types.Part(text=msg.content)]
            )
            history.append(content)

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=history,
                config=config,
            )
        except Exception as e:
            # TODO: Handle specific exceptions if needed. Stop sending the error to the frontend.
            logger.error(f"Error generating response: {str(e)}")
            return {"response": f"Error generating response: {str(e)}", "chart_data": None}
        
        response_text = str(response.text)

        # As the agent cannot directly return function call results, we need to check the response for function calls
        # and responses. So we will look for function calls to produce charts on the frontend.
        chart_data = None
        if hasattr(response, 'automatic_function_calling_history'):
            for content in response.automatic_function_calling_history:
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        if hasattr(part, 'function_call') and part.function_call and part.function_call.name == "generate_chart":
                            params = part.function_call.args
                            chart_data = generate_chart(**params)
                        
                        if hasattr(part, 'function_response') and part.function_response and part.function_response.name == "generate_chart":
                            if 'result' in part.function_response.response:
                                chart_data = part.function_response.response['result']
        
        return {
            "response": response_text,
            "chart_data": chart_data
        }
    
    def get_available_models(self) -> List[str]:
        """Return a list of available models for Gemini"""
        return self.available_models
