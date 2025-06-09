"""
Functions for managing chat sessions and messages in a database. This module provides 
functions to create, retrieve, delete chat sessions and deal with chat messages.
"""

from datetime import datetime
from backend.app.db.models import ChatSession, ChatMessage
from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
import uuid
import os
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_operations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL)

# Session related functions --------------------------------------------------------------------------
def create_session(name: Optional[str] = None) -> Optional[ChatSession]:
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    created_at = datetime.now()

    if not name:
        name = f"Session {created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO chat_sessions (id, name, created_at) VALUES (:id, :name, :created_at)"),
                {"id": session_id, "name": name, "created_at": created_at}
            )
            conn.commit()
        return ChatSession(id=session_id, name=name, created_at=created_at, messages=[])
    
    except SQLAlchemyError as e:
        logger.error(f"Error creating session: {e}")
        raise ValueError(f"Failed to create session: {e}")


def get_session(session_id: str) -> Optional[ChatSession]:
    """Get a chat session by ID"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, created_at FROM chat_sessions WHERE id = :id"),
                {"id": session_id}
            ).fetchone()

            if not result:
                logger.warning(f"Session with ID {session_id} not found.")
                return None

            messages = get_messages(session_id)
            return ChatSession(
                id=result[0],
                name=result[1],
                created_at=result[2],
                messages=messages
            )
        
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        return None


def delete_session(session_id: str) -> bool:
    """Delete a chat session and its messages"""
    try:
        with engine.connect() as conn:
            # Deleting messages first due to foreign key constraints
            conn.execute(
                text("DELETE FROM chat_messages WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            result = conn.execute(
                text("DELETE FROM chat_sessions WHERE id = :session_id"),
                {"session_id": session_id}
            )
            conn.commit()
            return result.rowcount > 0
    
    except SQLAlchemyError as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return False


def list_sessions() -> List[ChatSession]:
    """Get all chat sessions"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, created_at FROM chat_sessions")
            ).fetchall()

            logger.info(f"Found {len(result)} sessions in the database.")
            sessions = []
            for row in result:
                messages = get_messages(row[0])
                sessions.append(ChatSession(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    messages=messages
                ))
            return sessions
    
    except SQLAlchemyError as e:
        logger.error(f"Error listing sessions: {e}")
        return []

# Message related functions --------------------------------------------------------------------------
def add_message(session_id: str, role: str, content: str) -> Optional[ChatMessage]:
    """Add a message to a chat session"""
    timestamp = datetime.now()

    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO chat_messages (session_id, role, content, timestamp) VALUES (:session_id, :role, :content, :timestamp)"),
                {"session_id": session_id, "role": role, "content": content, "timestamp": timestamp}
            )
            conn.commit()
        return ChatMessage(role=role, content=content, timestamp=timestamp)
    
    except SQLAlchemyError as e:
        logger.error(f"Error adding message to session {session_id}: {e}")
        return None


def get_messages(session_id: str) -> List[ChatMessage]:
    """Get all messages in a chat session"""    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT role, content, timestamp FROM chat_messages WHERE session_id = :session_id ORDER BY timestamp"),
                {"session_id": session_id}
            ).fetchall()
            return [ChatMessage(role=row[0], content=row[1], timestamp=row[2]) for row in result]
    
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving messages for session {session_id}: {e}")
        return []