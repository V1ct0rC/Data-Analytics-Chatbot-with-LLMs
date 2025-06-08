"""
Script to define the base class for LLM providers. This class outlines the methods that any LLM provider 
must implement, such as generating responses and retrieving available models.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.db.models import ChatMessage


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, 
                          prompt: str, 
                          messages: List[ChatMessage], 
                          temperature: float = 0.2,
                          top_p: float = 0.95,
                          top_k: int = 30) -> Dict[str, Any]:
        """
        Generate a response from the LLM based on the provided prompt and conversation history.
        
        Args:
            prompt: The user's prompt
            messages: List of previous messages in the conversation
            temperature: Controls randomness
            top_p: Controls diversity via nucleus sampling
            top_k: Controls diversity by limiting to top K tokens
            
        Returns:
            Dictionary containing the response text and any additional data (charts, etc.)
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return a list of available models for this provider"""
        pass