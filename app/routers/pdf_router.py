from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
# import uuid
import json
import os 
from typing import Dict, Any, List
from app.services.pdf_service import pdf_service
from app.services.vintern import vintern_ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload/", response_model=Dict[str, Any])
async def upload_pdf(list_index: str, file: UploadFile = File(...)) -> JSONResponse:
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
        first_page_indexes = set(map(int, list_index.strip().split(',')))
        if not first_page_indexes:
            first_page_indexes = {1}

        # Read file content
        content = await file.read()
        
        # Convert PDF to PNG
        png_images = await pdf_service.convert_to_png(content)
        
        # Create a unique folder for this upload
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        folder_name = file.filename.split('.')[0]
        folder_key = os.path.join(parent_dir, "images", folder_name)
        os.makedirs(folder_key, exist_ok=True)
        
        # Save images to the folder
        for i, image in enumerate(png_images):
            png_filename = os.path.join(folder_key, f"{i+1}.PNG")
            with open(png_filename, 'wb') as f:
                f.write(image)
                
        
        # Process image to AI model
        for i, image in enumerate(png_images):
            pixel_values = VinternAIService.generate_input(image)
           
            # For example: await ai_model.process_image(image, first_page_indexes)
            logger.info(f"Processed page {i+1} with AI model")
        
        
        # Combine upload results with metadata
        response_data = {
            **metadata,
            "filename": file.filename,
            "total_pages": len(png_images),
            # "png_uploads": upload_results
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