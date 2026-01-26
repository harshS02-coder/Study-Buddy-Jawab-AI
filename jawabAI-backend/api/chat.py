from processing.embedder import embed
from retrieval.pinecone_client import query
from llm.generator import generate_answer
from storage.redis_client import redis_client
from utils.cache_helper import cache_helper

def chat(payload):
    document_id = payload["document_id"]
    use_case = payload.get("use_case", "study")
    question = payload["question"]

    # Step 1: Check document status
    status = redis_client.get(f"ingest:{document_id}")
    if status != "DONE":
        return {"error": "Document not ready"}
    
    # Step 2: Check if this query was already answered (cache)
    cached_response = cache_helper.get_cached_query_response(document_id, question)
    if cached_response:
        print(f"✨ Returning cached answer for: {question[:50]}...")
        cached_response["cached"] = True
        return cached_response

    namespace = f"{use_case}:{document_id}"
    query_vec = embed([question])[0]

    results = query(query_vec, namespace, document_id=document_id)
    
    contexts = []
    sources = []

    # Handle Pinecone QueryResponse - results.matches is a list of Match objects
    matches = results.matches if hasattr(results, 'matches') else results.get("matches", [])
    
    for match in matches:
        # Handle both object attributes and dict access
        if hasattr(match, 'metadata'):
            metadata = match.metadata or {}
        else:
            metadata = match.get("metadata", {}) or {}

        text = metadata.get("text", "") if isinstance(metadata, dict) else getattr(metadata, "text", "")
        page = metadata.get("page", "N/A") if isinstance(metadata, dict) else getattr(metadata, "page", "N/A")
        source = metadata.get("source", "document") if isinstance(metadata, dict) else getattr(metadata, "source", "document")
        score = match.score if hasattr(match, 'score') else match.get("score", 0)

        contexts.append(f"[Page {page}] {text}")

        sources.append({
            "page": page,
            "source": source,
            "score": score
        })

    context = "\n\n".join(contexts)

    # Step 3: Generate answer (cache miss - need to process)
    print(f"🔍 Processing new query: {question[:50]}...")
    answer = generate_answer(
        question=question,
        context=context,
        sources=sources,
        use_case=use_case
    )

    # Step 4: Prepare response
    response = {
        "answer": answer,
        "sources": sources,
        "cached": False
    }
    
    # Step 5: Cache the response for future queries
    cache_helper.cache_query_response(document_id, question, response)

    return response
