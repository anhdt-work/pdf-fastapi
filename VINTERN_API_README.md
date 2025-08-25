# Vintern Vision-Language Model API

This document describes the integration of the Vintern-1B-v3_5 vision-language model into the FastAPI application, providing endpoints for document analysis and text extraction from images.

## Overview

The Vintern API provides several endpoints for analyzing images using a state-of-the-art Vietnamese vision-language model. The model is particularly optimized for document analysis tasks such as:

- Date extraction from documents
- Document number/ID extraction
- Full text extraction (OCR with context understanding)
- Custom vision-language chat interactions

## Model Information

- **Model**: 5CD-AI/Vintern-1B-v3_5
- **Type**: Vision-Language Model
- **Language**: Optimized for Vietnamese text
- **Hardware Requirements**: CUDA-compatible GPU recommended
- **Memory Requirements**: ~4GB VRAM minimum

## API Endpoints

All endpoints are available under the `/api/v1/vintern` prefix.

### 1. Health Check
**GET** `/api/v1/vintern/health`

Check the API health status and model loading state.

**Response:**
```json
{
  "status": "healthy",
  "model_status": "loaded" | "not_loaded"
}
```

### 2. Root Information
**GET** `/api/v1/vintern/`

Get basic API information.

**Response:**
```json
{
  "message": "Vision Language Model API",
  "status": "running",
  "model_loaded": true
}
```

### 3. Model Startup
**GET** `/api/v1/vintern/startup`

Manually trigger model loading (useful for warming up the model).

**Response:**
```json
{
  "message": "Model loaded successfully",
  "status": "ready"
}
```

### 4. Date and Document Number Extraction
**GET** `/api/v1/vintern/date`

Extract document date and number from an image.

**Parameters:**
- `image_url` (string, required): Path to the image file

**Response:**
```json
{
  "date": "DD-MM-YYYY",
  "document_number": "NUMBER-SYMBOL",
  "success": true,
  "message": ""
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/vintern/date?image_url=/path/to/document.png"
```

### 5. Full Text Extraction
**POST** `/api/v1/vintern/text`

Extract complete text content from an image while preserving structure.

**Parameters:**
- `image_url` (string, required): Path to the image file

**Response:**
```json
{
  "text": "Extracted text content...",
  "success": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/vintern/text?image_url=/path/to/document.png"
```

### 6. Custom Chat
**POST** `/api/v1/vintern/chat`

Send a custom prompt along with an image for flexible vision-language interactions.

**Parameters:**
- `image_url` (string, required): Path to the image file
- `prompt` (string, required): Custom prompt for the model

**Response:**
```json
{
  "response": "Model response to your prompt...",
  "success": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/vintern/chat?image_url=/path/to/image.png&prompt=Describe%20what%20you%20see"
```

## Setup and Installation

### 1. Dependencies

The following packages are required (already included in `requirements.txt`):

```txt
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
pillow>=10.0.0
numpy>=1.24.0
fastapi>=0.100.0
```

### 2. Hardware Requirements

- **GPU**: CUDA-compatible GPU with at least 4GB VRAM (recommended: 8GB+)
- **RAM**: At least 8GB system RAM
- **Storage**: ~3GB for model weights (downloaded automatically)

### 3. Model Loading

The model is loaded automatically on the first API request. Initial loading may take 2-5 minutes depending on your hardware and internet connection.

You can pre-load the model using:
```bash
curl "http://localhost:8000/api/v1/vintern/startup"
```

## Usage Examples

### Python Client Example

```python
import requests

# API base URL
API_URL = "http://localhost:8000/api/v1/vintern"

# Check if model is ready
health = requests.get(f"{API_URL}/health").json()
print(f"Model status: {health['model_status']}")

# Extract date and document number
image_path = "/path/to/your/document.png"
response = requests.get(f"{API_URL}/date", params={"image_url": image_path})
result = response.json()
print(f"Date: {result['date']}")
print(f"Document Number: {result['document_number']}")

# Extract full text
response = requests.post(f"{API_URL}/text", params={"image_url": image_path})
result = response.json()
print(f"Extracted text: {result['text']}")

# Custom chat
prompt = "What type of document is this?"
response = requests.post(f"{API_URL}/chat", params={
    "image_url": image_path,
    "prompt": prompt
})
result = response.json()
print(f"Response: {result['response']}")
```

### Using the Test Script

A comprehensive test script is provided:

```bash
# Basic usage
python example_vintern_usage.py --image_path /path/to/document.png

# With custom prompt
python example_vintern_usage.py \
    --image_path /path/to/document.png \
    --custom_prompt "Analyze this document and summarize its contents"

# Different API endpoint
python example_vintern_usage.py \
    --image_path /path/to/document.png \
    --api_url "http://your-server:8000/api/v1/vintern"
```

## Error Handling

The API provides detailed error messages for common issues:

### Common Error Codes

- **400 Bad Request**: Missing required parameters (image_url, prompt)
- **503 Service Unavailable**: Model not loaded or initialization failed
- **500 Internal Server Error**: Model inference error or file access issues

### Example Error Response

```json
{
  "detail": "Model not loaded: CUDA out of memory",
  "status_code": 503
}
```

## Performance Notes

### First Request
- The first request will be slower (2-5 minutes) due to model loading
- Subsequent requests are much faster (1-10 seconds depending on image complexity)

### Optimization Tips
1. **Pre-warm the model** using the `/startup` endpoint
2. **Use appropriate image sizes** (the model will resize automatically, but smaller images process faster)
3. **Batch multiple requests** for better throughput
4. **Monitor GPU memory** usage to avoid OOM errors

## Integration with Existing PDF Workflow

The Vintern API integrates seamlessly with the existing PDF processing pipeline:

```python
from app.services.pdf_service import pdf_service
from app.services.vintern import vintern_service

# Convert PDF to PNG
pdf_content = open("document.pdf", "rb").read()
png_images = await pdf_service.convert_to_png(pdf_content)

# Process each page with Vintern
for i, image_bytes in enumerate(png_images):
    # Save temporary image
    temp_path = f"temp_page_{i}.png"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)
    
    # Extract information
    result = await vintern_service.extract_date_and_name_and_document_number(temp_path)
    text = await vintern_service.extract_full_text(temp_path)
    
    print(f"Page {i+1}: Date={result['date']}, Text preview={text[:100]}...")
```

## Troubleshooting

### Model Loading Issues
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check GPU memory
nvidia-smi
```

### Memory Issues
- Reduce batch size or image resolution
- Ensure sufficient GPU memory is available
- Monitor system RAM usage

### Connection Issues
- Verify the FastAPI server is running
- Check firewall settings
- Ensure correct API endpoint URLs

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The Vintern endpoints will appear under the "Vision Language Model" tag in the interactive documentation. 