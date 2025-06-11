from pydantic_settings import BaseSettings
import os
import logging
from typing import Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Google Cloud Storage settings
    BUCKET_NAME: str
    
    # Server settings
    HOST: str
    PORT: int
    
    # API settings
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "PDF Storage API"
    API_VERSION: str = "1.0.0"
    
    # Google Cloud Storage credentials
    GOOGLE_APPLICATION_CREDENTIALS: str 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Verify credentials file exists and is readable
        creds_path = Path(self.GOOGLE_APPLICATION_CREDENTIALS)
        if not creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
        
        if not os.access(creds_path, os.R_OK):
            raise PermissionError(f"No permission to read credentials file at: {creds_path}")
        
        # Set environment variable for Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path.absolute())
        logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {creds_path.absolute()}")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()