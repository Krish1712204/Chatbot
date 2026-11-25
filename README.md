# KS Chatbot

A Claude-like chat app: users sign up, log in, and chat with an AI.

## Folder structure

```
Chatbot/
├── backend/        Python FastAPI server (API, database, auth, AI calls)
│   └── app/        The backend's Python code lives here
├── frontend/       Next.js + TypeScript + Tailwind website (what users see)
├── .gitignore      Files Git should never save (secrets, installs, databases)
├── claude.md       Project notes and rules
└── README.md       This file
```

## Stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Auth:** JWT (pyjwt) + bcrypt password hashing
- **AI:** `backend/app/llm.py` with providers `mock`, `openai` (any OpenAI-compatible API) and `anthropic`, chosen by `LLM_PROVIDER` in `backend/.env`

## Running the app

Backend (port 8000):

```
cd backend
.venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

Frontend (opens http://localhost:3000):

```
cd frontend
npm run dev
```

> Setup steps (creating the virtual environment, installing packages, `.env` files) will be added as each part is built.

## Secrets

Real secrets go in `.env` files, which Git ignores. Each part will have a `.env.example` showing which settings are needed, without real values.
