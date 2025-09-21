import gc
import platform
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import unicodedata
import json
import asyncio
import base64
from typing import Dict, Any, List
import gc
import os
from concurrent.futures import ThreadPoolExecutor
import os 
from typing import Dict, Any, List

import torch
from app.services.pdf_service import pdf_service
from app.services.gov_convert import gov_pdf_service
# from app.services.vintern import vintern_ai_service
from app.services.qwenvision import qwen_service
from app.services.parser import parser
import logging
from app.template.result import result

from app.utils.prom import GET_AUTHOR, GET_DATE_PROMPT, GET_DOCUMENT_NUMBER, GET_FULL_TEXT_PROMPT, GET_TITLE_PROMPT, \
    GET_DOCUMENT_SIGNED

from app.services.tesseract import tesseract_service
from app.services.deepseek import deepseek_service
logger = logging.getLogger(__name__)

router = APIRouter(tags=["PDF"])

@router.post("/upload/qwen/jpeg/opt", response_model=Dict[str, Any])
async def upload_pdf_qwen_optimized(file: UploadFile = File(...)) -> JSONResponse:
    """
    Optimized PDF upload endpoint with better memory management
    """
    error = 'Start'
    processor = None

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
        png_images, total_page = await pdf_service.convert_to_png(content)

        # Initialize optimized processor
        processor = OptimizedPDFProcessor(qwen_service, max_pages=5)

        # Process images without saving to disk
        extracted_data = await processor.process_pdf_optimized(png_images)

        print("\nDone Processing")

        # Parse results
        error = 'Parse date'
        day, month, year = parser.parse_date(extracted_data["date_data"])

        error = 'Parse document number'
        document_number, document_symbol = parser.parse_document_number(extracted_data["document_number_data"])

        # Build result
        result = {}
        result['SheetTotal'] = total_page
        result['IssuedYear'] = year
        result['Field1'] = extracted_data["author_data"]
        result['Field2'] = document_number
        result['Field3'] = document_symbol
        result['Field6'] = f"{day}/{month}/{year}"
        result['Field7'] = extracted_data["doc_type"]
        result['Field8'] = parser.parse_full_title(extracted_data["title_data"])
        result['Field11'] = extracted_data["final_signed"]
        result['Field13'] = day
        result['Field14'] = month
        result['Field15'] = year
        result['Field32'] = "Thường"
        result['Field33'] = "Tiếng Việt"
        result['Field34'] = "Bản chính"
        result['Field35'] = ""
        result['Field36'] = ""
        result['SearchMeta'] = parser.remove_accents(
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
        result['IsHandWriting'] = extracted_data.get("is_full_handwritten", 0)

        # Light cleanup
        del png_images
        del content
        gc.collect()

        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error processing PDF '{file.filename if file and file.filename else 'unknown'}': {str(e)} and error: {error}")
        raise HTTPException(status_code=500, detail=f"Internal server error while processing PDF: {str(e)}")
    finally:
        # Cleanup processor
        if processor and hasattr(processor, 'executor'):
            processor.executor.shutdown(wait=False)

        # Final memory cleanup
        gc.collect()


class OptimizedPDFProcessor:
    def __init__(self, qwen_service, max_pages=4):
        self.qwen_service = qwen_service
        self.max_pages = max_pages
        self.executor = ThreadPoolExecutor(max_workers=2)  # Parallel processing

    def is_valid_data(self, value: str) -> bool:
        """Check if data is valid (not empty or 'Không có')"""
        if not value:
            return False
        return value.lower() not in ("không có", "khong co", "", "00/00/0000")

    def process_image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 data URL"""
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_image}"

    async def process_single_image(self, image_bytes: bytes, page_num: int) -> Dict[str, Any]:
        """Process single image without saving to disk"""
        try:
            # Convert to base64 for direct processing
            image_data_url = self.process_image_to_base64(image_bytes)

            # Process with Qwen (runs in thread to avoid blocking)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self.qwen_service.get_response_ocr,
                image_data_url
            )

            return response

        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            return {}

    def merge_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, str]:
        """Merge multiple AI responses into final result"""
        result = {
            "date_data": "",
            "document_number_data": "",
            "author_data": "",
            "title_data": "",
            "doc_type": "",
            "final_signed": "",
            "is_full_handwritten": 0
        }

        field_mapping = {
            "date_data": "ngay_ban_hanh",
            "document_number_data": "so_van_ban",
            "author_data": "co_quan",
            "title_data": "trich_yeu",
            "doc_type": "loai_van_ban",
            "final_signed": "nguoi_ky",
            "is_full_handwritten": "is_full_handwritten"
        }

        # Priority: first valid value wins, except for final_signed (last valid wins)
        for response in responses:
            for result_key, response_key in field_mapping.items():
                response_value = response.get(response_key, "")

                if result_key == "final_signed":
                    # For signature, take the last valid one
                    if self.is_valid_data(response_value):
                        result[result_key] = response_value
                elif result_key == "is_full_handwritten":
                    # For handwritten flag, if any response says 1, set to 1
                    if response_value == 1 or response_value == "1":
                        result[result_key] = 1
                else:
                    # For other fields, take first valid one
                    if not self.is_valid_data(result[result_key]) and self.is_valid_data(response_value):
                        result[result_key] = response_value

        return result

    async def process_pdf_optimized(self, png_images: List[bytes]) -> Dict[str, str]:
        """Main processing function with optimizations"""
        # Limit to max_pages for performance
        images_to_process = png_images[:self.max_pages]

        print(f"Processing {len(images_to_process)} pages (max: {self.max_pages})")

        # Process images in parallel (but limit concurrency to avoid GPU overload)
        semaphore = asyncio.Semaphore(1)  # Process one at a time for now

        async def process_with_semaphore(image_bytes, page_num):
            async with semaphore:
                return await self.process_single_image(image_bytes, page_num)

        # Create tasks for parallel processing
        tasks = [
            process_with_semaphore(image_bytes, i + 1)
            for i, image_bytes in enumerate(images_to_process)
        ]

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and merge results
        valid_responses = [r for r in responses if isinstance(r, dict) and r]
        merged_result = self.merge_responses(valid_responses)

        print(f"Processed {len(valid_responses)}/{len(images_to_process)} pages successfully")

        return merged_result