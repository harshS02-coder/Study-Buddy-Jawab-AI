from pinecone import Pinecone
from config.settings import PINECONE_API_KEY, PINECONE_INDEX

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def upsert(vectors, namespace, document_id):
    index.upsert(vectors=vectors, namespace=namespace)
    print(f"Upserted {len(vectors)} vectors to Pinecone index '{PINECONE_INDEX}' in namespace '{namespace}'")

def query(vector, namespace, top_k=5, document_id=None):
    print(f"Querying Pinecone index '{PINECONE_INDEX}' in namespace '{namespace}' with top_k={top_k}.")
    return index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
