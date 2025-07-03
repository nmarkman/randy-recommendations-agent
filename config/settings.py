"""
Configuration management for Randy recommendation agent.
Loads all settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Settings:
    """Configuration settings for Randy."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    
    # Email Configuration
    GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    
    # Randy Configuration
    REGION = os.getenv('REGION', 'Charleston, SC')
    QUIET_HOURS_START = int(os.getenv('QUIET_HOURS_START', '23'))
    QUIET_HOURS_END = int(os.getenv('QUIET_HOURS_END', '7'))
    RECOMMENDATION_CADENCE_DAYS = int(os.getenv('RECOMMENDATION_CADENCE_DAYS', '7'))
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present."""
        required_settings = [
            'OPENAI_API_KEY',
            'GOOGLE_PLACES_API_KEY', 
            'TMDB_API_KEY',
            'GMAIL_USERNAME',
            'GMAIL_APP_PASSWORD',
            'RECIPIENT_EMAIL'
        ]
        
        missing = []
        for setting in required_settings:
            if not getattr(cls, setting):
                missing.append(setting)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

# Global settings instance
settings = Settings() 