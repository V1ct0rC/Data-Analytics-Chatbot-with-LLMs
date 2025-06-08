import streamlit as st
from modules.utils import start_chatting


def render_landing_page() -> None:
    """Render the landing page with a welcome message and instructions."""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Welcome to the Data Analysis Chatbot")
        st.markdown("""
        ### Your AI Assistant for Data Analysis
        
        This chatbot helps you analyze and understand your data through natural conversations.
        
        **Features:**
        - Upload your CSV data files directly
        - Ask questions about your data in natural language
        - Get visualizations and insights automatically
        - Multiple chat sessions to organize your work
        - Save and export your analysis results
        - Multiple LLM providers for different needs
        
        **Example questions you can ask:**
        - "What are the trends in my sales data over the last quarter?"
        - "Create a visualization showing the relationship between X and Y"
        - "Summarize the key insights from this dataset"
        """)
        
        st.button("Start Chatting", on_click=start_chatting, type="primary", use_container_width=True)
    
    with col2:
        st.image("frontend/assets/landing_page_art_2_small.png", use_container_width=True)