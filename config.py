"""
Configuration module for the Verilog Verification Agent
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the agent"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Agent Settings
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))   # keep lower to save quota

    # Model Settings — override via GEMINI_MODEL env var
    # Since gemini-1.5-flash is not found, we use gemini-2.0-flash
    MODEL_NAME  = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    TEMPERATURE = 0.2
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
        return True

# Validate configuration on import
Config.validate()

