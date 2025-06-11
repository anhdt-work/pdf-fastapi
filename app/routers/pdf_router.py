from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
from typing import Dict, Any, List
from app.services.storage_service import storage_service
from app.services.pdf_service import pdf_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload/", response_model=Dict[str, Any])
async def upload_pdf(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload a PDF file, convert it to PNG, and store in Google Cloud Storage.
    
    Args:
        file (UploadFile): The PDF file to upload
        
    Returns:
        JSONResponse containing upload details and metadata
    """
    try:
        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Read file content
        content = await file.read()
        
        # Convert PDF to PNG
        png_images = await pdf_service.convert_to_png(content)
        
        # Upload PNG images to Google Cloud Storage
        logger.info("Uploading PNG images to Google Cloud Storage...")
        upload_results = await storage_service.upload_png_images(
            images=png_images,
            original_filename=file.filename.replace('.pdf', '')
        )
        
        # Read metadata from result.json if it exists
        try:
            with open('result.json', 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except FileNotFoundError:
            metadata = {}
        
        # Combine upload results with metadata
        response_data = {
            **metadata,
            "filename": file.filename,
            "total_pages": len(png_images),
            "png_uploads": upload_results
        }
        
        return JSONResponse(
            content=response_data,
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 