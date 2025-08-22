from pdf2image import convert_from_bytes
from typing import List
import io
import logging
import os

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    async def convert_to_png(pdf_content: bytes) -> List[bytes]:
        """
        Convert PDF content to a list of PNG images.
        
        Args:
            pdf_content (bytes): The PDF file content
            
        Returns:
            List[bytes]: List of PNG images as bytes
        """
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_content)
            
            # Convert each image to PNG bytes
            png_images = []
            for i, image in enumerate(images):
                # Convert to PNG format
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                png_images.append(img_byte_arr.getvalue())

                logger.info(f"Converted page {i+1} to PNG")
            
            return png_images
            
        except Exception as e:
            logger.error(f"Error converting PDF to PNG: {str(e)}")
            raise

pdf_service = PDFService() 