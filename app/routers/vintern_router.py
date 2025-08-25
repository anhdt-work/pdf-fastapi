from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
from app.services.vintern import vintern_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    message: str = ""

class DateExtractionResponse(BaseModel):
    date: str
    document_number: str
    document_name: str

async def ensure_model_ready():
    """Ensure the model service is ready"""
    if not await vintern_service.is_ready():
        try:
            await vintern_service.initialize()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise HTTPException(
                status_code=503, 
                detail=f"Model not loaded: {str(e)}"
            )

@router.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Vision Language Model API",
        "status": "running",
        "model_loaded": await vintern_service.is_ready()
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    is_ready = await vintern_service.is_ready()
    return {
        "status": "healthy",
        "model_status": "loaded" if is_ready else "not_loaded"
    }

@router.get("/main_page")
async def get_data_main_image_in_image(image_url: str):
    """
    Extract date and document number from an image using the vision-language model.
    
    Args:
        image_url (str): Path to the image file
        
    Returns:
        Dict containing date and document_number
    """
    try:
        await ensure_model_ready()
        
        if not image_url:
            raise HTTPException(status_code=400, detail="image_url parameter is required")
        
        # Use the service to extract date and document number
        result = await vintern_service.extract_date_and_name_and_document_number(image_url)
        
        return DateExtractionResponse(
            date=result["date"],
            document_number=result["document_number"],
            document_name=result["document_name"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/text")
async def get_text_in_image(image_url: str):
    """
    Extract full text content from an image using the vision-language model.
    
    Args:
        image_url (str): Path to the image file
        
    Returns:
        str: Extracted text content
    """
    try:
        await ensure_model_ready()
        
        if not image_url:
            raise HTTPException(status_code=400, detail="image_url parameter is required")
        
        # Use the service to extract full text
        text = await vintern_service.extract_full_text(image_url)
        
        return {
            "text": text,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/chat")
async def chat_with_image(image_url: str, prompt: str):
    """
    Generate a custom chat response for an image with a custom prompt.
    
    Args:
        image_url (str): Path to the image file
        prompt (str): Custom prompt to use
        
    Returns:
        Dict containing the response
    """
    try:
        await ensure_model_ready()
        
        if not image_url:
            raise HTTPException(status_code=400, detail="image_url parameter is required")
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt parameter is required")
        
        # Use the service to generate custom chat response
        response = await vintern_service.generate_chat_response(image_url, prompt)
        
        return {
            "response": response,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/startup")
async def startup_model():
    """Manually trigger model loading"""
    try:
        await ensure_model_ready()
        return {
            "message": "Model loaded successfully",
            "status": "ready"
        }
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )
