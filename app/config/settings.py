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
        # Google Cloud Storage settings
        self.BUCKET_NAME = os.getenv('BUCKET_NAME')
        if not self.BUCKET_NAME:
            raise ValueError("BUCKET_NAME environment variable is required")
        
        # Server settings
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', '8000'))
        
        # API settings
        self.API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
        self.API_TITLE = os.getenv('API_TITLE', 'PDF Storage API')
        self.API_VERSION = os.getenv('API_VERSION', '1.0.0')
        
        # Google Cloud Storage credentials
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not self.GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
        
        # Verify credentials file exists and is readable
        creds_path = Path(self.GOOGLE_APPLICATION_CREDENTIALS)
        if not creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
        
        if not os.access(creds_path, os.R_OK):
            raise PermissionError(f"No permission to read credentials file at: {creds_path}")
        
        # Set environment variable for Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path.absolute())
        logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {creds_path.absolute()}")

# Create settings instance
settings = Settings()