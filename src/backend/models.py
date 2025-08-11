from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class MoodType(Enum):
    """Enumeration for different mood types."""
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "very_sad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    CALM = "calm"
    EXCITED = "excited"
    TIRED = "tired"

@dataclass
class UserProfile:
    """User profile data model."""
    user_id: str
    created_at: datetime
    last_active: datetime
    total_sessions: int = 0
    total_messages: int = 0
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize preferences if None."""
        if self.preferences is None:
            self.preferences = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary from Firestore."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        return cls(**data)

@dataclass
class ChatMessage:
    """Individual chat message data model."""
    message_id: str
    user_id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    mood_detected: Optional[MoodType] = None
    sentiment_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.mood_detected:
            data['mood_detected'] = self.mood_detected.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary from Firestore."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('mood_detected'):
            data['mood_detected'] = MoodType(data['mood_detected'])
        return cls(**data)

@dataclass
class ChatSession:
    """Chat session data model."""
    session_id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int = 0
    average_mood: Optional[MoodType] = None
    overall_sentiment: Optional[float] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat()
        if self.ended_at:
            data['ended_at'] = self.ended_at.isoformat()
        if self.average_mood:
            data['average_mood'] = self.average_mood.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create from dictionary from Firestore."""
        data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('ended_at'):
            data['ended_at'] = datetime.fromisoformat(data['ended_at'])
        if data.get('average_mood'):
            data['average_mood'] = MoodType(data['average_mood'])
        return cls(**data)

@dataclass
class MoodAnalytics:
    """Mood analytics data model."""
    user_id: str
    date: datetime
    mood_distribution: Dict[str, int]  # mood_type -> count
    average_sentiment: float
    total_messages: int
    session_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        data = asdict(self)
        data['date'] = self.date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoodAnalytics':
        """Create from dictionary from Firestore."""
        data['date'] = datetime.fromisoformat(data['date'])
        return cls(**data)
    