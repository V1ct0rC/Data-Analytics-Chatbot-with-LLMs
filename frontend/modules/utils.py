import streamlit as st
from modules.api import load_sessions, load_messages

import streamlit as st

def initialize_session_state(backend_url: str) -> None:
    """Initialize Streamlit session state variables."""
    # Chat and session management
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    
    if "session_names" not in st.session_state:
        st.session_state.session_names = {}
    
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    
    # Chart data
    if "current_chart_data" not in st.session_state:
        st.session_state.current_chart_data = None
    
    if "chart_history" not in st.session_state:
        st.session_state.chart_history = {}
    
    # UI state
    if "show_landing_page" not in st.session_state:
        st.session_state.show_landing_page = True
    
    # LLM providers and models
    if "providers" not in st.session_state:
        st.session_state.providers = {}
    
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = "gemini"
    
    if "current_model" not in st.session_state:
        st.session_state.current_model = None

    # Form state
    if "submit_pressed" not in st.session_state:
        st.session_state.submit_pressed = False
    
    # Initialization flags
    if "sessions_loaded" not in st.session_state:
        st.session_state.sessions_loaded = False
    
    if "providers_loaded" not in st.session_state:
        st.session_state.providers_loaded = False

def start_chatting() -> None:
    """Hide landing page and show chat interface."""
    st.session_state.show_landing_page = False

def load_sessions_from_backend(backend_url: str) -> bool:
    """Load all sessions and their messages from the backend."""
    try:
        # Get all sessions
        sessions, success = load_sessions(backend_url)
        
        if success:
            for session in sessions:
                session_id = session["id"]
                
                if session_id in st.session_state.chat_sessions:
                    continue
                
                messages, msg_success = load_messages(backend_url, session_id)
                
                if msg_success:
                    # Convert to the format used in frontend
                    frontend_messages = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in messages
                    ]
                    
                    st.session_state.chat_sessions[session_id] = frontend_messages
                    st.session_state.session_names[session_id] = session.get("name", f"Chat {session_id[:6]}")
                    
                    if session_id not in st.session_state.chart_history:
                        st.session_state.chart_history[session_id] = []
            
            if st.session_state.current_chat_id is None and st.session_state.chat_sessions:
                st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
            
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Error loading sessions: {str(e)}")
        return False