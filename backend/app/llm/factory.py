"""
This factory is a design pattern used to manage and instantiate different LLM provider 
classes (like Gemini, Groq, etc.) in a unified way. It abstracts the creation of different 
LLM provider instances and largely improves the system's scalability.
"""
import os
from typing import List, Dict, Optional

from backend.app.llm.providers.base import LLMProvider
from backend.app.llm.providers.gemini import GeminiProvider
from backend.app.llm.providers.groq import GroqProvider


class LLMProviderFactory:
    """Factory class to create and manage LLM providers"""
    _providers: Dict[str, LLMProvider] = {}

    _provider_classes = {
        "gemini": (GeminiProvider, "GEMINI_API_KEY"),
        "groq": (GroqProvider, "GROQ_API_KEY"),
    }

    @classmethod
    def _initialize_providers(self):
        for name, (provider_cls, env_var) in self._provider_classes.items():
            api_key = os.getenv(env_var)
            if api_key:
                self._providers[name] = provider_cls(api_key=api_key)

    @classmethod
    def get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get an instance of the specified LLM provider"""
        self._initialize_providers()
        return self._providers.get(provider_name, None)
    
    @classmethod
    def get_available_providers(self) -> List[str]:
        """Get a list of available LLM providers"""
        self._initialize_providers()
        return list(self._providers.keys())