from google.cloud import storage
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config.settings import settings
import logging
import uuid
import os

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        """Initialize the storage service with Google Cloud Storage client."""
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.BUCKET_NAME)

    def generate_key(self) -> str:
        """
        Generate a unique key for folder creation.
        
        Returns:
            str: A unique key string
        """
        return str(uuid.uuid4())

    async def upload_file_to_folder(self, content: bytes, filename: str, content_type: str, folder_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to a specific folder in Google Cloud Storage.
        If no folder_key is provided, a new one will be generated.
        
        Args:
            content (bytes): The file content
            filename (str): Original filename
            content_type (str): MIME type of the file
            folder_key (str, optional): The folder key. If None, a new one will be generated
            
        Returns:
            Dict containing upload details including URL, path, and folder key
        """
        if folder_key is None:
            folder_key = self.generate_key()
        
        # Create blob path with folder structure
        blob_name = f"{folder_key}/{filename}"
        blob = self.bucket.blob(blob_name)
        
        # Upload the file
        blob.upload_from_string(
            content,
            content_type=content_type
        )
        
        logger.info(f"Uploaded file {filename} to folder {folder_key}")
        
        return {
            "gcs_url": blob.public_url,
            "gcs_path": blob_name,
            "folder_key": folder_key,
            "content_type": content_type,
            "file_size": len(content),
            "filename": filename
        }

    async def download_file_from_folder(self, folder_key: str, filename: str) -> bytes:
        """
        Download a file from a specific folder in Google Cloud Storage.
        
        Args:
            folder_key (str): The folder key
            filename (str): The filename to download
            
        Returns:
            bytes: The file content
            
        Raises:
            Exception: If file not found or download fails
        """
        blob_name = f"{folder_key}/{filename}"
        blob = self.bucket.blob(blob_name)
        
        if not blob.exists():
            raise FileNotFoundError(f"File {filename} not found in folder {folder_key}")
        
        content = blob.download_as_bytes()
        logger.info(f"Downloaded file {filename} from folder {folder_key}")
        
        return content

    async def list_files_in_folder(self, folder_key: str) -> List[Dict[str, Any]]:
        """
        List all files in a specific folder.
        
        Args:
            folder_key (str): The folder key
            
        Returns:
            List of file information dictionaries
        """
        prefix = f"{folder_key}/"
        blobs = self.bucket.list_blobs(prefix=prefix)
        
        files = []
        for blob in blobs:
            # Skip the folder itself
            if blob.name == prefix:
                continue
                
            files.append({
                "filename": os.path.basename(blob.name),
                "gcs_path": blob.name,
                "gcs_url": blob.public_url,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated
            })
        
        logger.info(f"Listed {len(files)} files in folder {folder_key}")
        return files

    async def delete_file_from_folder(self, folder_key: str, filename: str) -> bool:
        """
        Delete a file from a specific folder.
        
        Args:
            folder_key (str): The folder key
            filename (str): The filename to delete
            
        Returns:
            bool: True if deletion was successful
        """
        blob_name = f"{folder_key}/{filename}"
        blob = self.bucket.blob(blob_name)
        
        if not blob.exists():
            logger.warning(f"File {filename} not found in folder {folder_key}")
            return False
        
        blob.delete()
        logger.info(f"Deleted file {filename} from folder {folder_key}")
        return True

    async def delete_folder(self, folder_key: str) -> bool:
        """
        Delete an entire folder and all its contents.
        
        Args:
            folder_key (str): The folder key to delete
            
        Returns:
            bool: True if deletion was successful
        """
        prefix = f"{folder_key}/"
        blobs = self.bucket.list_blobs(prefix=prefix)
        
        deleted_count = 0
        for blob in blobs:
            blob.delete()
            deleted_count += 1
        
        logger.info(f"Deleted folder {folder_key} with {deleted_count} files")
        return deleted_count > 0

    async def upload_file(self, content: bytes, filename: str, content_type: str, folder: str = "") -> Dict[str, Any]:
        """
        Upload a file to Google Cloud Storage (legacy method for backward compatibility).
        
        Args:
            content (bytes): The file content
            filename (str): Original filename
            content_type (str): MIME type of the file
            
        Returns:
            Dict containing upload details including URL and path
        """
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
            # Create PNG filename as 1.PNG, 2.PNG, ...
            png_filename = f"{i+1}.PNG"
            
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
        Download a file from Google Cloud Storage (legacy method for backward compatibility).
        """
        blob = self.bucket.blob(filename)
        return blob.download_as_bytes()
    

# Create a singleton instance
storage_service = StorageService() 