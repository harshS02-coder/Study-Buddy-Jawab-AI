from file_processor import (load_and_extract_text, chunk_text, create_embedding, store_in_pinecone)
import time
from io import BytesIO

def ingest_pipeline(file_url, use_case: str):
    print(f"Starting the pipeline...")
    t_total_start = time.perf_counter()

    t0 = time.perf_counter()
    text = load_and_extract_text(file_url) 
    t1 = time.perf_counter()
    extract_ms = round((t1 - t0) * 1000)

    if not text:
        raise ValueError("Failed to extract, need text file..")

    t0 = time.perf_counter()
    chunks = chunk_text(text, use_case=use_case)
    t1 = time.perf_counter()
    chunk_ms = round((t1 - t0) * 1000)
    if not chunks:
        raise ValueError("Failed to chunk the text.")

    t0 = time.perf_counter()
    embeddings = create_embedding(chunks, use_case=use_case)
    t1 = time.perf_counter()
    embed_ms = round((t1 - t0) * 1000)
    if embeddings is None:
        raise ValueError("Failed to create embeddings.")
    
    t0 = time.perf_counter()
    store_in_pinecone(chunks, embeddings, use_case=use_case)
    t1 = time.perf_counter()
    upsert_ms = round((t1 - t0) * 1000)

    total_ms = round((time.perf_counter() - t_total_start) * 1000)

    print(
        f"Ingestion timings → extract: {extract_ms} ms | chunk: {chunk_ms} ms | embed: {embed_ms} ms | upsert: {upsert_ms} ms | total: {total_ms} ms"
    )
    print("Ingestion complete")
    
    return {
        "latency": {
            "extract_ms": extract_ms,
            "chunk_ms": chunk_ms,
            "embed_ms": embed_ms,
            "upsert_ms": upsert_ms,
            "total_ms": total_ms
        }
    }