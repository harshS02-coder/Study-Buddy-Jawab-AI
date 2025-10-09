from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

pdf_path = "sample.pdf"  

try:
    print(f"Loading PDF document from {pdf_path}...")
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    print(f"successfully loaded {len(documents)} document(s).")

    print("Spilitting documents ...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    chunks = text_splitter.split_documents(documents)
    print(f"Successfully split into {len(chunks)} chunks.")

    #see how chunks looks like

    print("first chunk..")
    print(chunks[0].page_content) #page_content holds the chunk text

    print(f"\nMetadata of first chunk..{chunks[0].metadata}")

except FileNotFoundError:
    print(f"Error: The file {pdf_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

import os 
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# storing data in vector db

embeddings = GoogleGenerativeAIEmbeddings(model = "models/text-embedding-004")

vector_store = Chroma.from_documents(
    documents = chunks,
    embedding = embeddings,
    persist_directory = "chroma_db",
)

print("Vector store created successfully in the 'chroma_db' directory.")

#test the vector store
query = "what is the main topic of the document?"
print(f"Query: {query}")

results = vector_store.similarity_search(query, k=2)

if results:
    print("\n2 most similar chunks:")
    for i, doc in enumerate(results, start=1):
        print(f"\nChunk {i}:")
        print(doc.page_content)
else:
    print("No similar chunks found.")