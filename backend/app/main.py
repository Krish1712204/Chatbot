"""FastAPI entry point. Run with: uvicorn app.main:app --reload --port 8000"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="KS Chatbot API")

# CORS: browsers block a website from calling an API on another address
# unless the API allows it. Here we allow only our frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    """Quick check that the server is running, and which AI provider is active."""
    return {"status": "ok", "provider": settings.LLM_PROVIDER}
