# PDF-to-Text AI Service

A powerful FastAPI-based service that extracts text and metadata from PDF documents using advanced AI vision models. This service converts PDFs to images and processes them through the Vintern AI model to extract structured information including dates, document numbers, authors, titles, and full text content.

## 🚀 Features

- **PDF to Image Conversion**: Converts PDF pages to high-quality PNG images
- **AI-Powered Text Extraction**: Uses Vintern-1B-v3.5 vision model for intelligent text recognition
- **Structured Data Extraction**: Automatically extracts:
  - Document dates (day, month, year)
  - Document numbers and symbols
  - Author information
  - Document titles
  - Full text content
- **Multi-language Support**: Optimized for Vietnamese documents with accent handling
- **GPU Acceleration**: CUDA support for faster processing
- **Memory Management**: Intelligent memory handling with lightweight mode for low-resource systems
- **Local Model Caching**: Downloads and caches AI models locally for offline use

## 🏗️ Architecture

```
PDF-to-Text/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routers/             # API route definitions
│   │   └── pdf_router.py    # PDF processing endpoints
│   ├── services/            # Core business logic
│   │   ├── pdf_service.py   # PDF to image conversion
│   │   ├── vintern.py       # AI model service
│   │   └── parser.py        # Data parsing utilities
│   ├── config/              # Configuration management
│   │   └── settings.py      # Environment variables and settings
│   ├── template/            # Response templates
│   │   └── result.py        # Standardized response format
│   └── utils/               # Utility functions
│       └── prom.py          # AI prompt templates
├── model-image/             # Local AI model cache
└── requirements.txt         # Python dependencies
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **AI Model**: Vintern-1B-v3.5 (5CD-AI)
- **Deep Learning**: PyTorch with CUDA support
- **Image Processing**: PIL (Pillow), torchvision
- **PDF Processing**: pdf2image
- **Memory Management**: psutil
- **API Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.8+
- CUDA-compatible GPU (optional, for acceleration)
- At least 4GB RAM (8GB+ recommended)
- 6GB+ GPU memory if using CUDA

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PDF-to-text
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   HOST=0.0.0.0
   PORT=8000
   API_PREFIX=/api/v1
   API_TITLE=PDF Storage API
   API_VERSION=1.0.0
   ```

## 🏃‍♂️ Running the Service

### Development Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at:
- **API**: http://localhost:8000/api/v1
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Usage

### Upload and Process PDF

**Endpoint**: `POST /api/v1/upload/`

**Request**: Multipart form data with PDF file

**Response**: Structured JSON with extracted information

```json
{
  "SheetTotal": 3,
  "IssuedYear": 2024,
  "Field1": "Author Name",
  "Field2": "DOC-001",
  "Field3": "SYM-001",
  "Field6": "15/12/2024",
  "Field7": "Document Title",
  "Field8": "Full Title Text",
  "Field13": 15,
  "Field14": 12,
  "Field15": 2024,
  "Field32": "Thường",
  "Field33": "Tiếng Việt",
  "Field34": "Bản chính",
  "ContentLength": 1250,
  "PageCountA4": 3,
  "SearchMeta": "processed search metadata"
}
```

### Example Usage with cURL

```bash
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Example Usage with Python

```python
import requests

url = "http://localhost:8000/api/v1/upload/"
files = {"file": open("document.pdf", "rb")}

response = requests.post(url, files=files)
result = response.json()
print(f"Document Title: {result['Field7']}")
print(f"Author: {result['Field1']}")
print(f"Date: {result['Field6']}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `API_PREFIX` | `/api/v1` | API endpoint prefix |
| `API_TITLE` | `PDF Storage API` | API title for documentation |
| `API_VERSION` | `1.0.0` | API version |

### AI Model Configuration

The service automatically detects system resources and configures the AI model accordingly:

- **Lightweight Mode**: For systems with limited memory (< 6GB GPU / < 8GB RAM)
- **Standard Mode**: For systems with adequate resources
- **Device Selection**: Automatically chooses between CPU and CUDA GPU

## 📊 Performance

- **Processing Speed**: 2-5 seconds per page (GPU), 10-20 seconds per page (CPU)
- **Memory Usage**: 2-6GB GPU memory, 4-8GB RAM
- **Concurrent Requests**: Supports multiple simultaneous PDF uploads
- **Model Loading**: First request loads model (~30 seconds), subsequent requests are instant

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - The service automatically falls back to CPU mode
   - Check GPU memory usage with `nvidia-smi`

2. **Model Download Issues**
   - Ensure stable internet connection for first run
   - Check available disk space (models require ~2GB)

3. **Performance Issues**
   - Verify CUDA installation and drivers
   - Check system resource availability

### Debug Endpoints

- **GPU Status**: Check GPU usage and model placement
- **System Resources**: Monitor memory and performance
- **Model Verification**: Verify AI model loading status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **5CD-AI** for the Vintern-1B-v3.5 vision model
- **FastAPI** team for the excellent web framework
- **PyTorch** community for deep learning tools

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the troubleshooting section above

---

**Note**: This service is optimized for Vietnamese documents but works with documents in other languages as well. The AI model automatically adapts to different document types and languages. 