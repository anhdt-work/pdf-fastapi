# Google Cloud Storage Service

This service provides a key-based folder structure for uploading and downloading files to/from Google Cloud Storage (GCS).

## Features

- **Key-based folder structure**: Each upload creates or uses a unique folder key
- **Automatic key generation**: Generate unique UUID-based folder keys
- **File management**: Upload, download, list, and delete files
- **Folder management**: Delete entire folders and their contents
- **RESTful API**: Complete HTTP API for all operations

## Architecture

The service uses a folder-based approach where:
1. A unique key is generated (or provided) for each folder
2. Files are stored in GCS using the pattern: `{folder_key}/{filename}`
3. All operations are scoped to specific folder keys

## API Endpoints

### 1. Generate Folder Key
```http
POST /api/v1/gcs/generate-key
```

**Response:**
```json
{
  "success": true,
  "folder_key": "550e8400-e29b-41d4-a716-446655440000",
  "message": "New folder key generated successfully"
}
```

### 2. Upload File
```http
POST /api/v1/gcs/upload
```

**Parameters:**
- `file`: The file to upload (multipart/form-data)
- `folder_key` (optional): Existing folder key. If not provided, a new one will be generated

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "gcs_url": "https://storage.googleapis.com/bucket-name/folder-key/filename.txt",
    "gcs_path": "folder-key/filename.txt",
    "folder_key": "550e8400-e29b-41d4-a716-446655440000",
    "content_type": "text/plain",
    "file_size": 1234,
    "filename": "filename.txt"
  }
}
```

### 3. Download File
```http
GET /api/v1/gcs/download/{folder_key}/{filename}
```

**Response:** File content as streaming response

### 4. List Files in Folder
```http
GET /api/v1/gcs/list/{folder_key}
```

**Response:**
```json
{
  "success": true,
  "folder_key": "550e8400-e29b-41d4-a716-446655440000",
  "file_count": 2,
  "files": [
    {
      "filename": "file1.txt",
      "gcs_path": "folder-key/file1.txt",
      "gcs_url": "https://storage.googleapis.com/bucket-name/folder-key/file1.txt",
      "size": 1234,
      "content_type": "text/plain",
      "created": "2024-01-01T00:00:00.000000Z",
      "updated": "2024-01-01T00:00:00.000000Z"
    }
  ]
}
```

### 5. Delete File
```http
DELETE /api/v1/gcs/delete/{folder_key}/{filename}
```

**Response:**
```json
{
  "success": true,
  "message": "File filename.txt deleted successfully from folder folder-key"
}
```

### 6. Delete Folder
```http
DELETE /api/v1/gcs/delete-folder/{folder_key}
```

**Response:**
```json
{
  "success": true,
  "message": "Folder folder-key and all contents deleted successfully"
}
```

## Service Methods

### StorageService Class

#### `generate_key() -> str`
Generate a unique UUID-based folder key.

#### `upload_file_to_folder(content, filename, content_type, folder_key=None) -> Dict`
Upload a file to a specific folder. If no folder_key is provided, a new one will be generated.

#### `download_file_from_folder(folder_key, filename) -> bytes`
Download a file from a specific folder.

#### `list_files_in_folder(folder_key) -> List[Dict]`
List all files in a specific folder.

#### `delete_file_from_folder(folder_key, filename) -> bool`
Delete a specific file from a folder.

#### `delete_folder(folder_key) -> bool`
Delete an entire folder and all its contents.

## Usage Examples

### Python Service Usage

```python
from app.services.storage_service import storage_service

# Generate a new folder key
folder_key = storage_service.generate_key()

# Upload a file
result = await storage_service.upload_file_to_folder(
    content=b"file content",
    filename="test.txt",
    content_type="text/plain",
    folder_key=folder_key
)

# Download a file
content = await storage_service.download_file_from_folder(
    folder_key=folder_key,
    filename="test.txt"
)

# List files in folder
files = await storage_service.list_files_in_folder(folder_key=folder_key)

# Delete a file
success = await storage_service.delete_file_from_folder(
    folder_key=folder_key,
    filename="test.txt"
)

# Delete entire folder
success = await storage_service.delete_folder(folder_key=folder_key)
```

### cURL Examples

#### Generate a key
```bash
curl -X POST "http://localhost:8000/api/v1/gcs/generate-key"
```

#### Upload a file
```bash
curl -X POST "http://localhost:8000/api/v1/gcs/upload" \
  -F "file=@/path/to/your/file.txt" \
  -F "folder_key=your-folder-key"
```

#### Download a file
```bash
curl -X GET "http://localhost:8000/api/v1/gcs/download/your-folder-key/filename.txt" \
  -o downloaded_file.txt
```

#### List files
```bash
curl -X GET "http://localhost:8000/api/v1/gcs/list/your-folder-key"
```

#### Delete a file
```bash
curl -X DELETE "http://localhost:8000/api/v1/gcs/delete/your-folder-key/filename.txt"
```

#### Delete a folder
```bash
curl -X DELETE "http://localhost:8000/api/v1/gcs/delete-folder/your-folder-key"
```

## Configuration

Make sure your `.env` file contains the necessary GCS configuration:

```env
BUCKET_NAME=your-gcs-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

## Error Handling

The service includes comprehensive error handling:

- **404 Not Found**: File or folder doesn't exist
- **500 Internal Server Error**: GCS operation failed
- **FileNotFoundError**: Specific file not found in folder
- **PermissionError**: Insufficient permissions for GCS operations

## Security Considerations

1. **Authentication**: Uses Google Cloud service account credentials
2. **Authorization**: Ensure proper IAM roles for GCS bucket access
3. **File validation**: Consider adding file type and size validation
4. **Rate limiting**: Consider implementing rate limiting for API endpoints

## Testing

Run the example script to test the service:

```bash
python example_gcs_usage.py
```

This will demonstrate all the key operations with the GCS service.

## Dependencies

- `google-cloud-storage`: Google Cloud Storage client
- `fastapi`: Web framework for API endpoints
- `python-multipart`: For file upload handling
- `uuid`: For generating unique folder keys 