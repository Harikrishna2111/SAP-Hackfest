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
    # Switched to gemini-pro-latest because flash models are hitting strict 20 req/day limits
    MODEL_NAME  = os.getenv("GEMINI_MODEL", "gemini-pro-latest")
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

