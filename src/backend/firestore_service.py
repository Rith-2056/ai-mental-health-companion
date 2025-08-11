import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from google.cloud.firestore import DocumentReference, CollectionReference
import logging

# Use absolute imports
import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import UserProfile, ChatMessage, ChatSession, MoodAnalytics, MoodType
from firestore_config import FirestoreConfig

logger = logging.getLogger(__name__)

class FirestoreService:
    """Service layer for Firestore database operations."""
    
    def __init__(self, firestore_config: FirestoreConfig):
        """
        Initialize Firestore service.
        
        Args:
            firestore_config: Firestore configuration instance
        """
        self.db = firestore_config.get_db()
        self.users_collection = self.db.collection('users')
        self.sessions_collection = self.db.collection('sessions')
        self.messages_collection = self.db.collection('messages')
        self.analytics_collection = self.db.collection('analytics')
    
    def create_user_profile(self, user_id: str) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Created user profile
        """
        now = datetime.utcnow()
        user_profile = UserProfile(
            user_id=user_id,
            created_at=now,
            last_active=now,
            preferences={}
        )
        
        # Save to Firestore
        doc_ref = self.users_collection.document(user_id)
        doc_ref.set(user_profile.to_dict())
        
        logger.info(f"Created user profile for user: {user_id}")
        return user_profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile or None if not found
        """
        doc_ref = self.users_collection.document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return UserProfile.from_dict(doc.to_dict())
        return None
    
    def update_user_activity(self, user_id: str) -> None:
        """
        Update user's last active timestamp.
        
        Args:
            user_id: User identifier
        """
        doc_ref = self.users_collection.document(user_id)
        doc_ref.update({
            'last_active': datetime.utcnow().isoformat(),
            'total_sessions': firestore.Increment(1)
        })
    
    def create_chat_session(self, user_id: str) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Created chat session
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            started_at=now,
            is_active=True
        )
        
        # Save to Firestore
        doc_ref = self.sessions_collection.document(session_id)
        doc_ref.set(session.to_dict())
        
        logger.info(f"Created chat session: {session_id} for user: {user_id}")
        return session
    
    def end_chat_session(self, session_id: str) -> None:
        """
        End a chat session.
        
        Args:
            session_id: Session identifier
        """
        doc_ref = self.sessions_collection.document(session_id)
        doc_ref.update({
            'ended_at': datetime.utcnow().isoformat(),
            'is_active': False
        })
        
        logger.info(f"Ended chat session: {session_id}")
    
    def save_chat_message(self, message: ChatMessage) -> None:
        """
        Save a chat message to Firestore.
        
        Args:
            message: Chat message to save
        """
        # Save message
        doc_ref = self.messages_collection.document(message.message_id)
        doc_ref.set(message.to_dict())
        
        # Update session message count
        session_ref = self.sessions_collection.document(message.session_id)
        session_ref.update({
            'message_count': firestore.Increment(1)
        })
        
        # Update user total messages
        user_ref = self.users_collection.document(message.user_id)
        user_ref.update({
            'total_messages': firestore.Increment(1)
        })
        
        logger.info(f"Saved message: {message.message_id}")
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of chat messages
        """
        query = self.messages_collection.where('session_id', '==', session_id).order_by('timestamp')
        docs = query.stream()
        
        messages = []
        for doc in docs:
            messages.append(ChatMessage.from_dict(doc.to_dict()))
        
        return messages
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[ChatSession]:
        """
        Get recent sessions for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of chat sessions
        """
        query = self.sessions_collection.where('user_id', '==', user_id).order_by('started_at', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        
        sessions = []
        for doc in docs:
            sessions.append(ChatSession.from_dict(doc.to_dict()))
        
        return sessions
    
    def save_mood_analytics(self, analytics: MoodAnalytics) -> None:
        """
        Save mood analytics data.
        
        Args:
            analytics: Mood analytics to save
        """
        # Use date as document ID for daily analytics
        doc_id = analytics.date.strftime('%Y-%m-%d')
        doc_ref = self.analytics_collection.document(doc_id)
        doc_ref.set(analytics.to_dict(), merge=True)
        
        logger.info(f"Saved mood analytics for date: {doc_id}")
    
    def get_user_mood_history(self, user_id: str, days: int = 30) -> List[MoodAnalytics]:
        """
        Get mood history for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            List of mood analytics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = self.analytics_collection.where('user_id', '==', user_id).where('date', '>=', start_date.isoformat())
        docs = query.stream()
        
        analytics = []
        for doc in docs:
            analytics.append(MoodAnalytics.from_dict(doc.to_dict()))
        
        return analytics