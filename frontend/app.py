import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Data Analysis Chatbot", layout="wide")

# Initialize session states
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"First Chat": []}
    
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "First Chat"

if "show_landing_page" not in st.session_state:
    st.session_state.show_landing_page = True

def start_chatting():
    """Callback to hide the landing page and show the chat interface."""
    st.session_state.show_landing_page = False

# Display landing page
if st.session_state.show_landing_page:
    st.title("Welcome to the Data Analysis Chatbot")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Your AI Assistant for Data Analysis
        
        This chatbot helps you analyze and understand your data through natural conversations.
        
        **Features:**
        - Ask questions about your data in plain English
        - Get visualizations and insights automatically
        - Multiple chat sessions to organize your work
        - Save and export your analysis results
        
        **Example questions you can ask:**
        - "What are the trends in my sales data over the last quarter?"
        - "Create a visualization showing the relationship between X and Y"
        - "Summarize the key insights from this dataset"
        """)
        
        st.button("Start Chatting", on_click=start_chatting, type="primary", use_container_width=True)
    
    with col2:
        # Placeholder for an image or illustration
        pass  # You can add an image here using st.image("path_to_image.jpg")
        
else:
    # Sidebar for chat session management ------------------------------------------------------------------
    with st.sidebar:
        st.title("Chat Sessions")
        
        # Create new chat session --------------------------------------------------------------------------
        if st.button("New Chat", use_container_width=True):
            new_id = f"Chat ({uuid.uuid4().hex[:6]})"
            st.session_state.chat_sessions[new_id] = []
            st.session_state.current_chat_id = new_id
        
        # Display chat sessions ----------------------------------------------------------------------------
        st.write("Your chats:")
        
        for chat_id in st.session_state.chat_sessions.keys():
            col1, col2 = st.columns([4, 1])
            
            # Highlight current chat
            if chat_id == st.session_state.current_chat_id:
                button_label = f":small_blue_diamond: {chat_id}"
            else:
                button_label = chat_id
                
            # Select chat button
            if col1.button(button_label, key=f"select_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
            
            # Delete button (only show if there are multiple)
            if len(st.session_state.chat_sessions) > 1:
                if col2.button(":x:", key=f"delete_{chat_id}"):
                    del st.session_state.chat_sessions[chat_id]
                    # If deleting current chat, switch to first available
                    if chat_id == st.session_state.current_chat_id:
                        st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
                    st.rerun()
        
        st.divider()

    # Main chat area ---------------------------------------------------------------------------------------
    st.title("Data Analysis Chatbot")

    chat_container = st.container(height=800)
    st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)  # Spacer
    input_container = st.container()

    # Get and display current chat messages ----------------------------------------------------------------
    current_messages = st.session_state.chat_sessions[st.session_state.current_chat_id]

    with chat_container:
        st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] {
            max-height: 800px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)

        for message in current_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input field for user messages ------------------------------------------------------------------------
    with input_container:
        if "submit_pressed" not in st.session_state:
            st.session_state.submit_pressed = False
        
        def handle_input():
            """Handle user input submission."""
            if st.session_state.user_input:
                # Add user message to chat history
                current_messages.append({"role": "user", "content": st.session_state.user_input})
                
                # Set flag to clear input on next rerun
                st.session_state.submit_pressed = True
        
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_input("Ask a question about your data:",
                                      key="user_input")
            submit_button = st.form_submit_button("Send")
            
            if submit_button and user_input:
                # Add user message to chat history
                current_messages.append({"role": "user", "content": user_input})
                
                with chat_container:
                    # Show user message
                    with st.chat_message("user"):
                        st.markdown(user_input)
                    
                    # Show assistant response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            # response = requests.post(
                            #     "http://localhost:8000/chat", 
                            #     json={"question": user_input}
                            # )
                            # answer = response.json()["answer"]
                            answer = "This is a placeholder response. Replace with actual API call."
                            st.markdown(answer)
                
                # Add assistant response to chat history
                current_messages.append({"role": "assistant", "content": answer})
                st.rerun()