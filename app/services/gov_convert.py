from pdf2image import convert_from_bytes
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageEnhance, ImageOps
import io
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


class GovernmentDocPDFService:
    """
    Optimized PDF service for Vietnamese government administrative documents.
    Balanced for text extraction accuracy while maintaining performance.
    """

    # Optimal settings for government documents (mostly text with tables/stamps)
    DOCUMENT_PRESETS = {
        'fast': {
            'dpi': 150,
            'max_width': 1024,
            'max_height': 1448,  # A4 ratio
            'description': 'Nhanh, phù hợp văn bản thuần text'
        },
        'balanced': {
            'dpi': 200,
            'max_width': 1280,
            'max_height': 1810,  # A4 ratio
            'description': 'Cân bằng tốc độ và chất lượng OCR'
        },
        'accurate': {
            'dpi': 250,
            'max_width': 1536,
            'max_height': 2172,  # A4 ratio
            'description': 'Chính xác cao cho văn bản có dấu mộc, chữ ký'
        },
        'maximum': {
            'dpi': 300,
            'max_width': 1920,
            'max_height': 2715,  # A4 ratio
            'description': 'Tối đa chất lượng cho văn bản quan trọng'
        }
    }

    # Recommended for Qwen2.5-VL with government docs
    RECOMMENDED_PRESET = 'balanced'

    def __init__(
            self,
            preset: str = 'balanced',
            enable_text_enhancement: bool = True,
            enable_table_detection: bool = False,
            output_format: str = 'JPEG'
    ):
        """
        Initialize service for government documents.

        Args:
            preset: Quality preset ('fast', 'balanced', 'accurate', 'maximum')
            enable_text_enhancement: Enhance text clarity for better OCR
            enable_table_detection: Optimize for table extraction
            output_format: 'JPEG' or 'PNG' (JPEG recommended for size)
        """
        self.config = self.DOCUMENT_PRESETS.get(preset, self.DOCUMENT_PRESETS['balanced'])
        self.enable_text_enhancement = enable_text_enhancement
        self.enable_table_detection = enable_table_detection
        self.output_format = output_format

        logger.info(f"Initialized with preset '{preset}': {self.config['description']}")
        logger.info(f"Image size: {self.config['max_width']}x{self.config['max_height']}px")

    def enhance_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Enhance image specifically for Vietnamese text OCR.

        Args:
            image: Input PIL Image

        Returns:
            Enhanced PIL Image
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert('RGB')

        # 1. Increase contrast for text
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(1.3)  # Higher for text documents

        # 2. Sharpen for clearer edges
        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(1.2)

        # 3. Adjust brightness if needed
        # Government docs often have gray backgrounds
        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(1.05)

        # 4. Denoise while preserving text
        # Convert to numpy for advanced processing
        img_array = np.array(image)

        # Simple denoising for scanned documents
        from scipy.ndimage import median_filter
        if img_array.shape[2] == 3:  # RGB
            for i in range(3):
                img_array[:, :, i] = median_filter(img_array[:, :, i], size=1)

        image = Image.fromarray(img_array)

        return image

    def optimize_for_tables(self, image: Image.Image) -> Image.Image:
        """
        Optimize image for table detection and extraction.

        Args:
            image: Input PIL Image

        Returns:
            Optimized PIL Image
        """
        # Enhance grid lines and borders
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(1.4)

        # Make lines more distinct
        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(1.5)

        return image

    async def convert_government_doc(
            self,
            pdf_content: bytes,
            page_numbers: Optional[List[int]] = None
    ) -> Dict[str, any]:
        """
        Convert government PDF document to optimized images.

        Args:
            pdf_content: PDF file bytes
            page_numbers: Specific pages to convert (None = all)

        Returns:
            Dictionary with images and metadata
        """
        try:
            # Conversion parameters
            convert_params = {
                'dpi': self.config['dpi'],
                'fmt': 'png',  # Initial format for quality
                'thread_count': min(os.cpu_count() or 4, 8),
                'use_pdftocairo': True,  # Better for text documents
            }

            # Add page selection if specified
            if page_numbers:
                convert_params['first_page'] = min(page_numbers)
                convert_params['last_page'] = max(page_numbers)

            logger.info(f"Converting PDF with DPI={self.config['dpi']}")

            # Convert PDF to images
            images = convert_from_bytes(pdf_content, **convert_params)

            processed_images = []
            metadata = []
            total_size = 0

            for i, image in enumerate(images):
                page_num = page_numbers[i] if page_numbers else i + 1

                # Calculate target size maintaining A4 ratio
                target_width = self.config['max_width']
                target_height = self.config['max_height']

                # Get original size
                orig_width, orig_height = image.size

                # Calculate scale to fit within bounds
                scale = min(
                    target_width / orig_width,
                    target_height / orig_height
                )

                # Only downscale, never upscale
                if scale < 1.0:
                    new_width = int(orig_width * scale)
                    new_height = int(orig_height * scale)

                    # Ensure divisible by 8 for better model compatibility
                    new_width = (new_width // 8) * 8
                    new_height = (new_height // 8) * 8

                    image = image.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )

                    logger.debug(
                        f"Page {page_num}: Resized from {orig_width}x{orig_height} to {new_width}x{new_height}")

                # Apply enhancements
                if self.enable_text_enhancement:
                    image = self.enhance_for_ocr(image)

                if self.enable_table_detection:
                    image = self.optimize_for_tables(image)

                # Convert to bytes
                img_byte_arr = io.BytesIO()

                if self.output_format == 'JPEG':
                    # JPEG with high quality for text
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')

                    image.save(
                        img_byte_arr,
                        format='JPEG',
                        quality=88,  # High quality for text clarity
                        optimize=True,
                        progressive=False,  # Not needed for document processing
                        subsampling=0  # Best quality for text
                    )
                else:
                    # PNG for maximum quality
                    image.save(
                        img_byte_arr,
                        format='PNG',
                        optimize=True,
                        compress_level=3  # Faster compression
                    )

                img_bytes = img_byte_arr.getvalue()
                img_size = len(img_bytes)
                total_size += img_size

                processed_images.append(img_bytes)

                metadata.append({
                    'page': page_num,
                    'width': image.width,
                    'height': image.height,
                    'size_kb': img_size / 1024,
                    'format': self.output_format
                })

                logger.debug(f"Page {page_num}: {image.width}x{image.height}, {img_size / 1024:.1f}KB")

            result = {
                'images': processed_images,
                'metadata': metadata,
                'total_pages': len(processed_images),
                'total_size_mb': total_size / (1024 * 1024),
                'avg_size_kb': (total_size / len(processed_images)) / 1024 if processed_images else 0,
                'config': self.config
            }

            logger.info(
                f"Converted {len(processed_images)} pages, total size: {result['total_size_mb']:.2f}MB")

            return result

        except Exception as e:
            logger.error(f"Error converting government document: {str(e)}")
            raise

    def estimate_processing_time(self, num_pages: int) -> Dict[str, float]:
        """
        Estimate processing time for different presets.

        Args:
            num_pages: Number of pages in document

        Returns:
            Estimated times in seconds for each preset
        """
        # Based on empirical data for RTX A6000
        base_times = {
            'fast': 0.3,  # ~0.3s per page
            'balanced': 0.5,  # ~0.5s per page
            'accurate': 0.8,  # ~0.8s per page
            'maximum': 1.2  # ~1.2s per page
        }

        estimates = {}
        for preset, time_per_page in base_times.items():
            estimates[preset] = {
                'time_seconds': num_pages * time_per_page,
                'description': self.DOCUMENT_PRESETS[preset]['description']
            }

        return estimates

    @staticmethod
    def recommend_preset(document_type: str) -> str:
        """
        Recommend preset based on document type.

        Args:
            document_type: Type of government document

        Returns:
            Recommended preset name
        """
        recommendations = {
            'công_văn': 'balanced',  # Official letters
            'quyết_định': 'accurate',  # Decisions (need stamps)
            'thông_tư': 'balanced',  # Circulars
            'nghị_định': 'balanced',  # Decrees
            'báo_cáo': 'fast',  # Reports (mostly text)
            'biên_bản': 'accurate',  # Minutes (signatures)
            'hợp_đồng': 'accurate',  # Contracts (signatures)
            'hóa_đơn': 'accurate',  # Invoices (stamps, tables)
            'bảng_kê': 'balanced',  # Tables/lists
            'default': 'balanced'
        }

        return recommendations.get(document_type.lower(), 'balanced')


# Usage examples
async def process_government_documents():
    """Example usage for different document types."""

    # 1. Công văn thông thường (Regular official letter)
    service_congvan = GovernmentDocPDFService(
        preset='balanced',  # 1280x1810px, good balance
        enable_text_enhancement=True,
        output_format='JPEG'
    )

    # 2. Quyết định có dấu mộc (Decision with stamps)
    service_quyetdinh = GovernmentDocPDFService(
        preset='accurate',  # 1536x2172px, higher quality
        enable_text_enhancement=True,
        output_format='PNG'  # Better for stamps
    )

    # 3. Báo cáo dài nhiều trang (Long report)
    service_baocao = GovernmentDocPDFService(
        preset='fast',  # 1024x1448px, faster processing
        enable_text_enhancement=True,
        output_format='JPEG'
    )

    # Process example
    with open('congvan.pdf', 'rb') as f:
        pdf_content = f.read()

    # Convert entire document
    result = await service_congvan.convert_government_doc(pdf_content)

    print(f"Processed {result['total_pages']} pages")
    print(f"Total size: {result['total_size_mb']:.2f}MB")
    print(f"Average page size: {result['avg_size_kb']:.1f}KB")

    # Process specific pages only
    result_pages = await service_congvan.convert_government_doc(
        pdf_content,
        page_numbers=[1, 3, 5]  # Only process pages 1, 3, 5
    )

    # Get processing time estimates
    estimates = service_congvan.estimate_processing_time(num_pages=10)
    for preset, info in estimates.items():
        print(f"{preset}: {info['time_seconds']:.1f}s - {info['description']}")


# Quick initialization for common use cases
def get_service_for_document(doc_type: str = 'công_văn') -> GovernmentDocPDFService:
    """Get optimized service for specific document type."""
    preset = GovernmentDocPDFService.recommend_preset(doc_type)
    return GovernmentDocPDFService(preset=preset)


# Default service instance
gov_pdf_service = GovernmentDocPDFService(preset='balanced')