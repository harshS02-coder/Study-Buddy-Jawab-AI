import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

load_dotenv()

print("initializing llm and embeddings...")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

print("initialized llm and embeddings...")

# load the vector store
vector_store = Chroma(
    persist_directory = "chroma_db",
    embedding_function = embeddings
)

#create a retriever
print("creating retriever...")
retriever = vector_store.as_retriever(search_kwargs ={"k":3})

#create a prompt template

template = """
You are a helpful study assistant who provides concise answers based on the context provided.
Answer the user's question using only the context below. 
If you cannot find the answer in the context, simply say: "I'm sorry, I cannot find the answer in the document."

Context:
{context}

Question:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)

#Building a RAG chain

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    |prompt
    | llm
    | StrOutputParser()
)

# test the RAG chain
query = "What is the main topic of the document?"
print(f"Query: {query}")

print("generating response...")

response = rag_chain.invoke(query)

print("Response:", response)