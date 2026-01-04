
import uuid
import os
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, HTTPException  
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse  

from ingestion.pipeline import ingest_pipeline
from ingestion.executor import executor
from file_processor import retrieve_from_pinecone, generate_answer
from config.cloudinary import cloudinary  

load_dotenv()

app = FastAPI()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("FastAPI app initialized.")  

# FILE UPLOAD API 

@app.post("/upload", status_code=202)  
async def upload_and_process(
    file: UploadFile = File(...),     
    use_case: str = Form("study")       
):
    print("Received a file upload request.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")  

    try:
        filename = f"{uuid.uuid4()}_{file.filename}"

        #upload to cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="raw",
            public_id=filename,
            folder=f"{use_case}/uploads"
            # async=True,
            # quality="auto"
        )

        file_url = upload_result.get("secure_url")
        print(f"File uploaded to Cloudinary: {file_url}")   


        # ASYNC ingestion (unchanged logic)
        executor.submit(ingest_pipeline, file_url, use_case)

        return {
            "message": "File uploaded. Processing started."
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


print("Upload endpoint is ready.")

# CHAT API

@app.post("/chat") 
async def chat(payload: dict): 
    print("Received a chat Request")

    use_case = payload.get("use_case", "study")
    user_question = payload.get("question")
    chat_history = payload.get("history", [])

    if not user_question:
        raise HTTPException(status_code=400, detail="No question provided.")  

    try:
        retrieved_chunks = retrieve_from_pinecone(
            user_question, use_case=use_case
        )

        final_answer = generate_answer(
            user_question,
            retrieved_chunks,
            chat_history,
            use_case=use_case
        )

        return {
            "answer": final_answer,
            "sources": retrieved_chunks
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))  


print("Chat endpoint is ready")


if __name__ == "__main__":
    print("Starting the Flask app")
    app.run(host = '0.0.0.0', port = 5300, debug = False)

