"""
FastAPI backend for Data Science LLM application.
This module provides endpoints for managing chat sessions, uploading CSV files, and interacting with a Gemini LLM.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form

import os
import logging
from dotenv import load_dotenv
from typing import List

from google import genai
from google.genai import types

from backend.app.llm.factory import LLMProviderFactory
from backend.app.llm.agent_functions import (
    query_database, generate_chart, list_tables
)
from backend.app.llm.prompt_templates import GEMINI_PROMPT_TEMPLATE
import backend.app.llm.session as session_manager

from backend.app.db.models import (
    ChatSession, ChatMessage, ChatSessionRequest, 
    GeminiRequest, GenerateRequest
)
from backend.app.db.db_functions import add_csv_to_database


load_dotenv()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True, title="Data Science LLM Backend", description="A backend service for interacting with SQL data and LLMs.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

# Session related endpoints --------------------------------------------------------------------------
@app.post("/sessions", response_model=ChatSession)
def create_session(request: ChatSessionRequest):
    """Create a new chat session"""
    new_session = session_manager.create_session(request.name)
    print(f"Created new session: {new_session.id}")
    return new_session

@app.get("/sessions/{session_id}", response_model=ChatSession)
def get_session(session_id: str):
    """Get a chat session by ID"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a chat session and its messages"""
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "message": "Session deleted"}

@app.get("/sessions", response_model=List[ChatSession])
def list_sessions():
    """Get all chat sessions"""
    return session_manager.list_sessions()

# Message related endpoints --------------------------------------------------------------------------
@app.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
def get_messages(session_id: str):
    """Get all messages in a chat session"""
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.messages

# Agent related endpoints ----------------------------------------------------------------------------
@app.post("/generate")
def generate_response(request: GenerateRequest):
    """Generate a response using the specified LLM provider"""

    # Get LLM provider from the factory -------------------------------------------------------------
    provider = LLMProviderFactory.get_provider(request.provider)
    if not provider:
        raise HTTPException(
            status_code=400, detail=f"Provider '{request.provider}' not available or API key not set"
        )
    
    # Manage session --------------------------------------------------------------------------------
    session_id = request.session_id
    if not session_id:
        session = session_manager.create_session()
        session_id = session.id
    elif not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Store user message
        session_manager.add_message(session_id, "user", request.prompt)
        # Get conversation history for context
        messages = session_manager.get_messages(session_id)

        result = provider.generate_response(
            prompt=request.prompt,  # For Gemini, prompt will not be used. The hustory already contains the last user message.
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k
        )

        # Store assistant's response
        session_manager.add_message(session_id, "assistant", result["response"])

        return {
            "response": result["response"],
            "session_id": session_id,
            "chart_data": result.get("chart_data", None)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
def get_available_providers():
    """Get a list of available LLM providers and models"""
    providers = LLMProviderFactory.get_available_providers()

    available_providers = {}
    for provider_str in providers:
        provider = LLMProviderFactory.get_provider(provider_str)
        if provider:
            available_providers[provider_str] = provider.get_available_models()

    return available_providers

# Database related endpoints -------------------------------------------------------------------------
@app.post("/upload_csv")
async def upload_csv(table_name: str = Form(...), file: UploadFile = File(...)):
    """Upload a CSV file and create a new table in the database."""
    try:
        contents = await file.read()
        result = add_csv_to_database(table_name, contents)
        if result.get("success"):
            return {"success": True, "message": f"Table '{table_name}' created successfully."}
        else:
            return {"success": False, "message": result.get("message", "Unknown error.")}
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        return {"success": False, "message": str(e)}
