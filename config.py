"""
Configuration settings for TalentScout Hiring Assistant
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    
    # Security
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_CONVERSATION_LENGTH = int(os.getenv('MAX_CONVERSATION_LENGTH', 50))
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    
    # Conversation Settings
    MAX_QUESTIONS_PER_TECH = 3
    MIN_ANSWER_LENGTH = 10
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # Supported Languages
    SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'hi']
    DEFAULT_LANGUAGE = 'en'
    
    # UI Settings
    PAGE_TITLE = "TalentScout Hiring Assistant"
    PAGE_ICON = "🤖"
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = ['GEMINI_API_KEY', 'ENCRYPTION_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
