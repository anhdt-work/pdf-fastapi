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

    @staticmethod
    async def convert_pdf_in_gcs_folder_to_png_local(folder_key: str):
        """
        Find the PDF file in the given GCS folder, download it, convert to PNG images, and save PNGs locally as 1.PNG, 2.PNG, ... in a folder named after folder_key.
        Args:
            folder_key (str): The GCS folder key containing the PDF file
        Returns:
            List of local file paths for each PNG image
        """
        from app.services.storage_service import storage_service
        # List files in the folder
        files = await storage_service.list_files_in_folder(folder_key)
        # Find the first PDF file
        pdf_file = next((f for f in files if f['filename'].lower().endswith('.pdf')), None)
        if not pdf_file:
            raise FileNotFoundError(f"No PDF file found in folder {folder_key}")
        # Download the PDF file
        pdf_content = await storage_service.download_file_from_folder(folder_key, pdf_file['filename'])
        # Convert PDF to PNG images
        png_images = await PDFService.convert_to_png(pdf_content)
        # Prepare local folder
        local_folder = os.path.join(os.getcwd(), folder_key)
        os.makedirs(local_folder, exist_ok=True)
        # Save PNG images locally
        local_paths = []
        for i, img_bytes in enumerate(png_images):
            local_path = os.path.join(local_folder, f"{i+1}.PNG")
            with open(local_path, 'wb') as f:
                f.write(img_bytes)
            local_paths.append(local_path)
        return local_paths

pdf_service = PDFService() 