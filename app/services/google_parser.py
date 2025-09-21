import re
import unicodedata


class GoogleParser:
    def __init__(self):
        pass

    def parse_date(self, text):
        match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", text, re.IGNORECASE)
        day, month, year = match.groups()
        return f"{int(day):02d}", f"{int(month):02d}", year

    def parse_document_number(self, text):
        parts = text.split("-", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return text.strip(), ""

    def parse_doc_type(self, text):
        text = self.remove_accents(text)
        first_words = " ".join(text.split()[:3]).lower()
        default_title = "Nghị quyết"
        for title in titles:
            if self.remove_accents(title.lower()) in first_words:
                return title
        return default_title

    def remove_accents(self, text: str):
        if not unicodedata.is_normalized("NFC", text):
            text = unicodedata.normalize("NFC", text)
        return text.translate(BANG_XOA_DAU)


BANG_XOA_DAU = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A" * 17 + "D" + "E" * 11 + "I" * 5 + "O" * 17 + "U" * 11 + "Y" * 5 + "a" * 17 + "d" + "e" * 11 + "i" * 5 + "o" * 17 + "u" * 11 + "y" * 5
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
    return re.sub(r'^\W+|\W+$', '', text).strip()


google_parser = GoogleParser()
