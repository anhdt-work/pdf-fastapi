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
                    return [parts[0], parts[1], parts[2]]
                elif len(parts) == 2:
                    return ["", parts[1], parts[0]]
        
        return ["", "", ""]
    
    def parse_document_number(self, text: str) -> tuple[str, str]:
        # parse document number from text format NUMBER-SYMBOL or NUMBER, return a tuple [number, symbol] 
        # Example: 123-ABC45 -> (123, ABC45)
        # Example: 123 -> (123, "")
        # Example: ABC45 -> ("", ABC45)
        # Example: 123 - ABC45 -> (123, ABC45)  # handles spaces around hyphen
        # Example: 123/ABC45 -> (123, ABC45)
        # Example: 123/ABC45-123 -> (123, ABC45-123)
        # Example: 123/ABC45/123 -> (123, ABC45/123)
        # Example: 123/ABC45/123 -> (123, ABC45/123)
        
        if not text:
            return "", ""
        
        # Clean up the text - remove extra spaces and normalize separators
        text = text.strip()
        text = re.sub(r'\s*[-/]\s*', '-', text)  # Convert both - and / to - with no spaces
        
        # Split by hyphen to separate parts
        parts = text.split('-')
        
        if len(parts) == 1:
            # Only one part - check if it's a number or symbol
            if parts[0].isdigit():
                return parts[0], ""
            else:
                return "", parts[0]
        
        # Multiple parts - first part should be number, second part should be symbol
        number_part = parts[0].strip()
        symbol_part = parts[1].strip() if len(parts) > 1 else ""
        
        # Validate that first part is a number
        if not number_part.isdigit():
            return "", symbol_part
        
        return number_part, symbol_part
    
    def parse_author(self, text: str):
        pass

    def parse_title(self, text: str) -> str | None:
        for title in titles:
            if title.lower() in text.lower():
                return title
        return ""
    
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


parser = Parser()