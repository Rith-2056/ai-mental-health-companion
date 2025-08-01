import streamlit as st
import sys
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chatbot.gemini_client import create_chatbot

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False

def setup_chatbot():
    """Setup the chatbot with API key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        st.error("⚠️ Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        st.stop()
    
    try:
        chatbot = create_chatbot(api_key)
        return chatbot
    except Exception as e:
        st.error(f"❌ Error initializing chatbot: {str(e)}")
        st.stop()

def display_chat_message(message: Dict[str, str]):
    """Display a single chat message."""
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

def main():
    """Main Streamlit app for the chat interface."""
    st.set_page_config(
        page_title="AI Mental Health Companion",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🧠 AI Mental Health Companion")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("💬 Chat Controls")
        
        if st.button("🔄 Start New Conversation", use_container_width=True):
            st.session_state.chatbot = setup_chatbot()
            st.session_state.messages = []
            st.session_state.conversation_started = True
            # Start the conversation
            greeting = st.session_state.chatbot.start_conversation()
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            st.rerun()
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Session Info")
        if st.session_state.messages:
            st.write(f"Messages: {len(st.session_state.messages)}")
            if st.session_state.conversation_started:
                st.write("Status: ✅ Active")
            else:
                st.write("Status: ⏸️ Paused")
        else:
            st.write("Status: 🚫 No session")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI companion is designed to provide empathetic support and active listening.
        
        **Remember:**
        - This is not a replacement for professional therapy
        - For crisis situations, please contact emergency services
        - Your conversations are private and secure
        """)
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display existing messages
        for message in st.session_state.messages:
            display_chat_message(message)
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message({"role": "user", "content": prompt})
            
            # Initialize chatbot if not already done
            if not st.session_state.chatbot:
                st.session_state.chatbot = setup_chatbot()
                st.session_state.conversation_started = True
            
            # Get bot response
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.chatbot.send_message(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I'm having trouble responding right now. Please try again."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    display_chat_message({"role": "assistant", "content": error_msg})
                    st.error(f"Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        💡 <strong>Tip:</strong> Be open and honest about your feelings. I'm here to listen and support you.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 