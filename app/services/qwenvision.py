from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
import torch
import json
import gc
import threading
import time


class QwenVisionService:
    _instance = None
    _chain = None
    _model_loaded = False
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not QwenVisionService._model_loaded:
            with QwenVisionService._lock:
                if not QwenVisionService._model_loaded:
                    self._init_optimized_chain()
                    QwenVisionService._model_loaded = True

    def _init_optimized_chain(self):
        """Tối ưu prompt cho A6000"""
        print("Initializing optimized chain for RTX A6000...")

        # Prompt ngắn gọn để giảm tokens
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Trích xuất JSON từ văn bản:
            {{
              "have_data": true/false,
              "co_quan": "Cơ quan",
              "so_van_ban": "Số văn bản", 
              "ngay_ban_hanh": "DD/MM/YYYY",
              "loai_van_ban": "Loại",
              "trich_yeu": "Trích yếu",
              "nguoi_ky": "Người ký"
            }}"""),
                    ("human", [{"type": "image_url", "image_url": {"url": "{question}"}}]),
        ])

        # Cấu hình tối ưu cho A6000 48GB
        model = ChatOllama(
            model="qwen2.5vl:32b-q8_0",
            temperature=0.1,
            format="json",
            options={
                # Tối ưu cho A6000
                "num_ctx": 2048,  # Tăng context để tận dụng VRAM
                "num_predict": 512,  # Đủ cho JSON response
                "num_keep": 0,  # Không giữ context cũ
                "num_batch": 4,  # A6000 có thể handle batch lớn hơn
                "num_thread": 8,  # Tận dụng CPU threads
                "numa": True,  # Enable NUMA cho performance
                "use_mmap": True,  # Memory mapping
                "use_mlock": True,  # Lock memory
                "low_vram": False,# Không cần low_vram với 48GB
            }
        )
        QwenVisionService._chain = prompt_template | model
        print("Chain initialized successfully")


    def get_response_ocr(self, question: str):
        """
        Gửi câu hỏi và nhận response dạng JSON
        """
        response = ""
        try:
            # Invoke chain
            response = self._chain.invoke({"question": question})
            print("Raw response from model:", response)

            # Parse JSON response
            if hasattr(response, "content"):
                response_content = response.content
            else:
                response_content = response
            json_response = json.loads(response_content)
            return json_response
        except json.JSONDecodeError as e:
            # Xử lý lỗi nếu response không phải JSON hợp lệ
            return {
                "answer": response,  # Trả về raw response
                "error": f"JSON parsing error: {str(e)}"
            }
        except Exception as e:
            return {
                "answer": "Error occurred while processing request",
                "error": str(e)
            }

qwen_service = QwenVisionService()
