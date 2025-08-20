import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', '8000'))
        
        # API settings
        self.API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
        self.API_TITLE = os.getenv('API_TITLE', 'PDF Storage API')
        self.API_VERSION = os.getenv('API_VERSION', '1.0.0')

# Create settings instance
settings = Settings()