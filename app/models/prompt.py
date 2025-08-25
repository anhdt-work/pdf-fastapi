class PROMPT:
    def __init__(self):
        self.date_prompt = """<image>\n Lấy ngày ban hành văn bản, trả về  dưới dạng DD-MM-YYYY (thường ở góc trên bên phải văn bản)."""
        self.fulltext_prompt = """<image>\n Lấy toàn bộ nội dung văn bản dưới dạng text và giữ nguyên cấu trúc"""
        self.document_number_prompt = """<image>\n Lấy số và kí hiệu của văn bản (thuờng ở góc trên bên trái văn bản)."""
        self.document_name_prompt = """<image>\n Lấy tên của văn bản (thuờng ở góc trên chính giữa văn bản)."""

    def get_date_prompt(self):
        return self.date_prompt

    def get_fulltext_prompt(self):
        return self.fulltext_prompt

    def get_document_number_prompt(self):
        return self.document_number_prompt

    def get_document_name_prompt(self):
        return self.document_name_prompt
