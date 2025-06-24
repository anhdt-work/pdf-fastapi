"""
Example usage of the GCS Storage Service with key-based folder structure.

This script demonstrates how to:
1. Generate a folder key
2. Upload files to a specific folder
3. List files in a folder
4. Download files from a folder
5. Delete files and folders
"""

import asyncio
import os
from app.services.storage_service import storage_service

async def example_gcs_operations():
    """Demonstrate GCS operations with key-based folder structure."""
    
    print("=== GCS Storage Service Example ===\n")
    
    # 1. Generate a new folder key
    print("1. Generating a new folder key...")
    folder_key = storage_service.generate_key()
    print(f"Generated folder key: {folder_key}\n")
    
    # 2. Upload a sample file
    print("2. Uploading a sample file...")
    sample_content = b"This is a sample file content for testing GCS upload."
    sample_filename = "sample.txt"
    
    upload_result = await storage_service.upload_file_to_folder(
        content=sample_content,
        filename=sample_filename,
        content_type="text/plain",
        folder_key=folder_key
    )
    
    print(f"Upload successful!")
    print(f"  - GCS URL: {upload_result['gcs_url']}")
    print(f"  - GCS Path: {upload_result['gcs_path']}")
    print(f"  - File Size: {upload_result['file_size']} bytes\n")
    
    # 3. Upload another file to the same folder
    print("3. Uploading another file to the same folder...")
    another_content = b"This is another sample file with different content."
    another_filename = "another_sample.txt"
    
    another_result = await storage_service.upload_file_to_folder(
        content=another_content,
        filename=another_filename,
        content_type="text/plain",
        folder_key=folder_key
    )
    
    print(f"Second upload successful!")
    print(f"  - GCS Path: {another_result['gcs_path']}\n")
    
    # 4. List all files in the folder
    print("4. Listing all files in the folder...")
    files = await storage_service.list_files_in_folder(folder_key=folder_key)
    
    print(f"Found {len(files)} files in folder {folder_key}:")
    for file_info in files:
        print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
    print()
    
    # 5. Download a file
    print("5. Downloading a file...")
    downloaded_content = await storage_service.download_file_from_folder(
        folder_key=folder_key,
        filename=sample_filename
    )
    
    print(f"Download successful!")
    print(f"  - Downloaded content: {downloaded_content.decode('utf-8')}")
    print(f"  - Content length: {len(downloaded_content)} bytes\n")
    
    # 6. Delete a specific file
    print("6. Deleting a specific file...")
    delete_success = await storage_service.delete_file_from_folder(
        folder_key=folder_key,
        filename=another_filename
    )
    
    if delete_success:
        print(f"Successfully deleted {another_filename}")
    else:
        print(f"Failed to delete {another_filename}")
    print()
    
    # 7. List files again to confirm deletion
    print("7. Listing files after deletion...")
    remaining_files = await storage_service.list_files_in_folder(folder_key=folder_key)
    
    print(f"Remaining files in folder {folder_key}:")
    for file_info in remaining_files:
        print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
    print()
    
    # 8. Delete the entire folder
    print("8. Deleting the entire folder...")
    folder_delete_success = await storage_service.delete_folder(folder_key=folder_key)
    
    if folder_delete_success:
        print(f"Successfully deleted folder {folder_key} and all contents")
    else:
        print(f"Failed to delete folder {folder_key}")
    
    print("\n=== Example completed successfully! ===")

async def example_with_existing_key():
    """Example using an existing folder key."""
    
    print("\n=== Example with Existing Key ===\n")
    
    # Use a specific folder key
    existing_key = "test-folder-123"
    
    print(f"Using existing folder key: {existing_key}")
    
    # Upload a file to the existing folder
    content = b"File uploaded to existing folder key."
    filename = "existing_folder_test.txt"
    
    result = await storage_service.upload_file_to_folder(
        content=content,
        filename=filename,
        content_type="text/plain",
        folder_key=existing_key
    )
    
    print(f"Upload successful to existing folder!")
    print(f"  - GCS Path: {result['gcs_path']}")
    print(f"  - Folder Key: {result['folder_key']}")
    
    # Clean up
    await storage_service.delete_folder(folder_key=existing_key)
    print(f"Cleaned up folder {existing_key}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(example_gcs_operations())
    asyncio.run(example_with_existing_key()) 