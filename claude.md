# Project: KS Chatbot (a Claude-like chat app)

## About me
- I am learning full stack development. Explain what you did in simple English after each task.
- Before big changes, show me a short plan and wait for my OK.

## Stack
- frontend/: Next.js (App Router) + TypeScript + Tailwind CSS
- backend/: Python FastAPI + SQLAlchemy + SQLite
- Auth: JWT (pyjwt) + bcrypt
- AI: one file backend/app/llm.py with providers "mock", "openai" (any OpenAI-compatible API) and "anthropic", chosen by LLM_PROVIDER in backend/.env

## Rules
- Keep secrets in .env files only. Never commit .env. Keep a .env.example.
- Small files, clear names, short comments on tricky parts.
- After each phase: tell me the exact commands to run and how to test it.
- Do not add features I did not ask for.

## Run commands
- Backend: cd backend && .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000
- Frontend: cd frontend && npm run dev  (opens http://localhost:3000)