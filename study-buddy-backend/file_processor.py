
# added caching 
import fitz
import os
import json
import hashlib
from dotenv import load_dotenv
from tqdm.auto import tqdm

from redis import Redis
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from pinecone import Pinecone

load_dotenv()


api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENVIRONMENT")
if not api_key or not environment:
    print("Pinecone credentials missing.")
    # return []

pc = Pinecone(api_key=api_key, environment=environment)
index = pc.Index("study-buddy")

# -------------------------------
# Redis Client (Global)
# -------------------------------
redis_client = Redis.from_url(
    os.getenv("UPSTASH_REDIS_REST_URL"),
    password=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
    decode_responses=True,
    # ssl=True
)

redis_client.set("test", "hello")
print(redis_client.get("test"))


# -------------------------------
# Load models ONCE (Huge speed boost)
# -------------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# Utility hash helpers
# -------------------------------
def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def answer_hash(question: str, context: list[str]) -> str:
    combined = question + "".join(context)
    return hashlib.sha256(combined.encode()).hexdigest()

def normalize_query(q: str) -> str:
    return q.lower().strip()

# -------------------------------
# PDF Loading
# -------------------------------
def load_and_extract_text(file_path: str) -> str | None:
    try:
        print(f"Loading data from {file_path}...")
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        print("Text extracted successfully.")
        return text
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# -------------------------------
# Chunking
# -------------------------------

#invoice chunking logic
def invoice_chunker(text: str) -> list[str]:
    sections = []
    keywords = [
        "invoice",
        "bill to",
        "vendor",
        "total",
        "tax",
        "gst",
        "amount",
        "payment"
    ]

    lines = text.split("\n")
    buffer = ""

    for line in lines:
        buffer += line + " "
        if any(k in line.lower() for k in keywords):
            sections.append(buffer.strip())
            buffer = ""

    if buffer.strip():
        sections.append(buffer.strip())

    return sections


def chunk_text(text: str, use_case:str = "study") -> list[str]:
    print(f"Chunking text... {use_case}")

    if(use_case == "invoice"):
        return invoice_chunker(text)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = splitter.split_text(text)
    print(f"Created {len(chunks)} chunks.")
    return chunks

# -------------------------------
# Embedding Creation (CACHED)
# -------------------------------
# def create_embedding(chunks: list[str], use_case:str = "study"):
#     print("Creating embeddings with cache...")
#     embeddings = []

#     for chunk in tqdm(chunks):
#         key = f"{use_case}:embed:{text_hash(chunk)}"
#         cached = redis_client.get(key)

#         if cached:
#             embeddings.append(json.loads(cached))
#         else:
#             emb = embedding_model.encode(chunk).tolist()
#             redis_client.set(key, json.dumps(emb))
#             embeddings.append(emb)

#     print("Embeddings ready.")
#     return embeddings

## reducing latency for embedding
def create_embedding(chunks: list[str], use_case: str = "study"):
    print("Creating embeddings with batch + cache...")

    embeddings = [None] * len(chunks)
    to_compute = []
    indices = []

    for i, chunk in enumerate(chunks):
        key = f"{use_case}:embed:{text_hash(chunk)}"
        cached = redis_client.get(key)
        if cached:
            embeddings[i] = json.loads(cached)
        else:
            to_compute.append(chunk)
            indices.append(i)

    if to_compute:
        new_embeddings = embedding_model.encode(
            to_compute,
            batch_size=32,  
            show_progress_bar=True
        )

        for idx, emb in zip(indices, new_embeddings):
            emb = emb.tolist()
            embeddings[idx] = emb
            redis_client.set(
                f"{use_case}:embed:{text_hash(chunks[idx])}",
                json.dumps(emb)
            )

    return embeddings



# -------------------------------
# Store in Pinecone
# -------------------------------
def store_in_pinecone(chunks: list[str], embeddings, use_case:str = "study"):
    print("Storing vectors in Pinecone...")

    vectors = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        vectors.append((
            f"chunk_{i}",
            emb,
            {"text": chunk}
        ))

    batch_size = 100
    for i in tqdm(range(0, len(vectors), batch_size)):
        index.upsert(vectors=vectors[i:i + batch_size], namespace=use_case)

    print("Pinecone upsert complete.")

# -------------------------------
# Retrieval (CACHED)
# -------------------------------
def retrieve_from_pinecone(query: str, top_k: int = 5, use_case:str = "study") -> list[str]:
    cache_key = f"{use_case}:retrieval:{normalize_query(query)}"
    cached = redis_client.get(cache_key)

    if cached:
        print("Retrieval cache HIT")
        return json.loads(cached)

    print("Retrieval cache MISS → querying Pinecone")

    # pc = Pinecone(api_key=api_key, environment=environment)   ------this  has beed moved to global scope
    # index = pc.Index("study-buddy")

    query_embedding = embedding_model.encode(query).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=use_case
    )

    chunks = [m["metadata"]["text"] for m in results["matches"]]

    redis_client.setex(
        cache_key,
        900,  # 15 minutes
        json.dumps(chunks)
    )

    return chunks

# -------------------------------
# Answer Generation (CACHED)
# -------------------------------
# def generate_answer(query: str, context_chunks: list[str], chat_history, use_case:str = "study") -> str:
#     cache_key = f"{use_case}:answer:{answer_hash(query, context_chunks)}"
#     cached = redis_client.get(cache_key)

#     if cached:
#         print("Answer cache HIT")
#         return cached

#     print("Answer cache MISS → calling Gemini")

#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         return "GOOGLE_API_KEY not set."

#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel("gemini-2.5-flash")

#     context = "\n".join(context_chunks)

#     history_text = ""
#     for msg in chat_history:
#         role = "User" if msg["sender"] == "user" else "Assistant"
#         history_text += f"{role}: {msg['text']}\n"

#     prompt = f"""
# You are a helpful study assistant.
# Answer strictly using the provided context.

# Conversation History:
# {history_text}

# Context:
# {context}

# Question:
# {query}
# """

#     try:
#         response = model.generate_content(prompt)
#         redis_client.setex(cache_key, 1800, response.text)  # 30 min
#         return response.text
#     except Exception as e:
#         return f"Generation error: {e}"

#multipurpose code with use_case:

def generate_answer(
    query: str,
    context_chunks: list[str],
    chat_history,
    use_case: str = "study"
) -> str:
    cache_key = f"{use_case}:answer:{answer_hash(query, context_chunks)}"
    cached = redis_client.get(cache_key)

    if cached:
        print("Answer cache HIT")
        return cached.decode("utf-8")  # Redis returns bytes

    print("Answer cache MISS → calling Gemini")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "GOOGLE_API_KEY not set."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    context = "\n".join(context_chunks)

    # Build conversation history
    history_text = ""
    for msg in chat_history:
        role = "User" if msg["sender"] == "user" else "Assistant"
        history_text += f"{role}: {msg['text']}\n"

    # 🔁 Use-case–specific system prompt
    
    if use_case == "invoice":
        print("Using invoice system prompt.")
        system_prompt = """
You are an AI invoice analyst.
Answer ONLY using the provided invoice context.
Extract exact values (amounts, dates, invoice numbers).
If the answer is not present, reply:
"Not found in the provided invoice."
Do NOT make assumptions.
"""
    else:  # study (default)
        print("Using study system prompt.")
        system_prompt = """
You are a helpful study assistant.
Explain concepts clearly and concisely
using ONLY the provided context.
If the answer is not found, say so explicitly.
"""

    prompt = f"""
{system_prompt}

Conversation History:
{history_text}

Context:
{context}

Question:
{query}
"""

    try:
        response = model.generate_content(prompt)
        answer_text = response.text.strip()

        # Cache for 30 minutes
        redis_client.setex(cache_key, 1800, answer_text)

        return answer_text

    except Exception as e:
        return f"Generation error: {e}"




if __name__ == "__main__":

    # file_path = "C:\\Users\\Harsh Kumar\\Desktop\\GenAi Projects\\Personalised_study_buddy\\Upload_path\\sample.pdf"
    # extracted_text = load_and_extract_text(file_path)

    # if extracted_text:
    #     text_chunks = chunk_text(extracted_text)
    #     print("Total Number of chunks created:",len(text_chunks))


    #     if text_chunks:
    #         print("first chunk :", text_chunks[0])
    #         embeddings = create_embedding(text_chunks)

    #         print("Embedding....")

    #         print(f"Shape of the embeddings array:", {embeddings.shape})

    #         # print("First embedding vector...")
    #         # print(embeddings[0])
    #         if embeddings is not None:
    #             store_in_pinecone(text_chunks, embeddings)

    # data stored in pinecone so no need of above codes

    while True:
        
        user_question = input("Ask a question about your document (or type 'exit' to quit): ")
        if user_question.lower() == 'exit':
            break
        
        retrieved_chunks = retrieve_from_pinecone(user_question)

        final_answer = generate_answer(user_question, retrieved_chunks)
        
        print(f"Final Answer:", final_answer)
        print("\n"+ "="*50 + "\n")



