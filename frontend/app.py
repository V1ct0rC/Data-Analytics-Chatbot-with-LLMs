import streamlit as st
import os

from modules.utils import initialize_session_state
from modules.utils import load_sessions_from_backend
from ui.landing_page import render_landing_page
from ui.sidebar import render_sidebar
from ui.chat import render_chat_area


# Set page configuration
st.set_page_config(page_title="Data Analysis Chatbot", layout="wide")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

initialize_session_state(BACKEND_URL)

# Load sessions from backend if not already loaded
if not st.session_state.sessions_loaded:
    sessions_loaded = load_sessions_from_backend(BACKEND_URL)
    st.session_state.sessions_loaded = True

# Main application flow
if st.session_state.show_landing_page:
    render_landing_page()
else:
    # Render sidebar with session management
    render_sidebar(BACKEND_URL)
    
    # Render main chat area
    render_chat_area(BACKEND_URL)