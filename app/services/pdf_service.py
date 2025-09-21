from pdf2image import convert_from_bytes
from typing import List, Tuple
import io
import logging
import os

logger = logging.getLogger(__name__)

A4_WIDTH = 660
A4_HEIGHT = 933

class PDFService:
    @staticmethod
    async def convert_to_png(pdf_content: bytes) -> Tuple[List[bytes], int]:
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
            total_pages = len(images)
            selected_images = []
            if total_pages <= 5:
                # If 5 or fewer pages, take all
                selected_images = images
            else:
                # Take first 3 pages
                selected_images.extend(images[:3])
                # Take last 2 pages
                selected_images.extend(images[-2:])

            # Convert each image to PNG bytes
            png_images = []
            for i, image in enumerate(selected_images):
                # Convert to PNG format
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                png_images.append(img_byte_arr.getvalue())
            return png_images, total_pages

        except Exception as e:
            logger.error(f"Error converting PDF to PNG: {str(e)}")
            raise


pdf_service = PDFService()
