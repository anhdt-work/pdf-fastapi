import io
from typing import Tuple

import PyPDF2
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
import os


async def process_pdf_from_content(content: bytes) -> Tuple[bytes, int]:
    """
    Xử lý PDF từ binary content và lấy 3 trang đầu + 2 trang cuối

    Args:
        content (bytes): Dữ liệu binary của file PDF
    Returns:
        Tuple[bytes, int]: Trả về bytes của PDF mới và tổng số trang
    """
    input_stream = None
    output_stream = None

    try:
        # Tạo BytesIO object từ content
        input_stream = io.BytesIO(content)

        # Đọc PDF từ stream
        pdf_reader = PyPDF2.PdfReader(input_stream)
        total_pages = len(pdf_reader.pages)

        print(f"PDF có {total_pages} trang")

        # Kiểm tra số trang tối thiểu
        if total_pages < 5:
            print("Cảnh báo: PDF có ít hơn 5 trang. Sẽ lấy tất cả các trang có sẵn.")

        # Tạo PDF writer
        pdf_writer = PyPDF2.PdfWriter()

        # Lấy 3 trang đầu
        pages_to_extract = min(3, total_pages)
        for i in range(pages_to_extract):
            page = pdf_reader.pages[i]
            pdf_writer.add_page(page)
            print(f"Đã thêm trang {i + 1}")

        # Lấy 2 trang cuối (nếu có đủ trang và không trùng với 3 trang đầu)
        if total_pages > 3:
            last_pages_to_extract = min(2, total_pages - 3)
            start_index = total_pages - last_pages_to_extract

            for i in range(start_index, total_pages):
                page = pdf_reader.pages[i]
                pdf_writer.add_page(page)
                print(f"Đã thêm trang {i + 1}")

        output_stream = io.BytesIO()
        pdf_writer.write(output_stream)
        output_bytes = output_stream.getvalue()
        output_stream.close()

        print(f"Đã tạo PDF trong memory với {len(pdf_writer.pages)} trang")
        return output_bytes, total_pages

    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {str(e)}")
        raise
    finally:
        # Đóng input stream
        if input_stream:
            input_stream.close()
        if output_stream:
            output_stream.close()


class GoogleService:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self, project_id=None, location=None, processor_id=None, mime_type=None,
                 field_mask=None, processor_version_id=None, credentials_file=None):
        if self._initialized:
            return

        if credentials_file and os.path.exists(credentials_file):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

        self.mime_type = mime_type
        self.field_mask = field_mask

        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com", credentials_file=credentials_file)
        try:
            self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        except Exception as e:
            print(f"Lỗi khi tạo DocumentAI client: {e}")
            raise

        if processor_version_id:
            # The full resource name of the processor version, e.g.:
            # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
            self.name = self.client.processor_version_path(
                project_id, location, processor_id, processor_version_id
            )
        else:
            # The full resource name of the processor, e.g.:
            # `projects/{project_id}/locations/{location}/processors/{processor_id}`
            self.name = self.client.processor_path(project_id, location, processor_id)

        self._initialized = True
        print(f"GoogleService initialized với processor: {self.name}")

    def process_document(self, content: bytes) -> dict:
        try:
            raw_document = documentai.RawDocument(content=content, mime_type=self.mime_type)
            request = documentai.ProcessRequest(
                name=self.name,
                raw_document=raw_document,
                field_mask=self.field_mask,
            )
            result = self.client.process_document(request=request)
            document = result.document
            extract_data = {}
            if hasattr(document, 'entities') and document.entities:
                for i, entity in enumerate(document.entities):
                    extract_data[entity.type_] = entity.mention_text
            else:
                print("Không tìm thấy entities trong document")

            return extract_data
        except Exception as e:
            print(f"Lỗi khi xử lý document: {e}")
            raise


def create_google_service(credentials_file=None):
    """
    Factory function để tạo GoogleService
    """
    return GoogleService(
        project_id="pdf-to-text-469514",
        location="us",
        processor_id="76aaa781c27b4c19",
        mime_type="application/pdf",
        field_mask="entities",
        processor_version_id="pretrained-foundation-model-v1.5-pro-2025-06-20",
        credentials_file=credentials_file
    )

# google_service = GoogleService(project_id="pdf-to-text-469514", location="us", processor_id="76aaa781c27b4c19", mime_type="application/pdf", field_mask="entities", processor_version_id = "pretrained-foundation-model-v1.5-pro-2025-06-20")

# project_id = "pdf-to-text-469514"
# location = "us"  # Format is "us" or "eu"
# processor_id = "76aaa781c27b4c19"  # Create processor before running sample
# file_path = r"C:\Users\admin\Downloads\SL\SL\BDV\A44-006-03-0238\A44-006-03-0238-004\A44-006-03-0238-004.pdf"
# mime_type = "application/pdf"  # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
# field_mask = "entities"  # Optional. The fields to return in the Document object.
# processor_version_id = "pretrained-foundation-model-v1.5-pro-2025-06-20"  # Optional. Processor version to use
