import os
import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleEnhancedChatbot:
    """
    Simplified enhanced chatbot with mood analysis (no Firestore dependency).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the simplified enhanced chatbot.
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
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
        
    def start_conversation(self, user_id: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Start a new conversation with mood analysis capabilities.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (greeting_message, habit_suggestions)
        """
        try:
            # Generate personalized greeting
            greeting = self._generate_personalized_greeting(user_id)
            
            # Get habit suggestions
            habit_suggestions = self._generate_habit_suggestions("neutral", 0.5, count=2)
            
            # Initialize conversation history
            self.conversation_history = [
                {"role": "assistant", "content": greeting}
            ]
            
            return greeting, habit_suggestions
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return "Hello! I'm here to listen and support you. How are you feeling today?", []
    
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
            sentiment_data = self._analyze_message_sentiment(user_message)
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Generate enhanced response
            response = self._generate_enhanced_response(user_message, sentiment_data)
            
            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Generate habit suggestions based on current mood
            habit_suggestions = self._generate_habit_suggestions(
                sentiment_data['mood'],
                sentiment_data['sentiment_score'],
                count=2
            )
            
            logger.info(f"Enhanced response generated")
            return response, sentiment_data, habit_suggestions
            
        except Exception as e:
            logger.error(f"Error in enhanced send_message: {str(e)}")
            return "I'm having trouble responding right now. Could you try again in a moment?", {}, []
    
    def _analyze_message_sentiment(self, message: str) -> Dict[str, any]:
        """
        Analyze the sentiment of a single message.
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with mood, sentiment score, intensity, and keywords
        """
        try:
            sentiment_prompt = f"""
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
            
            response = self.model.generate_content(sentiment_prompt)
            analysis_text = response.text.strip()
            
            # Parse the response
            result = self._parse_sentiment_response(analysis_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'mood': 'neutral',
                'sentiment_score': 0.5,
                'intensity': 'low',
                'keywords': []
            }
    
    def _parse_sentiment_response(self, response_text: str) -> Dict[str, any]:
        """Parse the sentiment analysis response."""
        try:
            lines = response_text.split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('MOOD:'):
                    result['mood'] = line.split(':', 1)[1].strip().lower()
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
    
    def _generate_personalized_greeting(self, user_id: str) -> str:
        """Generate a personalized greeting."""
        try:
            greeting_prompt = f"""
            Generate a warm, personalized greeting for a mental health companion user.
            
            User ID: {user_id}
            
            Make it:
            1. Welcoming and supportive
            2. Encourages them to share how they're feeling
            3. Warm and non-judgmental
            4. Brief (1-2 sentences)
            
            Greeting:
            """
            
            response = self.model.generate_content(greeting_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting: {str(e)}")
            return "Hello! I'm here to listen and support you. How are you feeling today?"
    
    def _generate_enhanced_response(self, user_message: str, sentiment_data: Dict[str, any]) -> str:
        """Generate an enhanced response using mood analysis."""
        try:
            # Create enhanced context
            enhanced_context = f"""
            {self.system_prompt}
            
            Current emotional context:
            - Detected mood: {sentiment_data['mood']}
            - Sentiment score: {sentiment_data['sentiment_score']:.2f}
            - Emotional intensity: {sentiment_data['intensity']}
            - Key emotions: {', '.join(sentiment_data.get('keywords', []))}
            
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
    
    def _generate_habit_suggestions(self, mood: str, sentiment_score: float, count: int = 3) -> List[Dict[str, str]]:
        """Generate habit suggestions based on mood."""
        try:
            # Define habit categories based on mood
            habit_categories = {
                'stressed': ['Deep breathing', 'Progressive muscle relaxation', 'Mindful walking'],
                'anxious': ['Grounding techniques', 'Regular sleep schedule', 'Mindfulness meditation'],
                'sad': ['Gratitude practice', 'Physical exercise', 'Social connection'],
                'very_sad': ['Daily movement', 'Social engagement', 'Professional support seeking'],
                'happy': ['Creative activities', 'Goal setting', 'Sharing positive experiences'],
                'neutral': ['Journaling', 'Nature exposure', 'Hobby development']
            }
            
            # Get appropriate habits
            base_habits = habit_categories.get(mood, habit_categories['neutral'])
            
            suggestions = []
            for i in range(min(count, len(base_habits))):
                habit = base_habits[i]
                suggestions.append({
                    'habit': habit,
                    'category': mood,
                    'description': f'Try {habit.lower()} to help improve your well-being.',
                    'difficulty': 'easy' if sentiment_score < 0.3 else 'medium',
                    'estimated_time': '5-15 minutes'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating habit suggestions: {str(e)}")
            return [
                {
                    'habit': 'Take a few deep breaths',
                    'category': 'stress_relief',
                    'description': 'Simple breathing exercise to help you feel more centered',
                    'difficulty': 'easy',
                    'estimated_time': '2-3 minutes'
                }
            ]

# Convenience function
def create_simple_enhanced_chatbot(api_key: Optional[str] = None) -> SimpleEnhancedChatbot:
    """Create and return a simple enhanced chatbot instance."""
    return SimpleEnhancedChatbot(api_key) 