from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json


class DeepSeekService:
    _instance = None
    _chain = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if DeepSeekService._chain is None:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """Bạn là một chuyên gia trích xuất dữ liệu từ các văn bản hành chính. 
                    Hãy trả về dưới định dạng JSON với các trường sau:
                    {{
                        "have_data": "Trả về True hoặc False nếu đây là trang dùng để trích xuất dữ liệu các trường bên dưới, nếu là trang bìa hoặc trang không có dữ liệu thì trả về False",
                        "co_quan": "Cơ quan ban hành văn bản này",
                        "so_van_ban" : "Sô hiệu của văn bản ", # Thường có dạng 4433/BYT-KCB 
                        "ngay_ban_hanh": "DD/MM/YYYY", # Nếu không có hoặc thiếu giá trị nào để giá trị 00 cho giá trị đó nếu là ngày và tháng, 0000 cho năm
                        "loai_van_ban": "Đây là loại văn bản gì",
                        "trich_yeu": "Tên của văn bản này",
                        "nguoi_ky": "Người ký văn bản này" 
                    }}
                    Giữ nguyên giá trị của các trường sao cho đúng với văn bản gốc nhất có thể, Nếu không có giá trị nào thì để giá trị Không có."""),
                ("human","{question}"),
            ])

            model = OllamaLLM(
                model="deepseek-v2:16b-lite-chat-fp16",
                temperature=0.1,
                top_k=50,
                top_p=0.95,
                format="json"
            )
            DeepSeekService._chain = prompt_template | model

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
            json_response = json.loads(response)
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

deepseek_service = DeepSeekService()
