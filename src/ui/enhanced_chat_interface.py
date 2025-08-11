import streamlit as st
import sys
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chatbot.simple_enhanced_chatbot import create_simple_enhanced_chatbot

def initialize_session_state():
    """Initialize session state variables."""
    if 'enhanced_chatbot' not in st.session_state:
        st.session_state.enhanced_chatbot = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    if 'habit_suggestions' not in st.session_state:
        st.session_state.habit_suggestions = []
    if 'mood_data' not in st.session_state:
        st.session_state.mood_data = {}

def setup_services():
    """Setup enhanced chatbot."""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("Google API key not found.")
            st.stop()
        
        st.session_state.enhanced_chatbot = create_simple_enhanced_chatbot(api_key=api_key)
        
    except Exception as e:
        st.error(f"Failed to setup services: {str(e)}")
        st.stop()

def display_mood_analysis(mood_data: Dict):
    """Display mood analysis results."""
    if mood_data:
        st.markdown("### 📊 Mood Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mood", mood_data.get('mood', 'Unknown').title())
        
        with col2:
            sentiment = mood_data.get('sentiment_score', 0)
            st.metric("Sentiment", f"{sentiment:.2f}")
        
        with col3:
            st.metric("Intensity", mood_data.get('intensity', 'Unknown').title())
        
        with col4:
            keywords = mood_data.get('keywords', [])
            if keywords:
                st.metric("Key Emotions", ", ".join(keywords[:3]))
            else:
                st.metric("Key Emotions", "None detected")

def display_habit_suggestions(suggestions: List[Dict]):
    """Display habit suggestions."""
    if suggestions:
        st.markdown("### 💡 Personalized Suggestions")
        
        for i, suggestion in enumerate(suggestions):
            with st.expander(f"💡 {suggestion['habit']} ({suggestion['category']})"):
                st.write(f"**Description:** {suggestion['description']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Difficulty:** {suggestion['difficulty'].title()}")
                with col2:
                    st.write(f"**Time:** {suggestion['estimated_time']}")

def main():
    """Enhanced Streamlit app with Milestone 4 features."""
    st.set_page_config(
        page_title="AI Mental Health Companion - Enhanced",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Setup services
    setup_services()
    
    # Header
    st.title("🧠 AI Mental Health Companion - Enhanced")
    st.markdown("**Now with intelligent mood analysis and personalized feedback!**")
    st.markdown("---")
    
    # User identification
    if not st.session_state.current_user_id:
        user_id = st.text_input("Enter a user ID to start (e.g., 'user123'):")
        if user_id:
            st.session_state.current_user_id = user_id
            st.rerun()
    else:
        st.success(f"Welcome back, {st.session_state.current_user_id}! 🌟")
    
    # Sidebar
    with st.sidebar:
        st.header("💬 Enhanced Controls")
        
        if st.button("🔄 Start New Conversation", use_container_width=True):
            if st.session_state.current_user_id:
                try:
                    greeting, habit_suggestions = st.session_state.enhanced_chatbot.start_conversation(
                        st.session_state.current_user_id
                    )
                    
                    st.session_state.messages = [{"role": "assistant", "content": greeting}]
                    st.session_state.habit_suggestions = habit_suggestions
                    st.session_state.conversation_started = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to start conversation: {str(e)}")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.habit_suggestions = []
            st.session_state.mood_data = {}
            st.rerun()
        
        st.markdown("---")
        
        # Session info
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
        
        # Milestone 4 features info
        st.markdown("### 🆕 Milestone 4 Features")
        st.markdown("""
        **New Capabilities:**
        - 🧠 Real-time mood analysis
        - 🎯 Sentiment scoring
        - 💡 Personalized habit suggestions
        - 🎯 Context-aware responses
        - 📈 Emotional pattern tracking
        - 🌟 Enhanced AI intelligence
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This enhanced version includes:
        - Intelligent mood analysis of every message
        - Personalized habit suggestions based on your emotional state
        - Enhanced AI responses that adapt to your mood
        - Real-time sentiment tracking
        """)
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display mood analysis
        if st.session_state.mood_data:
            display_mood_analysis(st.session_state.mood_data)
            st.markdown("---")
        
        # Display habit suggestions
        if st.session_state.habit_suggestions:
            display_habit_suggestions(st.session_state.habit_suggestions)
            st.markdown("---")
        
        # Display existing messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Share what's on your mind..."):
            if not st.session_state.current_user_id:
                st.error("Please enter a user ID first.")
                return
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get enhanced response
            with st.spinner("🤔 Analyzing your message and generating personalized response..."):
                try:
                    response, mood_data, new_suggestions = st.session_state.enhanced_chatbot.send_message(prompt)
                    
                    # Update session state
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.mood_data = mood_data
                    st.session_state.habit_suggestions = new_suggestions
                    
                    # Display bot response
                    with st.chat_message("assistant"):
                        st.write(response)
                    
                    # Auto-refresh to show new mood analysis and suggestions
                    st.rerun()
                    
                except Exception as e:
                    error_msg = "I'm having trouble responding right now. Please try again."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.write(error_msg)
                    st.error(f"Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        🧠 <strong>Milestone 4:</strong> Enhanced AI with mood analysis, personalized suggestions, and intelligent responses!
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 