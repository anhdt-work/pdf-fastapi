import glob

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any


from app.services.google import process_pdf_from_content
from app.services.google_parser import google_parser
import logging

from google.cloud import documentai  # type: ignore
logger = logging.getLogger(__name__)

router = APIRouter(tags=["PDF"])
from app.services.google import create_google_service


def get_credentials_file():
    json_files = glob.glob("app/cloud/*.json")
    if json_files:
        return json_files[0]  # Return first match
    raise FileNotFoundError("No JSON credentials file found in app/cloud/")

@router.post("/upload/google/", response_model=Dict[str, Any])
async def upload_pdf_google(file: UploadFile = File(...)) -> JSONResponse:
    """
    Optimized PDF upload endpoint with better memory management
    """

    try:
        # Validation (same as before)
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        if file.content_type and file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed")

        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Convert PDF to PNG
        bytes_pdf, total_page = await process_pdf_from_content(content)

        google_service = create_google_service(get_credentials_file())
        # Initialize optimized processor

        # Process images without saving to disk
        extracted_data = await google_service.process_document(bytes_pdf)

        print("\nDone Processing")

        # Parse results
        error = 'Parse date'
        day, month, year = google_parser.parse_date(extracted_data["ngay_ban_hanh"])

        error = 'Parse document number'
        document_number, document_symbol = google_parser.parse_document_number(extracted_data["so_quyet_dinh"])

        # Build result
        result = {}
        result['SheetTotal'] = total_page
        result['IssuedYear'] = year
        result['Field1'] = extracted_data["co_quan"]
        result['Field2'] = document_number
        result['Field3'] = document_symbol
        result['Field6'] = f"{day}/{month}/{year}"
        result['Field7'] = google_parser.parse_doc_type(extracted_data["ten_tai_lieu"])
        result['Field8'] = extracted_data["ten_tai_lieu"]
        result['Field11'] = extracted_data["nguoi_ky"]
        result['Field13'] = day
        result['Field14'] = month
        result['Field15'] = year
        result['Field32'] = "Thường"
        result['Field33'] = "Tiếng Việt"
        result['Field34'] = "Bản chính"
        result['Field35'] = ""
        result['Field36'] = ""
        result['SearchMeta'] = google_parser.remove_accents(
            f"{result['Field1']} {result['Field2']} {result['Field3']} {result['Field7']} {result['Field13']} {result['Field14']} {result['Field15']} {result['Field32']} {result['Field33']} {result['Field34']} {result['Field35']} {result['Field36']}").lower()
        result['ContentLength'] = 0  # No full text processing
        result['PageCountA0'] = 0
        result['PageCountA1'] = 0
        result['PageCountA2'] = 0
        result['PageCountA3'] = 0
        result['PageCountA4'] = total_page
        result['PageCountA5'] = 0
        result['PageCountOther'] = 0
        result['PageCount2A0'] = 0
        result['PageCount3A0'] = 0
        result['PageCount4A0'] = 0
        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error processing PDF '{file.filename if file and file.filename else 'unknown'}': {str(e)} and error: {error}")
        raise HTTPException(status_code=500, detail=f"Internal server error while processing PDF: {str(e)}")


