from pdf2image import convert_from_bytes
from typing import List
import io
import logging
import os

logger = logging.getLogger(__name__)

A4_WIDTH = 2480
A4_HEIGHT = 3508

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
            images = convert_from_bytes(pdf_content, dpi=300, fmt='png', size=(A4_WIDTH, A4_HEIGHT))

            # Convert each image to PNG bytes
            png_images = []
            for i, image in enumerate(images):
                # Convert to PNG format
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                png_images.append(img_byte_arr.getvalue())
            return png_images

        except Exception as e:
            logger.error(f"Error converting PDF to PNG: {str(e)}")
            raise


pdf_service = PDFService()
