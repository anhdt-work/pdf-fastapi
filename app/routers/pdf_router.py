import gc
import platform
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import unicodedata
import json
import os 
from typing import Dict, Any, List

import torch
from app.services.pdf_service import pdf_service
from app.services.vintern import vintern_ai_service
from app.services.parser import parser
import logging
from app.template.result import result

from app.utils.prom import GET_AUTHOR, GET_DATE_PROMPT, GET_DOCUMENT_NUMBER, GET_FULL_TEXT_PROMPT, GET_TITLE_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["PDF"])


@router.post("/upload/", response_model=Dict[str, Any])
async def upload_pdf(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload a PDF file, convert it to PNG, and store in Google Cloud Storage.
    
    Args:
        file (UploadFile): The PDF file to upload
        
    Returns:
        JSONResponse containing upload details and metadata
    """
    folder_name = file.filename.split('.')[0]
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
        
        # Create a unique folder for this upload
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        folder_key = os.path.join(parent_dir, "images", folder_name)
        os.makedirs(folder_key, exist_ok=True)
        # if folder is not empty, remove all files in the folder
        if os.listdir(folder_key):
            for file in os.listdir(folder_key):
                os.remove(os.path.join(folder_key, file))
        
        # Save images to the folder
        for i, image in enumerate(png_images):
            png_filename = os.path.join(folder_key, f"{i+1}.PNG")
            with open(png_filename, 'wb') as f:
                f.write(image)
        
        # Process image to AI model
        full_text = ""
        for i in range(len(png_images)):
            image_path = os.path.join(folder_key, f"{i+1}.PNG")
            pixel_values = vintern_ai_service.generate_input(image_path)
            if i == 0:
                date_data = vintern_ai_service.generate_chat(pixel_values, GET_DATE_PROMPT)
                torch.cuda.empty_cache()  # if using GPU
                gc.collect()
                document_number_data = vintern_ai_service.generate_chat(pixel_values, GET_DOCUMENT_NUMBER)
                torch.cuda.empty_cache()  # if using GPU
                gc.collect()
                author_data = vintern_ai_service.generate_chat(pixel_values, GET_AUTHOR)
                torch.cuda.empty_cache()  # if using GPU
                gc.collect()
                title_data = vintern_ai_service.generate_chat(pixel_values, GET_TITLE_PROMPT)
                torch.cuda.empty_cache()  # if using GPU
                gc.collect()
            full_text += vintern_ai_service.generate_chat(pixel_values, GET_FULL_TEXT_PROMPT)
            torch.cuda.empty_cache()  # if using GPU
            gc.collect()
        day, month, year = parser.parse_date(date_data)
        document_number, document_symbol = parser.parse_document_number(document_number_data)
        # Do all the log here to check each value after parsing
        logger.info(f"Date data: {date_data}")
        logger.info(f"Document number data: {document_number_data}")
        logger.info(f"Author data: {author_data}")
        logger.info(f"Title data: {title_data}")
        logger.info(f"Day: {day}")
        logger.info(f"Month: {month}")
        logger.info(f"Year: {year}")
        logger.info(f"Document number: {document_number}")
        logger.info(f"Document symbol: {document_symbol}")
        logger.info(f"Author: {author_data}")
        logger.info(f"Title: {title_data}")
        
        
        result['SheetTotal'] = len(png_images)
        result['IssuedYear'] = year
        result['Field1'] = author_data
        result['Field2'] = document_number
        result['Field3'] = document_symbol
        result['Field6'] = f"{day}/{month}/{year}"
        result['Field7'] = parser.parse_title(title_data)
        result['Field8'] = title_data
        result['Field11'] = ""
        result['Field13'] = day
        result['Field14'] = month
        result['Field15'] = year
        result['Field32'] = "Thường"
        result['Field33'] = "Tiếng Việt"
        result['Field34'] = "Bản chính"
        result['Field35'] = ""
        result['Field36'] = ""
        result['SearchMeta'] = parser.remove_accents(f"{result['Field1']} {result['Field2']} {result['Field3']} {result['Field7']} {result['Field13']} {result['Field14']} {result['Field15']} {result['Field32']} {result['Field33']} {result['Field34']} {result['Field35']} {result['Field36']}").lower()
        result['ContentLength'] = len(full_text)
        result['PageCountA0'] = 0
        result['PageCountA1'] = 0
        result['PageCountA2'] = 0
        result['PageCountA3'] = 0
        result['PageCountA4'] = len(png_images)
        result['PageCountA5'] = 0
        result['PageCountOther'] = 0
        result['PageCount2A0'] = 0
        result['PageCount3A0'] = 0
        result['PageCount4A0'] = 0
        return JSONResponse(
            content=result,
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing PDF name: {str(folder_name)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 
    


