"""
Configuration settings for the AI Mental Health Companion.
"""

import os
from typing import Optional

class Config:
    """Configuration class for the application."""
    
    # API Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    
    # Chatbot Configuration
    MAX_CONVERSATION_LENGTH = 50  # Maximum number of messages to keep in memory
    RESPONSE_TIMEOUT = 30  # Seconds to wait for API response
    
    # UI Configuration
    PAGE_TITLE = "AI Mental Health Companion"
    PAGE_ICON = "🧠"
    
    # Security
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.GOOGLE_API_KEY:
            print("❌ GOOGLE_API_KEY environment variable is required")
            return False
        return True 