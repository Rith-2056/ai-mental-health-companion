import os
import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
import logging
import uuid
from datetime import datetime

# Use absolute imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.mood_analyzer import MoodAnalyzer
from backend.habit_suggestions import HabitSuggestionEngine
from backend.firestore_service import FirestoreService
from backend.firestore_config import FirestoreConfig
from backend.models import ChatMessage, MoodType

logger = logging.getLogger(__name__)

class EnhancedChatbot:
    """
    Enhanced chatbot with mood analysis and personalized feedback capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None, firestore_service: Optional[FirestoreService] = None):
        """
        Initialize the enhanced chatbot.
        
        Args:
            api_key: Google Gemini API key
            firestore_service: Firestore service instance
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize services
        if firestore_service:
            self.firestore_service = firestore_service
        else:
            config = FirestoreConfig()
            self.firestore_service = FirestoreService(config)
        
        self.mood_analyzer = MoodAnalyzer(self.api_key, self.firestore_service)
        self.habit_engine = HabitSuggestionEngine(self.api_key, self.firestore_service)
        
        # Enhanced system prompt
        self.system_prompt = """
        You are an empathetic AI mental health companion with advanced emotional intelligence.
        
        Your capabilities include:
        - Real-time mood analysis and sentiment tracking
        - Personalized feedback based on emotional patterns
        - Habit suggestions tailored to individual needs
        - Long-term relationship building with users
        
        Core principles:
        1. Provide emotional support and active listening
        2. Maintain a warm, non-judgmental, and supportive tone
        3. Reference past conversations and patterns when relevant
        4. Offer specific, actionable coping strategies
        5. Never give medical advice or attempt to diagnose
        6. Always encourage professional help for serious concerns
        7. Show genuine care and understanding
        8. Adapt your approach based on the user's emotional state
        
        Response guidelines:
        - Always respond with empathy and understanding
        - Use "I hear you" and "That sounds..." to validate feelings
        - Ask open-ended questions to help users explore their thoughts
        - If someone mentions self-harm or severe distress, immediately encourage professional help
        - Keep responses conversational and not overly clinical
        - Reference their emotional patterns when helpful
        - Offer specific suggestions when appropriate
        
        Remember: You're building a long-term supportive relationship, not just having a single conversation.
        """
        
        # Initialize conversation history
        self.conversation_history = []
        self.current_user_id = None
        self.current_session_id = None
        
    def start_conversation(self, user_id: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Start a new conversation with mood analysis capabilities.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (greeting_message, habit_suggestions)
        """
        self.current_user_id = user_id
        
        # Create or get user profile
        user_profile = self.firestore_service.get_user_profile(user_id)
        if not user_profile:
            user_profile = self.firestore_service.create_user_profile(user_id)
        
        # Create new session
        session = self.firestore_service.create_chat_session(user_id)
        self.current_session_id = session.session_id
        
        # Generate personalized greeting
        greeting = self._generate_personalized_greeting(user_profile)
        
        # Get habit suggestions
        habit_suggestions = self.habit_engine.generate_habit_suggestions(
            user_id, MoodType.NEUTRAL, 0.5, count=2
        )
        
        # Initialize conversation history
        self.conversation_history = [
            {"role": "assistant", "content": greeting}
        ]
        
        # Save greeting to Firestore
        greeting_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session.session_id,
            role="assistant",
            content=greeting,
            timestamp=datetime.utcnow()
        )
        self.firestore_service.save_chat_message(greeting_msg)
        
        return greeting, habit_suggestions
    
    def send_message(self, user_message: str) -> Tuple[str, Dict[str, any], List[Dict[str, str]]]:
        """
        Send a message and get enhanced response with mood analysis.
        
        Args:
            user_message: User's message
            
        Returns:
            Tuple of (response, mood_data, habit_suggestions)
        """
        try:
            # Analyze message sentiment
            sentiment_data = self.mood_analyzer.analyze_message_sentiment(user_message)
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Save user message to Firestore
            user_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                user_id=self.current_user_id,
                session_id=self.current_session_id,
                role="user",
                content=user_message,
                timestamp=datetime.utcnow(),
                mood_detected=sentiment_data['mood'],
                sentiment_score=sentiment_data['sentiment_score']
            )
            self.firestore_service.save_chat_message(user_msg)
            
            # Update mood analytics
            self.mood_analyzer.update_mood_analytics(
                self.current_user_id, user_msg, sentiment_data
            )
            
            # Generate enhanced response
            response = self._generate_enhanced_response(user_message, sentiment_data)
            
            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Save bot response to Firestore
            bot_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                user_id=self.current_user_id,
                session_id=self.current_session_id,
                role="assistant",
                content=response,
                timestamp=datetime.utcnow()
            )
            self.firestore_service.save_chat_message(bot_msg)
            
            # Generate habit suggestions based on current mood
            habit_suggestions = self.habit_engine.generate_habit_suggestions(
                self.current_user_id,
                sentiment_data['mood'],
                sentiment_data['sentiment_score'],
                count=2
            )
            
            logger.info(f"Enhanced response generated for user: {self.current_user_id}")
            return response, sentiment_data, habit_suggestions
            
        except Exception as e:
            logger.error(f"Error in enhanced send_message: {str(e)}")
            return "I'm having trouble responding right now. Could you try again in a moment?", {}, []
    
    def _generate_personalized_greeting(self, user_profile) -> str:
        """
        Generate a personalized greeting based on user history.
        
        Args:
            user_profile: User profile data
            
        Returns:
            Personalized greeting message
        """
        try:
            if user_profile.total_sessions > 1:
                # Returning user
                greeting_prompt = f"""
                Generate a warm, personalized greeting for a returning user.
                
                User context:
                - Total sessions: {user_profile.total_sessions}
                - Total messages: {user_profile.total_messages}
                - Last active: {user_profile.last_active.strftime('%B %d')}
                
                Make it:
                1. Welcoming and familiar
                2. Acknowledges their return
                3. Encourages them to share how they're feeling
                4. Warm and supportive
                5. Brief (1-2 sentences)
                
                Greeting:
                """
                
                response = self.model.generate_content(greeting_prompt)
                return response.text.strip()
            else:
                # New user
                return "Hello! I'm here to listen and support you. How are you feeling today?"
                
        except Exception as e:
            logger.error(f"Error generating personalized greeting: {str(e)}")
            return "Hello! I'm here to listen and support you. How are you feeling today?"
    
    def _generate_enhanced_response(self, user_message: str, sentiment_data: Dict[str, any]) -> str:
        """
        Generate an enhanced response using mood analysis and user history.
        
        Args:
            user_message: User's message
            sentiment_data: Sentiment analysis results
            
        Returns:
            Enhanced response
        """
        try:
            # Get personalized feedback
            personalized_feedback = self.mood_analyzer.generate_personalized_feedback(
                self.current_user_id,
                sentiment_data['mood'],
                sentiment_data['sentiment_score']
            )
            
            # Create enhanced context
            enhanced_context = f"""
            {self.system_prompt}
            
            Current emotional context:
            - Detected mood: {sentiment_data['mood'].value}
            - Sentiment score: {sentiment_data['sentiment_score']:.2f}
            - Emotional intensity: {sentiment_data['intensity']}
            - Key emotions: {', '.join(sentiment_data.get('keywords', []))}
            
            Personalized feedback: {personalized_feedback}
            
            Conversation history:
            """
            
            for msg in self.conversation_history:
                role = "Assistant" if msg["role"] == "assistant" else "User"
                enhanced_context += f"{role}: {msg['content']}\n"
            
            # Generate response
            response = self.model.generate_content(enhanced_context)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return "I understand what you're saying. Could you tell me more about how you're feeling?"
    
    def get_weekly_report(self) -> Dict[str, any]:
        """
        Get a weekly report for the current user.
        
        Args:
            None
            
        Returns:
            Weekly report data
        """
        if not self.current_user_id:
            return {"error": "No user session active"}
        
        return self.habit_engine.get_weekly_habit_report(self.current_user_id)
    
    def end_conversation(self) -> None:
        """
        End the current conversation and save session data.
        """
        if self.current_session_id:
            self.firestore_service.end_chat_session(self.current_session_id)
            logger.info(f"Ended conversation session: {self.current_session_id}")
        
        self.conversation_history = []
        self.current_session_id = None

# Convenience function
def create_enhanced_chatbot(api_key: Optional[str] = None, firestore_service: Optional[FirestoreService] = None) -> EnhancedChatbot:
    """
    Create and return an enhanced chatbot instance.
    
    Args:
        api_key: Google Gemini API key
        firestore_service: Firestore service instance
        
    Returns:
        EnhancedChatbot instance
    """
    return EnhancedChatbot(api_key, firestore_service) 