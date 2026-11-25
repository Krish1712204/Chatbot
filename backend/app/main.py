"""FastAPI entry point. Run with: uvicorn app.main:app --reload --port 8000"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once when the server starts: create tables if missing
    yield


app = FastAPI(title="KS Chatbot API", lifespan=lifespan)

# CORS: browsers block a website from calling an API on another address
# unless the API allows it. Here we allow only our frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def friendly_validation_error(request: Request, exc: RequestValidationError):
    """Turn FastAPI's detailed input errors into one readable sentence:
    {"detail": "Password must be at least 8 characters"} — the same shape as our other errors."""
    err = exc.errors()[0]
    if err["type"] == "missing":
        message = f"{str(err['loc'][-1]).capitalize()} is required"
    else:
        message = err["msg"].removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"detail": message})


app.include_router(auth.router)


@app.get("/api/health")
def health():
    """Quick check that the server is running, and which AI provider is active."""
    return {"status": "ok", "provider": settings.LLM_PROVIDER}
