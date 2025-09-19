import re

import pytesseract
import os
import cv2
import numpy as np

# def setup_tesseract():
#     """Setup Tesseract cho Google Colab"""
#     pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
#     try:
#         langs = pytesseract.get_languages(config='')
#         print(f"✓ Tesseract sẵn sàng. Ngôn ngữ: {langs}")
#         return True
#     except Exception as e:
#         print(f"✗ Lỗi: {e}")
#         return False

class TesseractService:
    def __init__(self, dpi = 300, lang='vie', max_chars = 200, psm = 6, pixel_margin = 20):
        self.tesseract_path = '/usr/bin/tesseract'
        self.dpi = dpi
        self.lang = lang
        self.max_chars = max_chars
        self.psm = psm
        self.pixel_margin = pixel_margin
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        try:
            langs = pytesseract.get_languages(config='vie')
            print(f"✓ Tesseract sẵn sàng. Ngôn ngữ: {langs}")
        except Exception as e:
            print(f"✗ Lỗi: {e}")

    @staticmethod
    def read_image(path):
        """Đọc ảnh từ file"""
        img = cv2.imread(path)
        if img is None:
            print(f"✗ Không đọc được ảnh: {path}")
        return img

    def get_image_size(self, img):
        """Lấy kích thước ảnh"""
        h, w = img.shape[:2]
        return w, h

    def calculate_a4_size(self):
        """Tính kích thước A4 theo pixel"""
        # A4: 210mm x 297mm
        inch_to_mm = 25.4
        w = int(210 / inch_to_mm * self.dpi)
        h = int(297 / inch_to_mm * self.dpi)
        return w, h

    def resize_to_a4(self, img):
        """Resize ảnh về kích thước A4"""
        a4_w, a4_h = self.calculate_a4_size()
        h, w = img.shape[:2]

        # Tính tỷ lệ
        scale_w = a4_w / w
        scale_h = a4_h / h
        scale = min(scale_w, scale_h)

        # Resize
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        # Tạo canvas A4 trắng
        if len(img.shape) == 3:
            canvas = np.ones((a4_h, a4_w, 3), dtype=np.uint8) * 255
        else:
            canvas = np.ones((a4_h, a4_w), dtype=np.uint8) * 255

        # Đặt ảnh vào giữa
        y_off = (a4_h - new_h) // 2
        x_off = (a4_w - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized

        print(f"✓ Resized: {w}x{h} → A4 {a4_w}x{a4_h} (DPI={self.dpi})")
        return canvas

    def convert_to_gray(self, img):
        """Chuyển ảnh sang grayscale"""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def denoise_image(self, img):
        """Khử nhiễu ảnh"""
        img = cv2.bilateralFilter(img, 9, 75, 75)
        img = cv2.medianBlur(img, 3)
        return img

    def enhance_contrast(self, img):
        """Tăng độ tương phản"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        return clahe.apply(img)

    def binarize_image(self, img):
        """Chuyển ảnh sang binary (đen trắng)"""
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def clean_image(self, img):
        """Làm sạch ảnh với morphology"""
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        return img

    def preprocess_for_ocr(self, img):
        """
        Tiền xử lý ảnh cho OCR

        Args:
            img: Ảnh đầu vào
            resize_a4: Có resize về A4 không
            dpi: DPI cho A4 (150, 200, 300, 600)
        """

        # Chuyển sang gray
        img = self.convert_to_gray(img)

        # Khử nhiễu
        img = self.denoise_image(img)

        # Tăng contrast
        img = self.enhance_contrast(img)

        # Binary
        img = self.binarize_image(img)

        # Làm sạch
        img = self.clean_image(img)

        return img

    def extract_text_boxes(self, img):
        """
        Trích xuất bounding boxes từ ảnh

        Args:
            img: Ảnh đã xử lý
            lang: Ngôn ngữ ('vie', 'eng', 'vie+eng')
        """
        config = f'--psm {self.psm}'
        data = pytesseract.image_to_data(img, lang=self.lang, config=config,
                                         output_type=pytesseract.Output.DICT)

        boxes = []
        n = len(data['text'])

        for i in range(n):
            if data['text'][i].strip():
                box = {
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'text': data['text'][i],
                    'conf': data['conf'][i],
                    'block': data['block_num'][i],
                    'line': data['line_num'][i],
                    'word': data['word_num'][i]
                }
                boxes.append(box)

        print(f"✓ Tìm thấy {len(boxes)} text boxes")
        return boxes


    def check_overlap(self, box1, box2, margin=5):
        """
        Kiểm tra 2 boxes có overlap không

        Args:
            box1, box2: Hai boxes cần kiểm tra
            margin: Khoảng cách pixel coi là gần nhau
        """
        x1 = box1['x'] - margin
        y1 = box1['y'] - margin
        x1_end = box1['x'] + box1['width'] + margin
        y1_end = box1['y'] + box1['height'] + margin

        x2 = box2['x'] - margin
        y2 = box2['y'] - margin
        x2_end = box2['x'] + box2['width'] + margin
        y2_end = box2['y'] + box2['height'] + margin

        # Kiểm tra overlap
        if x1_end < x2 or x2_end < x1:
            return False
        if y1_end < y2 or y2_end < y1:
            return False
        return True

    def merge_two_boxes(self, box1, box2):
        """Gộp 2 boxes thành 1"""
        x = min(box1['x'], box2['x'])
        y = min(box1['y'], box2['y'])
        x_end = max(box1['x'] + box1['width'], box2['x'] + box2['width'])
        y_end = max(box1['y'] + box1['height'], box2['y'] + box2['height'])

        text1 = box1.get('text', '')
        text2 = box2.get('text', '')

        return {
            'x': x,
            'y': y,
            'width': x_end - x,
            'height': y_end - y,
            'text': f"{text1} {text2}".strip(),
            'conf': min(box1.get('conf', 0), box2.get('conf', 0))
        }

    def merge_overlapping_boxes(self, boxes):
        """
        Gộp các boxes overlap lại với nhau

        Args:
            boxes: Danh sách boxes
        """
        if not boxes:
            return []

        merged = []
        used = [False] * len(boxes)

        for i in range(len(boxes)):
            if used[i]:
                continue

            current = boxes[i].copy()
            used[i] = True

            # Tìm tất cả boxes overlap với current
            merged_any = True
            while merged_any:
                merged_any = False
                for j in range(len(boxes)):
                    if not used[j] and self.check_overlap(current, boxes[j], self.pixel_margin):
                        current = self.merge_two_boxes(current, boxes[j])
                        used[j] = True
                        merged_any = True

            merged.append(current)

        print(f"✓ Đã gộp: {len(boxes)} → {len(merged)} boxes")
        return merged

    def merge_boxes_by_line(self, boxes, y_threshold=10):
        """Gộp boxes theo dòng (cùng tọa độ y)"""
        if not boxes:
            return []

        # Sắp xếp theo y, sau đó x
        sorted_boxes = sorted(boxes, key=lambda b: (b['y'], b['x']))

        lines = []
        current_line = [sorted_boxes[0]]
        current_y = sorted_boxes[0]['y']

        for box in sorted_boxes[1:]:
            # Nếu cùng dòng (y gần nhau)
            if abs(box['y'] - current_y) <= y_threshold:
                current_line.append(box)
            else:
                # Gộp dòng hiện tại
                if current_line:
                    lines.append(self.merge_line_boxes(current_line))
                current_line = [box]
                current_y = box['y']

        # Gộp dòng cuối
        if current_line:
            lines.append(self.merge_line_boxes(current_line))

        print(f"✓ Gộp theo dòng: {len(boxes)} → {len(lines)} dòng")
        return lines

    def merge_line_boxes(self, line_boxes):
        """Gộp các boxes trong cùng 1 dòng"""
        if not line_boxes:
            return None

        x = min(b['x'] for b in line_boxes)
        y = min(b['y'] for b in line_boxes)
        x_end = max(b['x'] + b['width'] for b in line_boxes)
        y_end = max(b['y'] + b['height'] for b in line_boxes)

        # Sắp xếp theo x để ghép text đúng thứ tự
        sorted_boxes = sorted(line_boxes, key=lambda b: b['x'])
        text = ' '.join(b.get('text', '') for b in sorted_boxes)

        return {
            'x': x,
            'y': y,
            'width': x_end - x,
            'height': y_end - y,
            'text': text.strip(),
            'conf': min(b.get('conf', 0) for b in line_boxes)
        }

    # ===== FUNCTION CHÍNH =====


    def extract_all_boxes_text(self, img, boxes):
        """
        Trích xuất text từ tất cả boxes

        Args:
            img: Ảnh đã xử lý (processed image)
            boxes: Danh sách boxes
            max_chars: Số ký tự tối đa mỗi box
        """
        results = []
        total = len(boxes)

        for i, box in enumerate(boxes):

            # Copy box để không thay đổi original
            box_copy = box.copy()

            # Xử lý text
            processed_box = self.process_single_box_text(img, box_copy)
            results.append(processed_box)


        return results

    def process_single_box_text(self, img, box):
        """
        Xử lý text từ một box: OCR, làm sạch, cắt ngắn

        Args:
            img: Ảnh đã xử lý
            box: Box cần xử lý
        """
        # OCR
        text = self.extract_text_from_box(img, box)

        # Làm sạch
        text = self.clean_vietnamese_text(text)

        # Cắt ngắn
        text = self.truncate_text(text)

        # Thêm vào box
        box['extracted_text'] = text
        box['text_length'] = len(text)

        return box


    def extract_text_from_box(self, img, box):
        """
        Trích xuất text từ một box cụ thể

        Args:
            img: Ảnh đã xử lý (processed image)
            box: Dictionary chứa x, y, width, height
        """
        # Lấy tọa độ box
        x = max(0, box['x'])
        y = max(0, box['y'])
        w = box['width']
        h = box['height']

        # Kiểm tra giới hạn ảnh
        img_h, img_w = img.shape[:2]
        x_end = min(x + w, img_w)
        y_end = min(y + h, img_h)

        # Cắt vùng ảnh
        roi = img[y:y_end, x:x_end]

        # OCR vùng đã cắt
        try:
            config = f'--psm {self.psm}'
            text = pytesseract.image_to_string(roi, lang=self.lang, config=config)
            return text.strip()
        except Exception as e:
            print(f"Lỗi OCR tại box ({x},{y}): {e}")
            return ""


    def clean_vietnamese_text(self, text):
        """
        Làm sạch text tiếng Việt

        Args:
            text: Text cần làm sạch
        """
        # Xóa ký tự điều khiển
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Giữ lại chữ cái tiếng Việt, số, và dấu câu cơ bản
        # Danh sách đầy đủ ký tự tiếng Việt
        vietnamese_chars = 'àáảạãăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđĐ'
        allowed_chars = vietnamese_chars + vietnamese_chars.upper()

        # Giữ lại: chữ cái, số, dấu câu, khoảng trắng, và ký tự tiếng Việt
        pattern = f'[^a-zA-Z0-9{allowed_chars}\\s\\.,;:!?\\-–—\\\"()\\[\\]{{}}/]'
        text = re.sub(pattern, ' ', text)

        # Xóa khoảng trắng thừa
        text = ' '.join(text.split())

        return text

    def truncate_text(self, text):
        """
        Cắt text về độ dài tối đa

        Args:
            text: Text đầu vào
        """
        if len(text) <= self.max_chars:
            return text

        # Cắt tại ranh giới từ nếu có thể
        truncated = text[:self.max_chars]
        last_space = truncated.rfind(' ')

        if last_space > self.max_chars * 0.8:  # Nếu có khoảng trắng gần cuối
            return truncated[:last_space] + "..."

        return truncated + "..."

    def process_image_file(self, image_path) -> str:
        """Xử lý toàn bộ từ file ảnh"""
        img = self.read_image(image_path)
        if img is None:
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

        processed = self.preprocess_for_ocr(img)
        boxes = self.extract_text_boxes(processed)
        boxes = self.merge_overlapping_boxes(boxes)
        boxes_with_text = self.extract_all_boxes_text(processed, boxes)

        # Take 5 first boxes with text and 5 last boxes with text
        ocr_texts = 'Đây là phần có tên cơ quan ban hành, số hiệu văn bản, ngày tháng năm ban hành\n'
        for i in range (len(boxes_with_text)):
            if i < 8:
                if not boxes_with_text[i]['extracted_text']:
                    continue
                ocr_texts += f"{boxes_with_text[i]['extracted_text']} \n"
            if i >= len(boxes_with_text) - 3:
                ocr_texts += 'Tìm tên người ký trong này: \n'
                ocr_texts += f"{boxes_with_text[i]['extracted_text']} \n"
        return ocr_texts

tesseract_service = TesseractService()