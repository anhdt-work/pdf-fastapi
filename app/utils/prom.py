GET_FULL_TEXT_PROMPT = """ 
<image>\n Lấy toàn bộ nội dung của văn bản này, hạn chế thay đổi cấu trúc và nội dung văn bản
"""

GET_DETAIL_PROMPT = """
<image>\n Lấy tên cơ quan tổ chức ban hành (Thường ở góc trên bên trái). 
Số và kí hiệu của văn bản (thuờng ở bên dưới tên cơ quan ban hành).
Ngày ban hành văn bản (thường ở góc trên bên phải văn bản).
Tên loại và trích yếu nội dung văn bản (thường phần trên chính giữa văn bản)
"""