from db.models import ChatSession, ChatMessage
from typing import Dict, List, Optional
import uuid


chat_sessions: Dict[str, ChatSession] = {}

def create_session(name: Optional[str] = None) -> ChatSession:
    """Create a new chat session"""
    session = ChatSession(id=str(uuid.uuid4()), name=name)
    chat_sessions[session.id] = session
    return session

def get_session(session_id: str) -> Optional[ChatSession]:
    """Get a chat session by ID"""
    return chat_sessions.get(session_id)

def add_message(session_id: str, role: str, content: str) -> Optional[ChatMessage]:
    """Add a message to a chat session"""
    session = get_session(session_id)
    if not session:
        return None
    
    message = ChatMessage(role=role, content=content)
    session.messages.append(message)
    return message

def get_messages(session_id: str) -> List[ChatMessage]:
    """Get all messages in a chat session"""
    session = get_session(session_id)
    if not session:
        return []
    return session.messages