from google.cloud import storage
from datetime import datetime
from typing import Dict, Any, List
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        """Initialize the storage service with Google Cloud Storage client."""
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.BUCKET_NAME)

    async def upload_file(self, content: bytes, filename: str, content_type: str, folder: str = "") -> Dict[str, Any]:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            content (bytes): The file content
            filename (str): Original filename
            content_type (str): MIME type of the file
            
        Returns:
            Dict containing upload details including URL and path
        """
        # Generate folder structure based on current date

        
        # Create blob path with date-based structure
        blob_name = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_name)
        
        # Upload the file
        blob.upload_from_string(
            content,
            content_type=content_type
        )
        
        return {
            "gcs_url": blob.public_url,
            "gcs_path": blob_name,
            "content_type": content_type,
            "file_size": len(content)
        }

    async def upload_png_images(self, images: List[bytes], original_filename: str) -> List[Dict[str, Any]]:
        """
        Upload multiple PNG images to Google Cloud Storage.
        
        Args:
            images (List[bytes]): List of PNG images as bytes
            original_filename (str): Original PDF filename
            
        Returns:
            List of upload results for each image
        """
        results = []
        for i, image in enumerate(images):
            # Create PNG filename from original PDF filename
            png_filename = f"page_{i+1}.png"
            
            # Upload the PNG
            result = await self.upload_file(
                content=image,
                filename=png_filename,
                content_type="image/png",
                folder=original_filename
            )
            results.append(result)
            
            logger.info(f"Uploaded PNG {i+1} of {len(images)}")
        
        return results
    
    async def download_file(self, filename: str) -> bytes:
        """
        Download a file from Google Cloud Storage.
        """
        blob = self.bucket.blob(filename)
        return blob.download_as_bytes()
    

# Create a singleton instance
storage_service = StorageService() 