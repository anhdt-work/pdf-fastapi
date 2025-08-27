import re
import unicodedata

class Parser:
    def __init__(self):
        pass
    
    def parse_date(self, text: str) -> list[str | None]:
        # parse date from text format DD-MM-YYYY or DD/MM/YYYY or YYYY-MM-DD or YYYY/MM/DD or YYYY-MM  return a list [day, month, year]
        if not text:
            return ["", "", ""]
        
        # Try different date formats
        date_patterns = [
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}\.\d{2}\.\d{4}', # DD.MM.YYYY
            r'\d{4}-\d{2}-\d{2}', # YYYY-MM-DD
            r'\d{4}/\d{2}/\d{2}', # YYYY/MM/DD
            r'\d{4}-\d{2}', # YYYY-MM
        ]
        
        for pattern in date_patterns:
            date = re.search(pattern, text)
            if date:
                date_str = date.group(0)
                # Split by the separator found in the pattern
                if '-' in date_str:
                    parts = date_str.split('-')
                elif '/' in date_str:
                    parts = date_str.split('/')
                elif '.' in date_str:
                    parts = date_str.split('.')
                else:
                    continue
                
                if len(parts) == 3:
                    # Check if this is YYYY-MM-DD or YYYY/MM/DD format
                    if len(parts[0]) == 4 and parts[0].isdigit():
                        # YYYY-MM-DD format -> return [day, month, year]
                        return [parts[2], parts[1], parts[0]]
                    else:
                        # DD-MM-YYYY format -> return [day, month, year]
                        return [parts[0], parts[1], parts[2]]
                elif len(parts) == 2:
                    return ["", parts[1], parts[0]]
        
        return ["", "", ""]

    def format_text(text: str) -> str:
        return re.sub(r'^[^0-9\wÀ-ỹ]+|[^0-9\wÀ-ỹ]+$', '', text, flags=re.UNICODE).strip()
    
    def parse_document_number(self, text: str) -> tuple[str, str]:
        # parse document number from text format NUMBER-SYMBOL or NUMBER, return a tuple [number, symbol] 
        # Example: 123-ABC45 -> (123, ABC45)
        # Example: 123 -> (123, "")
        # Example: ABC45 -> ("", ABC45)
        # Example: 123 - ABC45 -> (123, ABC45)  # handles spaces around hyphen
        # Example: 123/ABC45 -> (123, ABC45)
        # Example: 123/ABC45-123 -> (123, ABC45-123)
        # Example: 123/ABC45/123 -> (123, ABC45/123)
        # Example: Số: 26/BC-ĐT -> (26, BC-ĐT)
        # Example: No: 123/ABC -> (123, ABC)
        try:
            if not text:
                return "", ""

            text = text.strip()

            # Bỏ prefix thường gặp
            text = re.sub(r'^(Số:|So:|No:)\s*', '', text, flags=re.IGNORECASE).strip()

            parts = []
            is_number = False
            for i, char in enumerate(text):
                if char.isdigit():
                    is_number = True
                if is_number and not char.isdigit() and i > 0:
                    parts = [text[:i], text[i:]]
                    break

            if len(parts) == 1:
                if parts[0].isdigit():
                    return parts[0], ""
                else:
                    return "", format_text(parts[0])

            if not parts or len(parts) == 0:
                return "", ""

            number_part = parts[0].strip()
            symbol_part = parts[1].strip() if len(parts) > 1 else ""

            # Convert number part thành số
            numb = "".join([c for c in number_part if c.isdigit()])

            return numb, format_text(symbol_part)
        except Exception:
            return "", ""
    
    def parse_author(self, text: str):
        pass

    def parse_title(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        
        try:
            text = text.strip()
            for title in titles:
                if title.lower() in text.lower():
                    return title
            return ""
        except Exception:
            return ""

    def parse_full_title(self, text: str) -> str | None:
        try:
            part = text.split("*")
            if len(part) > 1:
                return part[-1].lstrip()
            return text
        except Exception:
            return text

    def remove_accents(self, text: str):
        if not unicodedata.is_normalized("NFC", text):
            text = unicodedata.normalize("NFC", text)
        return text.translate(BANG_XOA_DAU)

BANG_XOA_DAU = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
)


titles = [
    "Nghị quyết",
    "Quyết định",
    "Chỉ thị",
    "Quy chế",
    "Quy định",
    "Thông cáo",
    "Thông báo",
    "Hướng dẫn",
    "Chương trình",
    "Kế hoạch",
    "Phương án",
    "Đề án",
    "Dự án",
    "Báo cáo",
    "Biên bản",
    "Tờ trình",
    "Hợp đồng",
    "Công văn",
    "Công điện",
    "Bản ghi nhớ",
    "Bản thỏa thuận",
    "Giấy ủy quyền",
    "Giấy mời",
    "Giấy giới thiệu",
    "Giấy nghỉ phép",
    "Phiếu gửi",
    "Phiếu chuyển",
    "Phiếu báo",
    "Thư công"
]

def format_text(text: str) -> str:
    text = text.strip()
    if text and text[0] == "-":
        text = text[1:]
    # remove all multiple spaces and newlines
    text = text.replace("\n", "")
    text = text.replace("Kí hiệu", "")
    text = text.replace("Kí hiệu:", "")
    text = text.replace("Số", "")
    text = text.replace("Số:", "")
    text = text.replace(":", "")
    return text

parser = Parser()