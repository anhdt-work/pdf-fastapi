import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

_TRIM_CHARS = " \t\r\n/\\-–—_.:,;|•·*~+!@#$%^&=<>?\"'`()[]{}"

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

    def _clean_symbol(s: str) -> str:
        return s.strip(_TRIM_CHARS)
    
    def parse_document_number(text: str) -> tuple[str, str]:
        """
        Trả về (number, symbol)
        Ví dụ:
          "123-ABC45"        -> ("123", "ABC45")
          "123"              -> ("123", "")
          "ABC45"            -> ("", "ABC45")
          "123 - ABC45"      -> ("123", "ABC45")
          "123/ABC45"        -> ("123", "ABC45")
          "123/ABC45-123"    -> ("123", "ABC45-123")
          "123/ABC45/123"    -> ("123", "ABC45/123")
          "Số: 26/BC-ĐT"     -> ("26", "BC-ĐT")
          "No: 123/ABC"      -> ("123", "ABC")
          "123 -  /BC-ĐT"    -> ("123", "BC-ĐT")
        """
        try:
            if not text:
                return "", ""

            t = text.strip()
            t = re.sub(r'^(?:Số|So|No)\s*:?\s*', '', t, flags=re.IGNORECASE).strip()
            m = re.match(r'^(\d+)(.*)$', t)
            if m:
                number = m.group(1)
                symbol = _clean_symbol(m.group(2))
                return number, symbol

            return "", _clean_symbol(t)

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