# Blog Generator Frontend

Minimalistic React UI for the LangGraph blog generator.

## Setup

### 1. Start the backend API (from `PROJECT/` directory)

```bash
pip install fastapi uvicorn python-multipart
uvicorn api:app --reload --port 8000
```

### 2. Start the React frontend (from `PROJECT/frontend/`)

```bash
npm install
npm run dev
```

Open **http://localhost:5173**

## Features

- Enter any topic → generates a full blog with images via LangGraph
- Preview rendered markdown with images
- Switch to raw markdown view
- Copy to clipboard / Download as `.md`
- Sidebar shows all previously generated blogs
- Click any past blog in sidebar to reload it

## Stack

- React 18 + Vite
- `react-markdown` + `remark-gfm` for rendering
- FastAPI backend proxied via Vite dev server
