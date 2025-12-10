"""Configuration settings for the debate system"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database Configuration
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Model Configuration
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Debate Configuration
    MAX_ROUNDS: int = 5
    MIN_ARGUMENT_LENGTH: int = 50
    MAX_ARGUMENT_LENGTH: int = 500
    
    # Memory Configuration
    MAX_MEMORY_SIZE: int = 100  # Number of conversations to keep
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True

# Validate config on import
Config.validate()