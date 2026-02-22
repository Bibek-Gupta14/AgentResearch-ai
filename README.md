<div align="center">

# ✦ AgentResearch.ai

_Transform any topic into a deep, publication-ready research blog — in seconds_

---

### 🎯 **Try It Now 👇🏼**

<a href="https://agentresearch.ai" target="_blank">
  <img src="https://img.shields.io/badge/🚀_LIVE-TRY_NOW-FF0000?style=for-the-badge&labelColor=000000" alt="Live Demo" height="50">
</a>

**👆 Click above to generate your first AI research blog instantly!**

---

### ⚡ **Powered By Cutting-Edge Technologies**

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10+-F2D9A0?style=for-the-badge&logo=python&logoColor=white" alt="Python" height="26">
  </a>
  <a href="https://langchain.com/">
    <img src="https://img.shields.io/badge/🦜_LangGraph-Latest-C668FF?style=for-the-badge&logoColor=white" alt="LangGraph" height="26">
  </a>
  <a href="https://groq.com/">
    <img src="https://img.shields.io/badge/⚡_Groq-Powered-F55036?style=for-the-badge&logoColor=white" alt="Groq" height="26">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" height="26">
  </a>
  <a href="https://vitejs.dev/">
    <img src="https://img.shields.io/badge/React_+_Vite-18+-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" height="26">
  </a>
</p>

<p align="center">
  <strong>🦙 Llama 3.3 70B</strong> • <strong>🔍 Tavily Search</strong> • <strong>🎨 FLUX.1-schnell</strong> • <strong>🤗 HuggingFace</strong>
</p>

</div>

---

## 🌟 Overview

### 🚀 **Your AI Research Team — On Demand**

Tired of spending hours researching, writing, and formatting technical blog posts? **AgentResearch.ai** deploys a full multi-agent pipeline that does it all for you.

💡 **What makes AgentResearch.ai special?**

🎯 **Just Give It a Topic** — Type anything from _"The Working Architecture of Transformers"_ to _"State of Open-Source LLMs 2026"_ and get a fully structured, multi-section research blog with citations.

⚡ **Parallel Agent Architecture** — Built on **LangGraph**, the pipeline fans out worker agents to write each section simultaneously — then merges everything into a cohesive blog. Dramatically faster than sequential writing.

🔍 **Real Web Research** — A smart router decides if your topic needs live web data. If yes, **Tavily** searches the web and feeds curated evidence into every section.

🎨 **Auto-Generated Images** — **HuggingFace FLUX.1-schnell** generates contextually placed images for each blog automatically.

📚 **Full History** — Every generated blog is saved. Reload, search, and manage your entire research library from the Gemini-style sidebar.

```
┌──────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│    Router    │────▶│  Research   │────▶│  Orchestrator    │────▶│   Workers    │
│  (route to  │     │  (Tavily    │     │  (outline plan)  │     │  (parallel   │
│  research?) │     │   search)   │     │                  │     │   writers)   │
└──────────────┘     └─────────────┘     └──────────────────┘     └──────┬───────┘
                                                                          │
                                                                          ▼
                                                                   ┌──────────────┐
                                                                   │   Reducer    │
                                                                   │ (merge + AI  │
                                                                   │   images)   │
                                                                   └──────────────┘
```

**Perfect for:** Tech bloggers, researchers, developers writing documentation, content teams, or anyone who wants expert-level research blogs without the hours of work.

---

## ✨ Features

### 🚀 **Core Capabilities**

- **🧠 Multi-Agent Pipeline** — Router → Research → Orchestrator → Parallel Workers → Reducer
- **🔍 Live Web Research** — Tavily-powered search for current events, news, and up-to-date technical content
- **✍️ Parallel Section Writing** — LangGraph fans out worker nodes for each section simultaneously
- **🎨 AI Image Generation** — FLUX.1-schnell generates and places contextual images automatically
- **📚 Research Library** — All blogs saved to disk, searchable, with date grouping in the sidebar
- **💾 One-Click Load** — Instantly reload any past blog from the history panel

### 🎯 **Advanced Features**

- **⚙️ Generation Options** — Control depth (quick/standard/deep), tone (technical/casual/formal), length, and citations toggle
- **📅 Temporal Awareness** — Router detects time-sensitive topics and forces live research automatically
- **🔒 Smart Routing** — Three modes: `closed_book`, `hybrid`, `open_book` — chosen automatically per topic
- **🗑️ Blog Management** — Delete individual blogs directly from the sidebar
- **↻ Auto-Refresh** — Sidebar polls for new blogs as they're generated in real time

---

## 🏗️ Architecture

```
AgentResearch.ai/
├── 📡 api.py                        # FastAPI backend + full LangGraph pipeline
├── 📋 requirements.txt
├── 🔐 .env.example
├── 📂 outputs/                      # Generated .md blogs (gitignored)
├── 🖼️  images/                      # AI-generated images (gitignored)
└── 🖥️  frontend/
    ├── vite.config.js
    └── src/
        ├── App.jsx                  # State management + API calls
        └── components/
            ├── Generator.jsx        # Topic input, options panel, suggestions
            ├── Generator.module.css
            ├── Sidebar.jsx          # Blog history, search, date groups
            ├── Sidebar.module.css
            ├── BlogViewer.jsx       # Markdown renderer
            └── BlogViewer.module.css
```

---

## 🛠️ Technology Stack

| Component         | Technology                    | Purpose                           |
| ----------------- | ----------------------------- | --------------------------------- |
| **LLM**           | 🦙 Llama 3.3 70B (Groq)       | Fast, accurate text generation    |
| **Orchestration** | 🦜 LangGraph                  | Parallel multi-agent pipeline     |
| **Web Search**    | 🔍 Tavily Search API          | Live research for current topics  |
| **Image Gen**     | 🎨 HuggingFace FLUX.1-schnell | Auto-generated blog images        |
| **Backend**       | ⚡ FastAPI + Uvicorn          | REST API + static file serving    |
| **Frontend**      | ⚛️ React 18 + Vite            | ChatGPT-style UI with CSS Modules |

---

## 📦 Getting Started

### 💻 **Run Locally**

**Prerequisites:**

- Python 3.10+
- Node.js 18+
- API keys for Groq and Tavily (HuggingFace optional)

**Step 1 — Clone & set up Python**

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

**Step 2 — Configure environment variables**

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

| Key                   | Where to get it                                                                                 |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| `GROQ_API_KEY`        | [console.groq.com](https://console.groq.com) — free tier available                              |
| `TAVILY_API_KEY`      | [app.tavily.com](https://app.tavily.com) — free tier available                                  |
| `HUGGINGFACE_API_KEY` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — optional, for images |

**Step 3 — Start the backend**

```bash
cd agentresearch-ai
uvicorn api:app --reload --port 8000
```

**Step 4 — Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) 🎉

---

## 🎮 Usage

### Basic Workflow

1. **✍️ Enter a Topic**
   - Type any research topic in the input box
   - Use suggestion chips for inspiration (e.g. _"Explain RAG architectures"_)

2. **⚙️ (Optional) Set Options**
   - Click **Options** to choose depth, tone, length, and citations
   - Default settings work great for most topics

3. **🚀 Generate**
   - Hit the Generate button or press `Enter`
   - Watch the pipeline run (typically 30–90 seconds)

4. **📚 Browse History**
   - All past blogs appear in the left sidebar, grouped by date
   - Search, click to reload, or delete any entry

### Example Topics

```
🔬 "The Working Architecture of Transformers"
📊 "State of Open-Source LLMs — February 2026"
🏗️  "System Design of a Real-Time Chat Application"
🛡️  "How RLHF Makes LLMs Safer"
⚡  "Comparing LangGraph vs CrewAI vs AutoGen"
📱 "Building Production RAG Systems"
```

---

## 🤝 Contributing

Contributions are welcome!

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔀 Open a Pull Request

---

## 🗺️ Roadmap

- [ ] 🌐 Export blogs as PDF / HTML
- [ ] 📊 Blog analytics dashboard (word count, topic clusters)
- [ ] 🔐 User authentication + multi-user library
- [ ] ☁️ S3/R2 storage for generated outputs and images
- [ ] 🔄 Streaming output (token-by-token display while generating)
- [ ] 🤖 Additional LLM providers (OpenAI, Anthropic, Gemini)
- [ ] 📱 Mobile-responsive layout
- [ ] 🌍 Multi-language blog generation

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) — For the powerful multi-agent orchestration framework
- [Groq](https://groq.com/) — For lightning-fast LLM inference
- [Tavily](https://tavily.com/) — For real-time web research capabilities
- [HuggingFace](https://huggingface.co/) — For open-source image generation models

---

<div align="center">

**Built with ❤️ using LangGraph, Groq, and React**

⭐ Star this repo if it saves you hours of research writing!

</div>
