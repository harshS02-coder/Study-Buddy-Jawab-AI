from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(chunks):
    print(f"Generated embeddings for {len(chunks)} texts.")
    return model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=2
    ).tolist()
    
