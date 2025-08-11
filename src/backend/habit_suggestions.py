import google.generativeai as genai
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import random

# Use absolute imports
import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import MoodType, ChatMessage
from firestore_service import FirestoreService

logger = logging.getLogger(__name__)

class HabitSuggestionEngine:
    """
    Generates personalized habit suggestions based on user mood and patterns.
    """
    
    def __init__(self, api_key: str, firestore_service: FirestoreService):
        """
        Initialize the habit suggestion engine.
        
        Args:
            api_key: Google Gemini API key
            firestore_service: Firestore service for data persistence
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.firestore_service = firestore_service
        
        # Predefined habit categories
        self.habit_categories = {
            'stress_relief': [
                'Deep breathing exercises',
                'Progressive muscle relaxation',
                'Mindful walking',
                'Journaling your thoughts',
                'Listening to calming music'
            ],
            'mood_boost': [
                'Gratitude practice',
                'Physical exercise',
                'Social connection',
                'Creative activities',
                'Nature exposure'
            ],
            'anxiety_management': [
                'Grounding techniques',
                'Regular sleep schedule',
                'Limiting caffeine',
                'Mindfulness meditation',
                'Structured daily routine'
            ],
            'depression_support': [
                'Daily movement',
                'Social engagement',
                'Goal setting',
                'Positive self-talk',
                'Professional support seeking'
            ],
            'general_wellness': [
                'Regular sleep hygiene',
                'Balanced nutrition',
                'Hydration tracking',
                'Digital detox periods',
                'Hobby development'
            ]
        }
    
    def generate_habit_suggestions(self, user_id: str, current_mood: str, sentiment_score: float, count: int = 3) -> List[Dict[str, str]]:
        """
        Generate personalized habit suggestions.
        
        Args:
            user_id: User identifier
            current_mood: Current detected mood
            sentiment_score: Current sentiment score
            count: Number of suggestions to generate
            
        Returns:
            List of habit suggestions with descriptions
        """
        try:
            # Get user history for context
            user_profile = self.firestore_service.get_user_profile(user_id)
            recent_sessions = self.firestore_service.get_user_sessions(user_id, limit=5)
            
            # Determine appropriate habit categories based on mood
            categories = self._select_habit_categories(current_mood, sentiment_score)
            
            # Generate personalized suggestions
            suggestions = []
            
            for category in categories[:count]:
                base_habits = self.habit_categories.get(category, [])
                
                if base_habits:
                    # Select a random habit from the category
                    habit = random.choice(base_habits)
                    
                    # Generate personalized description
                    description = self._generate_habit_description(
                        habit, category, current_mood, user_profile
                    )
                    
                    suggestions.append({
                        'habit': habit,
                        'category': category,
                        'description': description,
                        'difficulty': self._assess_difficulty(sentiment_score),
                        'estimated_time': self._estimate_time(category)
                    })
            
            logger.info(f"Generated {len(suggestions)} habit suggestions for user: {user_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating habit suggestions: {str(e)}")
            # Return fallback suggestions
            return [
                {
                    'habit': 'Take a few deep breaths',
                    'category': 'stress_relief',
                    'description': 'Simple breathing exercise to help you feel more centered',
                    'difficulty': 'easy',
                    'estimated_time': '2-3 minutes'
                }
            ]
    
    def _select_habit_categories(self, mood: str, sentiment_score: float) -> List[str]:
        """
        Select appropriate habit categories based on mood and sentiment.
        
        Args:
            mood: Current mood
            sentiment_score: Sentiment score
            
        Returns:
            List of relevant habit categories
        """
        categories = []
        
        # Mood-based category selection
        if mood in ['stressed', 'anxious']:
            categories.extend(['stress_relief', 'anxiety_management'])
        elif mood in ['sad', 'very_sad']:
            categories.extend(['mood_boost', 'depression_support'])
        elif mood in ['happy', 'very_happy', 'excited']:
            categories.extend(['general_wellness', 'mood_boost'])
        elif mood == 'tired':
            categories.extend(['general_wellness', 'stress_relief'])
        else:
            categories.extend(['general_wellness', 'mood_boost'])
        
        # Sentiment-based adjustments
        if sentiment_score < 0.3:
            categories.insert(0, 'depression_support')
        elif sentiment_score > 0.7:
            categories.insert(0, 'mood_boost')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_categories = []
        for cat in categories:
            if cat not in seen:
                seen.add(cat)
                unique_categories.append(cat)
        
        return unique_categories
    
    def _generate_habit_description(self, habit: str, category: str, mood: str, user_profile) -> str:
        """
        Generate a personalized description for a habit.
        
        Args:
            habit: The habit name
            category: Habit category
            mood: Current mood
            user_profile: User profile data
            
        Returns:
            Personalized habit description
        """
        try:
            prompt = f"""
            Create a personalized, encouraging description for this mental health habit:
            
            Habit: {habit}
            Category: {category}
            Current mood: {mood}
            User experience level: {user_profile.total_sessions if user_profile else 0} sessions
            
            Make the description:
            1. Encouraging and non-judgmental
            2. Specific and actionable
            3. Tailored to their current emotional state
            4. Brief (1-2 sentences)
            5. Focused on benefits they'll experience
            
            Description:
            """
            
            response = self.model.generate_content(prompt)
            description = response.text.strip()
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating habit description: {str(e)}")
            return f"Try {habit.lower()} to help improve your well-being."
    
    def _assess_difficulty(self, sentiment_score: float) -> str:
        """
        Assess the difficulty level based on current sentiment.
        
        Args:
            sentiment_score: Current sentiment score
            
        Returns:
            Difficulty level (easy, medium, hard)
        """
        if sentiment_score < 0.3:
            return 'easy'  # When feeling down, suggest easier habits
        elif sentiment_score < 0.6:
            return 'medium'
        else:
            return 'medium'  # When feeling good, can handle moderate challenges
    
    def _estimate_time(self, category: str) -> str:
        """
        Estimate time required for habit category.
        
        Args:
            category: Habit category
            
        Returns:
            Estimated time string
        """
        time_estimates = {
            'stress_relief': '5-10 minutes',
            'mood_boost': '15-30 minutes',
            'anxiety_management': '10-20 minutes',
            'depression_support': '20-45 minutes',
            'general_wellness': 'varies'
        }
        
        return time_estimates.get(category, '10-15 minutes')
    
    def get_weekly_habit_report(self, user_id: str) -> Dict[str, any]:
        """
        Generate a weekly habit report for the user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Weekly habit report
        """
        try:
            # Get mood analytics for the week
            mood_history = self.firestore_service.get_user_mood_history(user_id, days=7)
            
            if not mood_history:
                return {
                    'summary': 'No data available for this week',
                    'trend': 'No trend detected',
                    'recommendations': ['Start tracking your mood to get personalized insights']
                }
            
            # Analyze trends
            avg_sentiment = sum(analytics.average_sentiment for analytics in mood_history) / len(mood_history)
            
            # Determine trend
            if len(mood_history) >= 2:
                recent_avg = mood_history[-1].average_sentiment
                earlier_avg = mood_history[0].average_sentiment
                if recent_avg > earlier_avg + 0.1:
                    trend = 'improving'
                elif recent_avg < earlier_avg - 0.1:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Generate recommendations
            if trend == 'improving':
                recommendations = [
                    'Keep up the great work!',
                    'Consider adding more challenging wellness activities',
                    'Share your positive progress with others'
                ]
            elif trend == 'declining':
                recommendations = [
                    'Be gentle with yourself during difficult times',
                    'Consider reaching out to a mental health professional',
                    'Focus on small, manageable self-care activities'
                ]
            else:
                recommendations = [
                    'Try introducing new wellness activities',
                    'Consider tracking specific mood triggers',
                    'Explore different coping strategies'
                ]
            
            return {
                'summary': f'Your average mood this week was {avg_sentiment:.2f}/1.0',
                'trend': trend,
                'recommendations': recommendations,
                'total_sessions': sum(analytics.session_count for analytics in mood_history),
                'total_messages': sum(analytics.total_messages for analytics in mood_history)
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
            return {
                'summary': 'Unable to generate report at this time',
                'trend': 'unknown',
                'recommendations': ['Continue using the app for better insights']
            }
