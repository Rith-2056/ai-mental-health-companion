import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import re

# Use absolute imports
import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import MoodType, ChatMessage, MoodAnalytics
from firestore_service import FirestoreService

logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """
    Analyzes user messages for emotional content and provides personalized feedback.
    Uses Gemini API for sentiment analysis and pattern recognition.
    """
    
    def __init__(self, api_key: str, firestore_service: FirestoreService):
        """
        Initialize the mood analyzer.
        
        Args:
            api_key: Google Gemini API key
            firestore_service: Firestore service for data persistence
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.firestore_service = firestore_service
        
        # Sentiment analysis prompt
        self.sentiment_prompt = """
        Analyze the emotional content of this message and provide:
        1. Primary mood (very_happy, happy, neutral, sad, very_sad, anxious, stressed, calm, excited, tired)
        2. Sentiment score (0.0 to 1.0, where 0.0 is very negative and 1.0 is very positive)
        3. Emotional intensity (low, medium, high)
        4. Key emotional keywords
        
        Message: "{message}"
        
        Respond in this exact format:
        MOOD: [mood_type]
        SENTIMENT: [score]
        INTENSITY: [intensity]
        KEYWORDS: [comma-separated keywords]
        """
        
        # Pattern analysis prompt
        self.pattern_prompt = """
        Analyze these recent messages for emotional patterns and provide insights:
        
        Recent messages:
        {messages}
        
        Provide analysis in this format:
        PATTERN: [brief description of emotional pattern]
        TREND: [improving/declining/stable]
        SUGGESTION: [personalized coping strategy or habit suggestion]
        """
    
    def analyze_message_sentiment(self, message: str) -> Dict[str, any]:
        """
        Analyze the sentiment of a single message.
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with mood, sentiment score, intensity, and keywords
        """
        try:
            # Prepare prompt
            prompt = self.sentiment_prompt.format(message=message)
            
            # Get analysis from Gemini
            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()
            
            # Parse the response
            result = self._parse_sentiment_response(analysis_text)
            
            logger.info(f"Sentiment analysis completed for message: {message[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # Return neutral sentiment as fallback
            return {
                'mood': 'neutral',
                'sentiment_score': 0.5,
                'intensity': 'low',
                'keywords': []
            }
    
    def _parse_sentiment_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse the sentiment analysis response from Gemini.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed sentiment data
        """
        try:
            lines = response_text.split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('MOOD:'):
                    mood_str = line.split(':', 1)[1].strip().lower()
                    result['mood'] = mood_str  # Return string instead of enum
                elif line.startswith('SENTIMENT:'):
                    score_str = line.split(':', 1)[1].strip()
                    result['sentiment_score'] = float(score_str)
                elif line.startswith('INTENSITY:'):
                    result['intensity'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('KEYWORDS:'):
                    keywords_str = line.split(':', 1)[1].strip()
                    result['keywords'] = [k.strip() for k in keywords_str.split(',') if k.strip()]
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {str(e)}")
            return {
                'mood': 'neutral',
                'sentiment_score': 0.5,
                'intensity': 'low',
                'keywords': []
            }
    
    def analyze_emotional_patterns(self, user_id: str, days: int = 7) -> Dict[str, any]:
        """
        Analyze emotional patterns over time for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Pattern analysis results
        """
        try:
            # Get recent messages
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user sessions
            sessions = self.firestore_service.get_user_sessions(user_id, limit=20)
            
            # Collect recent messages
            recent_messages = []
            for session in sessions:
                if session.started_at >= start_date:
                    messages = self.firestore_service.get_session_messages(session.session_id)
                    recent_messages.extend(messages)
            
            if not recent_messages:
                return {
                    'pattern': 'No recent messages to analyze',
                    'trend': 'stable',
                    'suggestion': 'Start a conversation to get personalized insights'
                }
            
            # Prepare messages for analysis
            message_texts = []
            for msg in recent_messages[-10:]:  # Last 10 messages
                if msg.role == 'user':
                    message_texts.append(f"User: {msg.content}")
            
            if not message_texts:
                return {
                    'pattern': 'No user messages to analyze',
                    'trend': 'stable',
                    'suggestion': 'Share your thoughts to get personalized support'
                }
            
            # Analyze patterns
            messages_text = '\n'.join(message_texts)
            prompt = self.pattern_prompt.format(messages=messages_text)
            
            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()
            
            # Parse pattern analysis
            result = self._parse_pattern_response(analysis_text)
            
            logger.info(f"Pattern analysis completed for user: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
            return {
                'pattern': 'Unable to analyze patterns at this time',
                'trend': 'stable',
                'suggestion': 'Continue sharing your thoughts for better insights'
            }
    
    def _parse_pattern_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the pattern analysis response from Gemini.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed pattern data
        """
        try:
            lines = response_text.split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('PATTERN:'):
                    result['pattern'] = line.split(':', 1)[1].strip()
                elif line.startswith('TREND:'):
                    result['trend'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('SUGGESTION:'):
                    result['suggestion'] = line.split(':', 1)[1].strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing pattern response: {str(e)}")
            return {
                'pattern': 'Unable to analyze patterns',
                'trend': 'stable',
                'suggestion': 'Continue sharing your thoughts'
            }
    
    def generate_personalized_feedback(self, user_id: str, current_mood: str, sentiment_score: float) -> str:
        """
        Generate personalized feedback based on current mood and user history.
        
        Args:
            user_id: User identifier
            current_mood: Current detected mood
            sentiment_score: Current sentiment score
            
        Returns:
            Personalized feedback message
        """
        try:
            # Get user profile
            user_profile = self.firestore_service.get_user_profile(user_id)
            
            # Get recent pattern analysis
            patterns = self.analyze_emotional_patterns(user_id, days=7)
            
            # Generate personalized feedback
            feedback_prompt = f"""
            Generate personalized, empathetic feedback for a mental health companion user.
            
            User context:
            - Current mood: {current_mood}
            - Sentiment score: {sentiment_score:.2f}
            - Total sessions: {user_profile.total_sessions if user_profile else 0}
            - Recent pattern: {patterns.get('pattern', 'No pattern detected')}
            - Trend: {patterns.get('trend', 'stable')}
            
            Provide a supportive, personalized response that:
            1. Acknowledges their current emotional state
            2. References their recent patterns if relevant
            3. Offers specific, actionable suggestions
            4. Maintains a warm, non-judgmental tone
            5. Keeps it concise (2-3 sentences)
            
            Response:
            """
            
            response = self.model.generate_content(feedback_prompt)
            feedback = response.text.strip()
            
            logger.info(f"Generated personalized feedback for user: {user_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating personalized feedback: {str(e)}")
            return "I'm here to listen and support you. How are you feeling right now?"
    
    def update_mood_analytics(self, user_id: str, message: ChatMessage, sentiment_data: Dict[str, any]) -> None:
        """
        Update mood analytics with new message data.
        
        Args:
            user_id: User identifier
            message: Chat message
            sentiment_data: Sentiment analysis results
        """
        try:
            # Get or create daily analytics
            today = datetime.utcnow().date()
            analytics_id = today.strftime('%Y-%m-%d')
            
            # Get existing analytics or create new
            existing_analytics = self.firestore_service.get_user_mood_history(user_id, days=1)
            
            if existing_analytics and existing_analytics[0].date.date() == today:
                analytics = existing_analytics[0]
                # Update existing analytics
                analytics.total_messages += 1
                analytics.average_sentiment = (
                    (analytics.average_sentiment * (analytics.total_messages - 1) + sentiment_data['sentiment_score']) 
                    / analytics.total_messages
                )
                
                # Update mood distribution
                mood_key = sentiment_data['mood']
                analytics.mood_distribution[mood_key] = analytics.mood_distribution.get(mood_key, 0) + 1
                
            else:
                # Create new analytics
                analytics = MoodAnalytics(
                    user_id=user_id,
                    date=datetime.combine(today, datetime.min.time()),
                    mood_distribution={sentiment_data['mood']: 1},
                    average_sentiment=sentiment_data['sentiment_score'],
                    total_messages=1,
                    session_count=1
                )
            
            # Save analytics
            self.firestore_service.save_mood_analytics(analytics)
            
            logger.info(f"Updated mood analytics for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating mood analytics: {str(e)}")