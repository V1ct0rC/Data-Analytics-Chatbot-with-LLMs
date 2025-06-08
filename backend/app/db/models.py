"""
Database and request models for Gemini chat application. They define the structure of 
requests and chat sessions, avoiding seralization issues.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GenerateRequest(BaseModel):
    prompt: str
    provider: str
    model: Optional[str]
    temperature: float
    top_p: float
    top_k: int
    session_id: Optional[str] = None

class GeminiRequest(BaseModel):
    prompt: str
    temperature: float
    top_p: float
    top_k: int
    session_id: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ChatSession(BaseModel):
    id: str
    name: Optional[str] = None
    created_at: datetime = datetime.now()
    messages: List[ChatMessage] = []

class ChatSessionRequest(BaseModel):
    name: Optional[str] = None