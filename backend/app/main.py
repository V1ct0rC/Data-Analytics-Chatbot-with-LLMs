from fastapi import FastAPI, HTTPException
import os
from google import genai
from google.genai import types
from typing import List

from llm.agent_functions import query_database, generate_chart
from llm.prompt_template import PROMPT_TEMPLATE
import llm.session as session_manager
from db.models import ChatSession, ChatMessage, ChatSessionRequest, GeminiRequest


app = FastAPI(debug=True, title="Data Science LLM Backend", description="A backend service for interacting with SQL data and LLMs.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

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

@app.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
def get_messages(session_id: str):
    """Get all messages in a chat session"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages

@app.post("/gemini")
def call_gemini(request: GeminiRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set in environment variables.")
    
    # Create a new session if none provided
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
        
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=PROMPT_TEMPLATE,
            tools=[query_database, generate_chart]
        )
        
        # Create a conversation format for Gemini
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
        
        print(f"Gemini response: {response}")

        chart_data = None
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

