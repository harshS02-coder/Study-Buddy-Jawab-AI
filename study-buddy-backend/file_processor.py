# import fitz
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# # from langchain_google_genai import GoogleGenerativeAIEmbeddings
# # from langchain_community.vectorstores import Chroma
# from sentence_transformers import SentenceTransformer

# from pinecone import Pinecone
# import os
# from dotenv import load_dotenv
# from tqdm.auto import tqdm # for a nice progress bar
# import google.generativeai as genai
# from langchain.prompts import ChatPromptTemplate

# load_dotenv()

# def load_and_extract_text(file_path: str) -> str | None:
#     try:
#         print(f"Loading data from {file_path}..")
#         text= ""
#         with fitz.open(file_path) as doc:
#             for page in doc:
#                 text += page.get_text()
#             print("Data extracted successfully")
#             return text
#     except FileNotFoundError:
#         print(f"Error: The file {file_path} was not found.")
#         return None

# # if __name__ == "__main__":
# #     file_path = "C:\\Users\\Harsh Kumar\\Desktop\\GenAi Projects\\Personalised_study_buddy\\Upload_path\\sample.pdf"
# #     extracted_text = load_and_extract_text(file_path)
# #     if extracted_text:
# #         print("Extracted Text:")
# #         print("Total characters extracted :", len(extracted_text))
# #         print("First 500 characters:", extracted_text[:500])

# # chunking the text
# def chunk_text(text : str) -> list[str]:
#     print("chunking text..")
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size = 1000,
#         chunk_overlap = 200,
#         length_function = len
#     )  

#     chunks = text_splitter.split_text(text)
#     print(f"Text chunked into {len(chunks)} chunks")
#     return chunks


# # creating embeddings
# def create_embedding(chunks: list[str])->str |None :  # using my local machine to create the embedding
#     print("Loading Model..")
#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     print("creating embedding..")
#     embeddings = model.encode(chunks, show_progress_bar=True)

#     print("Embedding created successfully..")
#     return embeddings

# # stoe in pinecone or chroma db
# def store_in_pinecone(chunks:list[str], embeddings):

#     print("Storing chunks and embedding in pinecone db..")
#     api_key = os.getenv("PINECONE_API_KEY")
#     environment = os.getenv("PINECONE_ENVIRONMENT")
#     # api_key = "pcsk_3fQ1q8_LXqM6XWuAy3iQFwjHTM7yps2EjHFgKb7iMAqCsum4JY8Mke4vSq6Saxg5KsVi8a"
#     # environment = "us-east-1-aws"
#     if not api_key or not environment:
#         print("please set the pinecone api and environment")
#         return

#     print("Connecting to pinecone...")
#     pc = Pinecone(api_key=api_key, environment=environment)

#     index_name = "study-buddy"

#     print(f"Connecting to index: {index_name}")
#     index = pc.Index(index_name)

#     print("Prepairing data for pinecone upsert... ")
#     vectors_to_upsert = []

#     for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
#         vector_id = f"chunk_{i}"
#         metadata = {"text": chunk}
#         # Pinecone expects the embedding to be a list of floats
#         vectors_to_upsert.append((vector_id, embedding.tolist(), metadata))

#     print("Upserting data to Pinecone in batches...")
#     # Upsert data in batches to avoid overwhelming the connection
#     batch_size = 100
#     for i in tqdm(range(0, len(vectors_to_upsert), batch_size)):
#         batch = vectors_to_upsert[i : i + batch_size]
#         index.upsert(vectors=batch)

#     print("Successfully stored data in Pinecone.")

# #retrieval process
# def retrieve_from_pinecone(query: str, top_k: int = 5) -> list[str]:
#     print(f"Retrieving results fro query: {query}")
#     print("Loading embedding model...")

#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     api_key = os.getenv("PINECONE_API_KEY")
#     environment = os.getenv("PINECONE_ENVIRONMENT")

#     if not api_key or not environment:
#         print("Pinecone credentials not set.")
#         return []
    
#     pc = Pinecone(api_key=api_key, environment=environment)
#     index_name = "study-buddy"
#     index = pc.Index(index_name)

#     print("Creating query embedding..")
#     query_embedding = model.encode(query).tolist()

#     print("Querying Pinecone index..")

#     results = index.query(
#         vector=query_embedding,
#         top_k=top_k,
#         include_metadata=True
#     )
#     # 4. Extract the text from the results
#     relevant_chunks = [match['metadata']['text'] for match in results['matches']]
    
#     print("Retrieval complete.")
#     return relevant_chunks

# #generation
# def generate_answer(query:str, context_chunks:list[str], chat_history)->str:

#     print("generating final answer..")
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         return "Error: GOOGLE_API_KEY environment variable not set."

#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel('gemini-2.5-flash')

#     context = "\n".join(context_chunks)

#     #for chat history
#     history_text = ""
#     for msg in chat_history:
#         role = 'User' if msg['sender'] == 'user' else 'Assistant'
#         history_text += f"{role}: {msg['text']}\n"

#     prompt = f"""
#     You are a helpful study assistant. Use only the following context to answer the user's question.
#     The context is the most relevant information found in the document.
#     The conversation history provides context for follow-up questions.
#     If the answer is not found in the context, say "I couldn't find an answer in the provided document."

#     Conversation History:
#     {history_text}
    
#     Context:
#     {context}

#     Question:
#     {query}
#     """

#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"An error occured..{e}"


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
def create_embedding(chunks: list[str], use_case:str = "study"):
    print("Creating embeddings with cache...")
    embeddings = []

    for chunk in tqdm(chunks):
        key = f"{use_case}:embed:{text_hash(chunk)}"
        cached = redis_client.get(key)

        if cached:
            embeddings.append(json.loads(cached))
        else:
            emb = embedding_model.encode(chunk).tolist()
            redis_client.set(key, json.dumps(emb))
            embeddings.append(emb)

    print("Embeddings ready.")
    return embeddings

# -------------------------------
# Store in Pinecone
# -------------------------------
def store_in_pinecone(chunks: list[str], embeddings, use_case:str = "study"):
    print("Storing vectors in Pinecone...")

    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")

    if not api_key or not environment:
        print("Pinecone credentials missing.")
        return

    pc = Pinecone(api_key=api_key, environment=environment)
    index = pc.Index("study-buddy")

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

    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")

    if not api_key or not environment:
        print("Pinecone credentials missing.")
        return []

    pc = Pinecone(api_key=api_key, environment=environment)
    index = pc.Index("study-buddy")

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
        print("⚡ Answer cache HIT")
        return cached.decode("utf-8")  # Redis returns bytes

    print("🐢 Answer cache MISS → calling Gemini")

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
        
        # Print the results
        # print("\n--- Top 5 Relevant Chunks ---")
        # if not retrieved_chunks:
        #     print("No relevant chunks found.")
        # else:
        #     for i, chunk in enumerate(retrieved_chunks):
        #         print(f"Chunk {i+1}:\n{chunk}\n---")
        # print("\n" + "="*50 + "\n") # Separator for clarity

        print(f"Final Answer:", final_answer)
        print("\n"+ "="*50 + "\n")



