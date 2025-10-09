import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

from pinecone import Pinecone
import os
from dotenv import load_dotenv
from tqdm.auto import tqdm # for a nice progress bar
import google.generativeai as genai
from langchain.prompts import ChatPromptTemplate

load_dotenv()

def load_and_extract_text(file_path: str) -> str | None:
    try:
        print(f"Loading data from {file_path}..")
        text= ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
            print("Data extracted successfully")
            return text
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None

# if __name__ == "__main__":
#     file_path = "C:\\Users\\Harsh Kumar\\Desktop\\GenAi Projects\\Personalised_study_buddy\\Upload_path\\sample.pdf"
#     extracted_text = load_and_extract_text(file_path)
#     if extracted_text:
#         print("Extracted Text:")
#         print("Total characters extracted :", len(extracted_text))
#         print("First 500 characters:", extracted_text[:500])

# chunking the text
def chunk_text(text : str) -> list[str]:
    print("chunking text..")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )  

    chunks = text_splitter.split_text(text)
    print(f"Text chunked into {len(chunks)} chunks")
    return chunks


# creating embeddings
def create_embedding(chunks: list[str])->str |None :  # using my local machine to create the embedding
    print("Loading Model..")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("creating embedding..")
    embeddings = model.encode(chunks, show_progress_bar=True)

    print("Embedding created successfully..")
    return embeddings

# stoe in pinecone or chroma db
def store_in_pinecone(chunks:list[str], embeddings):

    print("Storing chunks and embedding in pinecone db..")
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    # api_key = "pcsk_3fQ1q8_LXqM6XWuAy3iQFwjHTM7yps2EjHFgKb7iMAqCsum4JY8Mke4vSq6Saxg5KsVi8a"
    # environment = "us-east-1-aws"
    if not api_key or not environment:
        print("please set the pinecone api and environment")
        return

    print("Connecting to pinecone...")
    pc = Pinecone(api_key=api_key, environment=environment)

    index_name = "study-buddy"

    print(f"Connecting to index: {index_name}")
    index = pc.Index(index_name)

    print("Prepairing data for pinecone upsert... ")
    vectors_to_upsert = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vector_id = f"chunk_{i}"
        metadata = {"text": chunk}
        # Pinecone expects the embedding to be a list of floats
        vectors_to_upsert.append((vector_id, embedding.tolist(), metadata))

    print("Upserting data to Pinecone in batches...")
    # Upsert data in batches to avoid overwhelming the connection
    batch_size = 100
    for i in tqdm(range(0, len(vectors_to_upsert), batch_size)):
        batch = vectors_to_upsert[i : i + batch_size]
        index.upsert(vectors=batch)

    print("Successfully stored data in Pinecone.")

#retrieval process
def retrieve_from_pinecone(query: str, top_k: int = 5) -> list[str]:
    print(f"Retrieving results fro query: {query}")
    print("Loading embedding model...")

    model = SentenceTransformer('all-MiniLM-L6-v2')
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")

    if not api_key or not environment:
        print("Pinecone credentials not set.")
        return []
    
    pc = Pinecone(api_key=api_key, environment=environment)
    index_name = "study-buddy"
    index = pc.Index(index_name)

    print("Creating query embedding..")
    query_embedding = model.encode(query).tolist()

    print("Querying Pinecone index..")

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    # 4. Extract the text from the results
    relevant_chunks = [match['metadata']['text'] for match in results['matches']]
    
    print("Retrieval complete.")
    return relevant_chunks

#generation
def generate_answer(query:str, context_chunks:list[str], chat_history)->str:

    print("generating final answer..")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable not set."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    context = "\n".join(context_chunks)

    #for chat history
    history_text = ""
    for msg in chat_history:
        role = 'User' if msg['sender'] == 'user' else 'Assistant'
        history_text += f"{role}: {msg['text']}\n"

    prompt = f"""
    You are a helpful study assistant. Use only the following context to answer the user's question.
    The context is the most relevant information found in the document.
    The conversation history provides context for follow-up questions.
    If the answer is not found in the context, say "I couldn't find an answer in the provided document."

    Conversation History:
    {history_text}
    
    Context:
    {context}

    Question:
    {query}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occured..{e}"




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



