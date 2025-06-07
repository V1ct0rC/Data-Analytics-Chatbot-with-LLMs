"""
FastAPI backend for Data Science LLM application.
This module provides endpoints for managing chat sessions, uploading CSV files, and interacting with a Gemini LLM.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form

import os
import logging
from typing import List

from google import genai
from google.genai import types

from backend.app.llm.agent_functions import query_database, generate_chart, list_tables
from backend.app.llm.prompt_template import GEMINI_PROMPT_TEMPLATE
import backend.app.llm.session as session_manager

from backend.app.db.models import ChatSession, ChatMessage, ChatSessionRequest, GeminiRequest
from backend.app.db.db_functions import add_csv_to_database
from dotenv import load_dotenv


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

# Message related endpoints --------------------------------------------------------------------------
@app.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
def get_messages(session_id: str):
    """Get all messages in a chat session"""
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.messages

# Agent related endpoints ----------------------------------------------------------------------------
@app.post("/gemini")
def call_gemini(request: GeminiRequest):
    api_key = os.getenv("GEMINI_API_KEY")

    # Validate API key
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set in environment variables.")
    
    # Create a new session if none provided (just a fallback)
    session_id = request.session_id
    if not session_id:
        session = session_manager.create_session()
        session_id = session.id
    elif not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    print(f"Processing request for session: {session_id}")
    
    try:
        # Store user message
        session_manager.add_message(session_id, "user", request.prompt)
        
        # Get conversation history for context
        messages = session_manager.get_messages(session_id)
        
        # Adjust the request parameters based on the request preferences
        # In python, gemini is able to automatically handle function calling, so we can pass the tools directly.
        # In other languages, we would need to pass the {function}_declaration, also specified on agent_functions
        # file, and manage the function calls manually.
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=GEMINI_PROMPT_TEMPLATE,
            tools=[query_database, generate_chart, list_tables],
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k
        )
        print(f"Temperature: {request.temperature}, Top P: {request.top_p}, Top K: {request.top_k}")
        
        # Create a conversation history in Gemini format
        history = []
        for msg in messages:
            content = types.Content(
                role="user" if msg.role == "user" else "model",
                parts=[types.Part(text=msg.content)]
            )
            history.append(content)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=history,
            config=config,
        )
        
        # Store assistant's response
        response_text = str(response.text)
        session_manager.add_message(session_id, "assistant", response_text)

        chart_data = None
        # As the agent cannot directly return function call results, we need to check the response for function calls
        # and responses. So we will look for function calls to produce charts on the frontend.
        if hasattr(response, 'automatic_function_calling_history'):
            for content in response.automatic_function_calling_history:
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        if hasattr(part, 'function_call') and part.function_call and part.function_call.name == "generate_chart":
                            params = part.function_call.args
                            chart_data = generate_chart(**params)
                            print(f"Found function call with params: {params}")
                        
                        if hasattr(part, 'function_response') and part.function_response and part.function_response.name == "generate_chart":
                            if 'result' in part.function_response.response:
                                chart_data = part.function_response.response['result']
                                print(f"Found function response with result data")

        print(f"Chart data: {chart_data}")
        return {
            "response": response_text,
            "session_id": session_id,
            "chart_data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
