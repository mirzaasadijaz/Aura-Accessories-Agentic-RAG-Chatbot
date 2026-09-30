# Aura Accessories – Agentic RAG Chatbot

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-mirzaasadijaz%2Fenterprise--ai--agent-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/repository/docker/mirzaasadijaz/enterprise-ai-agent/)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C)
https://hub.docker.com/repository/docker/mirzaasadijaz/enterprise-ai-agent/general
An AI shopping assistant for **The Aura Accessories**, a luxury fashion brand (handbags, footwear, watches, jewelry). It is an agentic RAG system: a LangGraph ReAct agent powered by Groq decides whether to answer directly, search your uploaded internal documents (ChromaDB), or search the live web (Tavily). Every visitor gets their own persistent conversation memory.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Loading Your Knowledge Base](#loading-your-knowledge-base)
- [API Reference](#api-reference)
- [Docker](#docker)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Known Limitations](#known-limitations)

## Features

- **Agentic routing:** LangGraph `create_react_agent` chooses between internal-document search and web search.
- **RAG:** upload PDF, DOCX, CSV, TXT, or MD files; they are chunked, embedded locally, and stored in ChromaDB.
- **Multi-user memory:** each browser session gets a unique `session_id`, used as the LangGraph `thread_id`. History is persisted in SQLite.
- **Brand-aware prompt:** polite, luxurious tone; business first; never recommends competitors.
- **Web UI:** a chat page and a separate upload page, both served by FastAPI.
- **Streamlit option:** `app.py` is a single-page dev/testing UI.
- **Docker ready:** Dockerfile and docker-compose included.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (`openai/gpt-oss-120b`) via `langchain-groq` |
| Agent framework | LangChain + LangGraph |
| Vector DB | ChromaDB (`langchain-chroma`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Web search | Tavily |
| Memory | SQLite (`langgraph-checkpoint-sqlite`) |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML + Tailwind CSS (optional Streamlit) |

## Project Structure

```
.
├── main.py                    # FastAPI server (chat, upload, health, page routes)
├── agent.py                   # LangGraph agent, system prompt, SQLite memory
├── tools.py                   # search_internal_docs (Chroma) + Tavily web search
├── ingest.py                  # Load, split, embed and store documents in ChromaDB
├── app.py                     # Optional Streamlit UI
├── ai_chatbot_interface.html  # Chat page (served at /)
├── upload_window.html         # Upload page (served at /upload-page)
├── upload_script.py           # CLI helper to upload a file to /upload
├── aura_inventory.csv         # Sample data: product inventory
├── aura_policies.txt          # Sample data: store policies
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example               # Template for your API keys
├── .env                       # Your real keys (git-ignored)
├── chroma_db/                 # Vector store (generated, git-ignored)
└── chat_memory.db             # Conversation memory (generated, git-ignored)
```

## Quick Start

**Prerequisites:** Python 3.10+, a [Groq API key](https://console.groq.com/keys), a [Tavily API key](https://app.tavily.com/). Docker is optional.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env              # Windows: copy .env.example .env
# then open .env and paste your keys

# 5. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

| URL | Purpose |
|---|---|
| http://127.0.0.1:8000/ | Chat interface |
| http://127.0.0.1:8000/upload-page | Document upload page |
| http://127.0.0.1:8000/docs | Swagger API docs |
| http://127.0.0.1:8000/health | Health check |

Prefer Streamlit? Run `streamlit run app.py` instead.

## Environment Variables

Defined in `.env` (template: `.env.example`).

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key used by the LLM |
| `TAVILY_API_KEY` | Yes | Tavily API key used for web search |

## Loading Your Knowledge Base

The agent can only answer from your own data after you ingest documents (for example `aura_inventory.csv` and `aura_policies.txt`). Pick any method:

1. **Upload page:** open `/upload-page`, choose a file, click *Upload to AI*.
2. **Script:** set `file_name` in `upload_script.py`, then run `python upload_script.py`.
3. **API:** `curl -F "file=@aura_policies.txt" http://127.0.0.1:8000/upload`

Supported formats: `.pdf`, `.docx`, `.csv`, `.txt`, `.md`.

> **Important:** `tools.py` registers the document search tool only if `./chroma_db` exists at startup. After your **first** upload, restart the server.

## API Reference

### `POST /chat`

```json
{
  "message": "Do you have any leather handbags in stock?",
  "session_id": "user_abc123"
}
```

Response: `{ "response": "Certainly! ..." }`

Reuse the same `session_id` to continue a conversation (defaults to `default_user`).

### `POST /upload`

Multipart form with a `file` field.
Response: `{ "status": "success", "message": "Successfully ingested aura_policies.txt" }`

### `GET /health`

Response: `{ "status": "Running" }`

## Docker

Docker Hub repository: [mirzaasadijaz/ai-email-dispatcher](https://hub.docker.com/repository/docker/mirzaasadijaz/ai-email-dispatcher)

### Run the published image

```bash
mkdir -p chroma_db && touch chat_memory.db

docker run -d --name ai-agent-container \
  --env-file .env \
  -p 8000:8000 \
  -v "$(pwd)/chroma_db:/app/chroma_db" \
  -v "$(pwd)/chat_memory.db:/app/chat_memory.db" \
  --restart unless-stopped \
  mirzaasadijaz/ai-email-dispatcher:latest
```

### Docker Compose

In `docker-compose.yml`, set the image to the repository above:

```yaml
image: mirzaasadijaz/ai-email-dispatcher:latest
```

Then:

```bash
docker compose up -d
```

Compose mounts `./chroma_db` and `./chat_memory.db` so vectors and chat history survive restarts. Create them first (see above) so Docker doesn't turn `chat_memory.db` into a directory.

### Build it yourself

```bash
docker build -t mirzaasadijaz/ai-email-dispatcher:latest .
docker push mirzaasadijaz/ai-email-dispatcher:latest
```

`.dockerignore` excludes `.env`, databases, `venv/`, and temp files, so secrets are never baked into the image. Pass them at runtime with `--env-file`.

## How It Works

```
Browser ──► FastAPI /chat ──► LangGraph ReAct agent (Groq LLM + system prompt)
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
        search_internal_docs              Tavily web search
        (ChromaDB, top-3 chunks)          (top-3 results)
                                   │
                                   ▼
                     SQLite checkpointer (per thread_id)
```

1. The browser generates a `session_id` and sends it with every message.
2. The agent loads that thread's history from SQLite.
3. It decides which tool (if any) to call, then answers in the brand's voice.
4. Ingestion: file → loader → 1000-char chunks (100 overlap) → MiniLM embeddings → ChromaDB.

## Configuration

| What | Where |
|---|---|
| Model / temperature | `agent.py` → `ChatGroq(...)` |
| Brand behavior and tone | `agent.py` → `system_prompt` |
| Retrieval depth | `tools.py` → `search_kwargs={"k": 3}` |
| Chunking | `ingest.py` → `chunk_size`, `chunk_overlap` |

## Known Limitations

- The HTML files call `http://127.0.0.1:8000` directly. Use relative paths (`/chat`, `/upload`) when deploying to a real domain.
- CORS is `allow_origins=["*"]` and `/upload` has no authentication. Restrict both before going public, or anyone can add data to your knowledge base.
- `session_id` lives in `sessionStorage`, so memory resets when the tab is closed.
- All uploads go into one shared ChromaDB collection with no delete or de-duplication; re-uploading a file creates duplicate chunks.
- `app.py` (Streamlit) doesn't pass a `thread_id`, so it doesn't use the persistent SQLite memory.

## Security Checklist Before Pushing to GitHub

- `.env` is listed in `.gitignore`; only commit `.env.example`.
- If a real key was ever committed, rotate it in the Groq and Tavily dashboards.
- Don't commit `chroma_db/` or `chat_memory.db`; they can contain private customer conversations and documents.

