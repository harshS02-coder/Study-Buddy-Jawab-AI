from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.upload import upload_document
from api.chat import chat
from storage.redis_client import redis_client

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clear cache on server startup
@app.on_event("startup")
async def startup_event():
    try:
        redis_client.flushdb()
        print("✅ Cache cleared on server startup")
        print("🚀 FastAPI app initialized with fresh cache")
    except Exception as e:
        print(f"⚠️ Failed to clear cache: {e}")
        print("FastAPI app initialized.") 

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    use_case: str = Form("study"),
    background_tasks: BackgroundTasks = None
):
    return upload_document(file, use_case, background_tasks)

@app.post("/chat")
async def chat_api(payload: dict):
    return chat(payload)
