from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
from app.services.pdf_service import pdf_service
from app.services.storage_service import storage_service
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gcs", tags=["Google Cloud Storage"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_key: Optional[str] = None
):
    """
    Upload a file to GCS with key-based folder structure.
    If no folder_key is provided, a new one will be generated.
    
    Returns:
        Dict with upload details including the folder key
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload to GCS with folder structure
        result = await storage_service.upload_file_to_folder(
            content=content,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            folder_key=folder_key
        )
        
        logger.info(f"File uploaded successfully: {file.filename} to folder {result['folder_key']}")
        return await pdf_service.convert_pdf_in_gcs_folder_to_png_local(folder_key)
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/download/{folder_key}/{filename}")
async def download_file(folder_key: str, filename: str):
    """
    Download a file from GCS using folder key and filename.
    
    Args:
        folder_key: The folder key
        filename: The filename to download
        
    Returns:
        File content as streaming response
    """
    try:
        # Download file from GCS
        content = await storage_service.download_file_from_folder(
            folder_key=folder_key,
            filename=filename
        )
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/list/{folder_key}")
async def list_files(folder_key: str):
    """
    List all files in a specific folder.
    
    Args:
        folder_key: The folder key
        
    Returns:
        List of file information
    """
    try:
        files = await storage_service.list_files_in_folder(folder_key=folder_key)
        
        return {
            "success": True,
            "folder_key": folder_key,
            "file_count": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.delete("/delete/{folder_key}/{filename}")
async def delete_file(folder_key: str, filename: str):
    """
    Delete a specific file from a folder.
    
    Args:
        folder_key: The folder key
        filename: The filename to delete
        
    Returns:
        Success status
    """
    try:
        success = await storage_service.delete_file_from_folder(
            folder_key=folder_key,
            filename=filename
        )
        
        if success:
            return {
                "success": True,
                "message": f"File {filename} deleted successfully from folder {folder_key}"
            }
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.delete("/delete-folder/{folder_key}")
async def delete_folder(folder_key: str):
    """
    Delete an entire folder and all its contents.
    
    Args:
        folder_key: The folder key to delete
        
    Returns:
        Success status
    """
    try:
        success = await storage_service.delete_folder(folder_key=folder_key)
        
        if success:
            return {
                "success": True,
                "message": f"Folder {folder_key} and all contents deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Folder not found or empty")
            
    except Exception as e:
        logger.error(f"Error deleting folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.post("/generate-key")
async def generate_key():
    """
    Generate a new folder key for future uploads.
    
    Returns:
        The generated key
    """
    try:
        key = storage_service.generate_key()
        
        return {
            "success": True,
            "folder_key": key,
            "message": "New folder key generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}") 