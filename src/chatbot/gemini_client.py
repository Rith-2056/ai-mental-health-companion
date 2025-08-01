import os
import google.generativeai as genai
from typing import List, Dict, Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmpatheticChatbot:
    """
    An empathetic chatbot using Google's Gemini API for mental health support.
    Maintains a supportive, non-judgmental tone throughout conversations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the empathetic chatbot.
        Args: api_key: Google Gemini API key. If not provided, will look for GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("Successfully initialized gemini-2.0-flash-exp model")
        
        # System prompt for empathetic mental health support
        self.system_prompt = """
        You are an empathetic AI mental health companion. Your role is to:
        
        1. Provide emotional support and active listening
        2. Maintain a warm, non-judgmental, and supportive tone
        3. Help users explore their feelings through gentle questioning
        4. Offer coping strategies when appropriate
        5. Never give medical advice or attempt to diagnose
        6. Always encourage professional help for serious concerns
        7. Keep responses conversational and not overly clinical
        8. Show genuine care and understanding
        
        Important guidelines:
        - Always respond with empathy and understanding
        - Use "I hear you" and "That sounds..." to validate feelings
        - Ask open-ended questions to help users explore their thoughts
        - If someone mentions self-harm or severe distress, immediately encourage professional help
        - Keep responses concise but meaningful (2-4 sentences)
        - Remember this is a supportive conversation, not therapy
        
        Start each conversation warmly and check in on how the user is feeling.
        """
        
        # Initialize conversation history
        self.conversation_history = []
        
    def start_conversation(self) -> str:
        """
        Start a new conversation with a warm greeting.
        Returns: Initial greeting message
        """
        greeting = "Hello! I'm here to listen and support you. How are you feeling today?"
        self.conversation_history = [
            {"role": "assistant", "content": greeting}
        ]
        return greeting
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message to the chatbot and get an empathetic response.
        Args: user_message: The user's message
        Returns: The chatbot's empathetic response
        """
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Create the full conversation context
            conversation_context = self.system_prompt + "\n\nConversation history:\n"
            for msg in self.conversation_history:
                role = "Assistant" if msg["role"] == "assistant" else "User"
                conversation_context += f"{role}: {msg['content']}\n"
            
            logger.info(f"Sending message to Gemini API: {user_message[:50]}...")
            
            # Generate response
            response = self.model.generate_content(conversation_context)
            bot_response = response.text.strip()
            
            # Add bot response to history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            logger.info(f"Successfully generated response: {bot_response[:50]}...")
            return bot_response
            
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}")
            return "I'm having trouble responding right now. Could you try again in a moment?"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        Returns: List of conversation messages with role and content
        """
        return self.conversation_history.copy()
    
    def reset_conversation(self) -> str:
        """
        Reset the conversation and start fresh.
        Returns: New greeting message
        """
        return self.start_conversation()

# Convenience function for easy initialization
def create_chatbot(api_key: Optional[str] = None) -> EmpatheticChatbot:
    """
    Create and return an empathetic chatbot instance.
    Args: api_key: Google Gemini API key   
    Returns: EmpatheticChatbot instance
    """
    return EmpatheticChatbot(api_key)
        
