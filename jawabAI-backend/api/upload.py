import uuid
from fastapi import UploadFile, BackgroundTasks
from storage.cloudinary_client import upload_file
from ingestion.pipeline import ingest_pipeline
from utils.cache_helper import cache_helper
from storage.redis_client import redis_client

def upload_document(
    file: UploadFile,
    use_case: str,
    background_tasks: BackgroundTasks
):
    print("Received a file upload request.")
    
    # Step 1: Read file content to generate hash
    file_content = file.file.read()
    file.file.seek(0)  # Reset file pointer for later use
    
    # Step 2: Generate hash of PDF content
    file_hash = cache_helper.get_file_hash(file_content)
    print(f"📝 File hash: {file_hash[:16]}...")
    
    # Step 3: Check if this PDF was already processed for this use_case
    cached_document_id = cache_helper.get_cached_document_id(file_hash, use_case)
    
    if cached_document_id:
        # PDF already processed for this use_case - return existing document_id
        print(f"✨ Using cached document for {use_case}: {cached_document_id}")
        return {
            "document_id": cached_document_id,
            "message": f"Document already processed for {use_case} (from cache)",
            "status": "DONE",
            "cached": True
        }
    
    # Step 4: New PDF - process it
    document_id = str(uuid.uuid4())
    print(f"🆕 New document - processing: {document_id}")
    
    # Step 5: Upload to Cloudinary
    url = upload_file(file.file, f"{use_case}/uploads")
    
    # Step 6: Cache the PDF hash -> document_id mapping with use_case
    cache_helper.cache_pdf_mapping(file_hash, document_id, use_case)
    
    # Step 7: Start background ingestion pipeline
    background_tasks.add_task(
        ingest_pipeline,
        url,
        use_case,
        document_id
    )

    return {
        "document_id": document_id,
        "message": "Upload successful",
        "status": "PROCESSING",
        "cached": False
    }
