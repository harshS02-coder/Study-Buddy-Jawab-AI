from processing.loader import load_pdf
from processing.chunker import chunk_text
from processing.embedder import embed
from retrieval.pinecone_client import upsert
from storage.redis_client import redis_client

def ingest_pipeline(file_url, use_case, document_id):
    namespace = f"{use_case}:{document_id}"
    redis_client.set(f"ingest:{document_id}", "PROCESSING")

    text = load_pdf(file_url)
    chunks_with_metadata = chunk_text(text, use_case)
    
    # Extract just the text for embedding
    chunk_texts = [chunk["text"] for chunk in chunks_with_metadata]
    embeddings = embed(chunk_texts)

    vectors = [
        {
            "id": f"{document_id}_{i}",
            "values": emb,
            "metadata": {
                "text": chunk_meta["text"],
                "page": chunk_meta["page"],
                "source": file_url,
                "document_id": document_id
            }
        }
        for i, (chunk_meta, emb) in enumerate(zip(chunks_with_metadata, embeddings))
    ]

    upsert(vectors, namespace, document_id)
    print(f"Ingestion pipeline completed for document ID '{document_id}' in namespace '{namespace}' with {len(vectors)} vectors.")
    redis_client.set(f"ingest:{document_id}", "DONE")
