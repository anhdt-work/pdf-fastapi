GET_FULL_TEXT_PROMPT = """ <image>\n Lấy toàn bộ nội dung của văn bản này, hạn chế thay đổi cấu trúc và nội dung văn bản"""

GET_DATE_PROMPT = """<image>\n Lấy ngày ban hành văn bản, trả về dưới dạng DD-MM-YYYY (thường ở góc trên bên phải văn bản)."""

GET_DOCUMENT_NUMBER = """<image>\n Lấy số và kí hiệu của văn bản, trả về dưới dạng NUMBER-SYMBOL (thuờng ở góc trên bên trái văn bản)."""

GET_AUTHOR = """<image>\n Lấy tên cơ quan tổ chức ban hành, trả về tên cơ quan tổ chức ban hành (Thường ở góc trên bên trái)."""

GET_TITLE_PROMPT = """<image>\n Lấy tên loại và trích yếu nội dung văn bản, trả về tên loại và trích yếu nội dung văn bản (thường phần trên chính giữa văn bản)"""

GET_DOCUMENT_SIGNED = """<image>\n Lấy tên người ký văn bản.Nếu có trả về tên người ký còn không tìm thấy thì trả về 'Không có'."""