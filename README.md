# PDF to Text API

A FastAPI application that processes PDF files and returns structured data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start at http://127.0.0.1:8000

## API Endpoints

### POST /extract-text/
Upload a PDF file and get structured data in response.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: PDF file

**Response:**
```json
{
    "NAM": null,
    "STT": 19,
    "TEN": "Dynamic",
    "NGAYCONGBO": null,
    "NGAYTHUTHAP": null,
    "LOAIHINHTAILIEUID": "d322a7cc-f876-4f73-a192-639a6a5ea3af",
    "TENLOAIHINHTL": "Tài liệu giấy",
    "STATUS": 50,
    "TRANGTHAILUUTRU": 0,
    "SOKYHIEU": null,
    "KYHIEUTT": null,
    "NGAYBDTL": null,
    "NGAYBDTLTHIEU": null,
    "TACGIA": null,
    "BUTTICH": null,
    "SOTO": null,
    "CHEDOSUDUNG": null,
    "TENCHEDOSUDUNG": null,
    "TINHTRANGVATLY": null,
    "TENTINHTRANGVATLY": null,
    "HINHTHUCID": null,
    "HINHTHUC": null,
    "DOMAT": 1,
    "TENDOMAT": "Không mật",
    "MUCDOTINCAYID": "1",
    "MUCDOTINCAY": "Bản trích sao",
    "SOTRANG": null,
    "DONVITINH": 0,
    "KHO": "282FA284-87B5-4D7B-A8E9-9D2284D08F0C",
    "KHOGIAY": "a4",
    "KHONGXEPHOP": "1",
    "DASAOCHUP": "1",
    "GIA": null,
    "TANG": null,
    "MAHOSO": null,
    "TUKHOA": null,
    "LOAILUUTRU": 1,
    "NGONNGUID": "d765914a-71fc-464e-8064-0d141266693d",
    "NGONNGU": "Tiếng Việt",
    "NGUOIKYID": null,
    "TOANVAN": "",
    "PC_GHICHU": null,
    "TINHTRANGKHAITHAC": 10,
    "TENTINHTRANGKHAITHAC": "Đang lưu kho",
    "HSDALUU": 1,
    "SOQUYEN": 0,
    "SOBANVE": 0
}
```

## Testing the API

1. Open http://127.0.0.1:8000/docs in your browser
2. Click on the POST /extract-text/ endpoint
3. Click "Try it out"
4. Upload a PDF file
5. Click "Execute"

## Dependencies

- FastAPI
- PyPDF2
- uvicorn
- python-multipart 