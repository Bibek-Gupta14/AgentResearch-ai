# AgentResearch.ai

An AI-powered research blog generator built with **LangGraph**, **Groq (Llama 3.3 70B)**, **Tavily** web search, and **HuggingFace** image generation. Features a React + Vite frontend with a ChatGPT-style UI.

---

## Architecture

```
Frontend (React + Vite)  ──►  FastAPI backend  ──►  LangGraph pipeline
                                                         ├── Router node (closed/hybrid/open_book)
                                                         ├── Research node (Tavily search)
                                                         ├── Orchestrator node (outline planning)
                                                         ├── Worker nodes (parallel section writing)
                                                         └── Reducer (merge + image generation)
```

---

## Local Development

### 1. Clone & set up Python environment

```bash
git clone https://github.com/your-username/agentresearch-ai.git
cd agentresearch-ai

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Required keys:
| Key | Where to get it |
|-----|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) |
| `HUGGINGFACE_API_KEY` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

### 3. Start the backend

```bash
cd PROJECT
uvicorn api:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd PROJECT/frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Production Deployment (single server)

### Build the frontend

```bash
cd PROJECT/frontend
npm run build          # outputs to frontend/dist/
```

### Run the backend (serves the React build too)

```bash
cd PROJECT
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
```

The FastAPI app auto-detects `frontend/dist/` and serves the SPA — no separate web server needed.

Set these environment variables on your server:

```
GROQ_API_KEY=...
TAVILY_API_KEY=...
HUGGINGFACE_API_KEY=...
ALLOWED_ORIGINS=https://yourdomain.com
```

### Deploy to Railway / Render

1. Connect your GitHub repo
2. Set the **root directory** to `PROJECT`
3. Set **build command**: `pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..`
4. Set **start command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Add all env vars in the dashboard

> ⚠️ Generated `outputs/` and `images/` are written to disk. On ephemeral containers (Railway free tier) these reset on restart. For persistence, mount a volume or swap to cloud storage (S3/R2).

---

## Project Structure

```
PROJECT/
├── api.py                  # FastAPI backend + LangGraph pipeline
├── requirements.txt
├── .env.example
├── outputs/                # Generated .md blogs (gitignored)
├── images/                 # Generated images (gitignored)
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Generator.jsx      # Input UI
    │   │   ├── Sidebar.jsx        # Blog history
    │   │   └── BlogViewer.jsx     # Markdown renderer
    └── vite.config.js
```

---

## Tech Stack

| Layer         | Technology                         |
| ------------- | ---------------------------------- |
| LLM           | Groq — Llama 3.3 70B Versatile     |
| Orchestration | LangGraph (parallel worker fanout) |
| Web search    | Tavily Search API                  |
| Image gen     | HuggingFace FLUX.1-schnell         |
| Backend       | FastAPI + Uvicorn                  |
| Frontend      | React 18 + Vite + CSS Modules      |
