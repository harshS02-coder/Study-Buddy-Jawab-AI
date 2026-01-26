from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.upload import upload_document
from api.chat import chat
from storage.redis_client import redis_client
import os

app = FastAPI(
    title="JawabAI API",
    version="1.0.0",
    description="AI-powered document Q&A system"
)

# Get environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS - allow Railway and Vercel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        FRONTEND_URL,
        "https://*.railway.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        # Only clear cache in development, NOT in production
        if ENVIRONMENT == "development":
            redis_client.flushdb()
            print("✅ Cache cleared (development mode)")
        
        # Test Redis connection
        redis_client.ping()
        print(f"🚀 FastAPI app initialized - Environment: {ENVIRONMENT}")
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️ Redis connection warning: {e}")

@app.get("/")
async def root():
    """Root endpoint - shows API is running"""
    return {
        "message": "JawabAI API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check for Railway monitoring"""
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy" if "connected" in redis_status else "degraded",
        "services": {
            "api": "up",
            "redis": redis_status
        }
    }

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

# Required for Railway to bind correct port
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
