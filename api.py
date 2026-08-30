"""
FastAPI backend for the Blog Generator.
Run with: uvicorn api:app --reload --port 8000
"""

import os
import asyncio
import json
import re
from pathlib import Path
from datetime import date
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ── LangChain / LangGraph ────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated, Literal
import operator

# ── Pydantic models (same as notebook) ───────────────────────────────────────
from pydantic import BaseModel as PydanticBase

class Task(PydanticBase):
    id: str = "task_1"
    title: str
    goal: str = ""
    bullets: List[str] = []
    target_words: int = 250
    section_type: str = "body"
    tags: List[str] = []
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False

class Plan(PydanticBase):
    title: str
    audience: str = "developers and tech enthusiasts"
    tone: str = "technical and informative"
    tasks: List[Task] = []
    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = "explainer"
    constraints: List[str] = []

class EvidenceItem(PydanticBase):
    title: str = ""
    url: str = ""
    published_at: Optional[str] = None
    snippet: Optional[str] = None
    source: Optional[str] = None

class RouterDecision(PydanticBase):
    needs_research: bool = False
    mode: Literal["closed_book", "hybrid", "open_book"] = "closed_book"
    queries: List[str] = []

class EvidencePack(PydanticBase):
    evidence: List[EvidenceItem] = []

class State(TypedDict):
    topic: str
    plan: Optional[Plan]
    sections: Annotated[List[tuple], operator.add]
    final_result: str
    queries: List[str]
    evidence: List[EvidenceItem]
    mode: str
    needs_research: bool
    merged_md: str
    md_with_placeholders: str
    image_specs: List[dict]
    as_of: str
    recency_days: int

# ── LLM ──────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(
    model="openrouter/free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
)

def _extract_json_dict(text: str) -> dict:
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}

# ── Graph nodes (mirrors notebook exactly) ───────────────────────────────────
ROUTER_SYSTEM = """You are a routing module for a technical blog planner.
Decide whether web research is needed BEFORE planning.
Modes:
- closed_book (needs_research=false): Evergreen topics.
- hybrid (needs_research=true): Mostly evergreen but needs up-to-date examples.
- open_book (needs_research=true): Mostly volatile: weekly roundups, "this week", "latest".

You must respond ONLY with a raw JSON object with these keys:
{
  "needs_research": true|false,
  "mode": "closed_book"|"hybrid"|"open_book",
  "queries": ["query 1", "query 2"]
}"""

def router(state: State):
    resp = llm.invoke([
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=f"Topic: {state['topic']}"),
    ])
    raw = _extract_json_dict(resp.content)
    try:
        decision = RouterDecision.model_validate(raw)
    except Exception:
        needs_res = raw.get("needs_research", False)
        mode_val = raw.get("mode", "closed_book" if not needs_res else "hybrid")
        queries = raw.get("queries", [])
        decision = RouterDecision(needs_research=bool(needs_res), mode=mode_val, queries=queries if isinstance(queries, list) else [])
    return {"needs_research": decision.needs_research, "mode": decision.mode, "queries": decision.queries}

def route_next(state: State) -> str:
    return "research" if state["needs_research"] else "orchestrator"

def _tavily_search(query: str, max_results: int = 3):
    tool = TavilySearchResults(max_results=max_results)
    results = tool.invoke({"query": query})
    normalized = []
    for r in results or []:
        normalized.append({"title": r.get("title") or "", "url": r.get("url") or "",
            "snippet": r.get("content") or r.get("snippet") or "",
            "published_at": r.get("published_date") or r.get("published_at"), "source": r.get("source")})
    return normalized

RESEARCH_SYSTEM = """You are a research synthesizer. Given raw web search results, produce a list of EvidenceItem objects.
Rules: Only include items with a non-empty url. Keep snippets short. Deduplicate by URL.
You must respond ONLY with a raw JSON object:
{
  "evidence": [
    {"title": "...", "url": "https://...", "snippet": "..."}
  ]
}"""

def research(state: State):
    queries = state.get("queries", []) or []
    raw_results = []
    for q in queries:
        raw_results.extend(_tavily_search(q, max_results=2))
    if not raw_results:
        return {"evidence": []}
    for r in raw_results:
        if r.get("snippet") and len(r["snippet"]) > 200:
            r["snippet"] = r["snippet"][:200] + "..."
    raw_results = raw_results[:15]

    resp = llm.invoke([
        SystemMessage(content=RESEARCH_SYSTEM),
        HumanMessage(content=f"Raw results:\n{raw_results}")
    ])
    raw = _extract_json_dict(resp.content)
    evidence_list = []
    for item in raw.get("evidence", []):
        if isinstance(item, dict) and item.get("url"):
            evidence_list.append(EvidenceItem(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                published_at=item.get("published_at"),
                source=item.get("source")
            ))
    dedup = {e.url: e for e in evidence_list}
    return {"evidence": list(dedup.values())}

ORCH_SYSTEM = """You are a senior technical writer. Produce a structured outline plan for a technical blog post.
Requirements:
- Create 3-6 logical section tasks.
- Respond ONLY with a valid JSON object matching this schema:
{
  "title": "Clear Catchy Blog Title",
  "audience": "developers and AI engineers",
  "tone": "technical and practical",
  "blog_kind": "explainer",
  "tasks": [
    {
      "id": "sec_1",
      "title": "Introduction to Topic",
      "goal": "Explain what the topic is and why it matters.",
      "bullets": ["Key bullet point 1", "Key bullet point 2"],
      "target_words": 250,
      "section_type": "intro",
      "requires_research": false,
      "requires_citations": false,
      "requires_code": false
    }
  ]
}"""

def orchestrator(state: State) -> dict:
    evidence = state.get("evidence", [])
    mode = state.get("mode", "closed_book")
    resp = llm.invoke([
        SystemMessage(content=ORCH_SYSTEM),
        HumanMessage(content=(f"Topic: {state['topic']}\nMode: {mode}\n\n"
            f"Evidence:\n{[e.model_dump() for e in evidence][:16]}"))
    ])
    raw = _extract_json_dict(resp.content)

    title = raw.get("title") or state["topic"]
    audience = raw.get("audience", "developers")
    tone = raw.get("tone", "technical")
    blog_kind = raw.get("blog_kind", "explainer")
    if blog_kind not in ["explainer", "tutorial", "news_roundup", "comparison", "system_design"]:
        blog_kind = "explainer"

    tasks_raw = raw.get("tasks") or raw.get("sections") or []
    tasks = []
    if isinstance(tasks_raw, list):
        for idx, t in enumerate(tasks_raw, 1):
            if isinstance(t, dict):
                t_title = t.get("title", f"Section {idx}")
                t_goal = t.get("goal", "")
                t_bullets = t.get("bullets", [])
                if isinstance(t_bullets, str):
                    t_bullets = [t_bullets]
                t_words = t.get("target_words") or t.get("word_count") or 250
                tasks.append(Task(
                    id=f"sec_{idx}",
                    title=t_title,
                    goal=t_goal,
                    bullets=t_bullets if isinstance(t_bullets, list) else [],
                    target_words=int(t_words) if str(t_words).isdigit() else 250,
                    section_type=t.get("section_type", "body"),
                    requires_research=bool(t.get("requires_research", False)),
                    requires_citations=bool(t.get("requires_citations", False)),
                    requires_code=bool(t.get("requires_code", False)),
                ))
    if not tasks:
        tasks = [
            Task(id="sec_1", title="Introduction", goal=f"Overview of {state['topic']}", bullets=["Background", "Core concept"], target_words=200),
            Task(id="sec_2", title="Core Architecture & Working", goal="Technical breakdown", bullets=["Architecture details", "Key components"], target_words=350),
            Task(id="sec_3", title="Practical Applications & Future", goal="Real world use cases", bullets=["Applications", "Key takeaways"], target_words=250),
        ]

    plan = Plan(title=title, audience=audience, tone=tone, blog_kind=blog_kind, tasks=tasks)
    return {"plan": plan}

def fanout(state: State):
    return [Send("worker", {"task": task.model_dump(), "topic": state["topic"],
        "plan": state["plan"].model_dump(), "mode": state["mode"],
        "evidence": [e.model_dump() for e in state.get("evidence", [])]})
        for task in state["plan"].tasks]

WORKER_SYSTEM = """You are a senior technical writer. Write ONE section of a technical blog post in Markdown.
Start with a '## <Section Title>' heading. Follow the Goal and cover ALL Bullets."""

def worker(payload: dict):
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]
    mode = payload.get("mode", "closed_book")
    bullets = "\n- " + "\n- ".join(task.bullets)
    evidence_text = "\n".join(f"- {e.title} | {e.url}" for e in evidence[:20]) if evidence else ""
    section = llm.invoke([
        SystemMessage(content=WORKER_SYSTEM),
        HumanMessage(content=(f"Title: {plan.title}\nAudience: {plan.audience}\nTone: {plan.tone}\n"
            f"Blog kind: {plan.blog_kind}\nTopic: {payload['topic']}\nMode: {mode}\n"
            f"Section: {task.title}\nGoal: {task.goal}\nBullets: {bullets}\n"
            f"Target words: {task.target_words}\nrequires_citations: {task.requires_citations}\n"
            f"Evidence:\n{evidence_text}"))
    ]).content
    return {"sections": [(task.id, section)]}

def merge(state: State):
    plan = state["plan"]
    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    return {"merged_md": f"# {plan.title}\n\n{body}\n"}

DECIDE_IMAGES_SYSTEM = """You are an expert technical editor. Create exactly 2 image specs for this blog.
For each image: section_keyword (exact phrase from heading), alt, caption, prompt (detailed), filename.
IMPORTANT: section_keyword must match a ## heading exactly.
Return a JSON array of exactly 2 objects."""

def decide_for_images(state: State):
    merged_md = state["merged_md"]
    response = llm.invoke([
        SystemMessage(content=DECIDE_IMAGES_SYSTEM),
        HumanMessage(content=f"Blog kind: {state['plan'].blog_kind}\nTopic: {state['topic']}\n\n{merged_md[:3000]}")
    ]).content
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        image_specs_raw = json.loads(json_match.group()) if json_match else []
    except:
        image_specs_raw = []

    if not image_specs_raw:
        return {"md_with_placeholders": merged_md, "image_specs": []}

    md_with_placeholders = merged_md
    image_specs = []
    for idx, spec in enumerate(image_specs_raw[:2], 1):
        placeholder = f"[[IMAGE_{idx}]]"
        section_keyword = spec.get("section_keyword", "")
        inserted = False
        if section_keyword:
            pattern = rf'(##\s+[^\n]*{re.escape(section_keyword)}[^\n]*\n)'
            match = re.search(pattern, md_with_placeholders, re.IGNORECASE)
            if match:
                insert_pos = match.end()
                md_with_placeholders = (md_with_placeholders[:insert_pos] +
                    f"\n{placeholder}\n\n" + md_with_placeholders[insert_pos:])
                inserted = True
            if not inserted:
                body_match = re.search(re.escape(section_keyword), md_with_placeholders, re.IGNORECASE)
                if body_match:
                    pos = body_match.start()
                    para_start = md_with_placeholders.rfind('\n\n', 0, pos)
                    para_start = para_start + 2 if para_start != -1 else 0
                    md_with_placeholders = (md_with_placeholders[:para_start] +
                        f"{placeholder}\n\n" + md_with_placeholders[para_start:])
                    inserted = True
        if not inserted:
            conclusion_match = re.search(r'(##\s+Conclusion[^\n]*\n)', md_with_placeholders, re.IGNORECASE)
            if conclusion_match:
                md_with_placeholders = (md_with_placeholders[:conclusion_match.start()] +
                    f"{placeholder}\n\n" + md_with_placeholders[conclusion_match.start():])
            else:
                md_with_placeholders += f"\n\n{placeholder}\n"
        image_specs.append({"placeholder": placeholder, "filename": spec.get("filename", f"image_{idx}.png"),
            "alt": spec.get("alt", ""), "caption": spec.get("caption", ""), "prompt": spec.get("prompt", "")})
    return {"md_with_placeholders": md_with_placeholders, "image_specs": image_specs}

def generate_and_place_images(state: State):
    from huggingface_hub import InferenceClient
    from io import BytesIO
    import time

    plan = state["plan"]
    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs", []) or []
    safe_title = plan.title.replace(":", " -").replace("/", "-").replace("\\", "-").replace("?","").replace("*","").replace("|","-").replace("<","").replace(">","").replace('"',"")

    if not image_specs:
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        file_path = outputs_dir / f"{safe_title}.md"
        file_path.write_text(md, encoding="utf-8")
        return {"final_result": md}

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    api_key = os.environ.get("HUGGINGFACE_API_KEY")

    for idx, spec in enumerate(image_specs, 1):
        placeholder = spec["placeholder"]
        filename = spec["filename"]
        out_path = images_dir / filename
        if not out_path.exists() and api_key:
            try:
                if idx > 1:
                    time.sleep(3)
                client = InferenceClient(token=api_key)
                image = client.text_to_image(prompt=spec["prompt"], model="black-forest-labs/FLUX.1-schnell")
                img_bytes = BytesIO()
                image.save(img_bytes, format="PNG")
                out_path.write_bytes(img_bytes.getvalue())
            except Exception as e:
                md = md.replace(placeholder, f"> **[Image: {spec.get('caption','')}]**\n")
                continue
        img_md = f"![{spec['alt']}](/images/{filename})\n*{spec['caption']}*"
        md = md.replace(placeholder, img_md)

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    file_path = outputs_dir / f"{safe_title}.md"
    file_path.write_text(md, encoding="utf-8")
    return {"final_result": md}

# ── Build graph ───────────────────────────────────────────────────────────────
subgraph = StateGraph(State)
subgraph.add_node("merge_content", merge)
subgraph.add_node("decide_images", decide_for_images)
subgraph.add_node("generate_and_place_images", generate_and_place_images)
subgraph.add_edge(START, "merge_content")
subgraph.add_edge("merge_content", "decide_images")
subgraph.add_edge("decide_images", "generate_and_place_images")
subgraph.add_edge("generate_and_place_images", END)
reducer_graph = subgraph.compile()

graph = StateGraph(State)
graph.add_node("router", router)
graph.add_node("research", research)
graph.add_node("orchestrator", orchestrator)
graph.add_node("worker", worker)
graph.add_node("reducer", reducer_graph)
graph.add_edge(START, "router")
graph.add_conditional_edges("router", route_next, {"research": "research", "orchestrator": "orchestrator"})
graph.add_edge("research", "orchestrator")
graph.add_conditional_edges("orchestrator", fanout, ["worker"])
graph.add_edge("worker", "reducer")
graph.add_edge("reducer", END)
app_graph = graph.compile()

# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(title="Blog Generator API")

# In production set ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images statically
images_path = Path("images")
images_path.mkdir(exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")

class GenerateRequest(BaseModel):
    topic: str
    depth: str = "standard"       # quick | standard | deep
    tone: str = "technical"        # technical | casual | formal
    word_count: str = "medium"     # short | medium | long
    citations: bool = True

class GenerateResponse(BaseModel):
    markdown: str
    title: str

@app.get("/health")
def health():
    return {"status": "ok", "message": "Blog Generator API is running"}

# ── Serve React build in production ──────────────────────────────────────────
_frontend_dist = Path("frontend/dist")
if _frontend_dist.exists():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles as _SF
    app.mount("/assets", _SF(directory=str(_frontend_dist / "assets"), name="assets"), )

    @app.get("/")
    def serve_root():
        return FileResponse(str(_frontend_dist / "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Let API routes pass through; catch-all serves the SPA
        candidate = _frontend_dist / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_frontend_dist / "index.html"))

@app.post("/generate", response_model=GenerateResponse)
async def generate_blog(req: GenerateRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    # Build an enriched topic string that injects user options into the LLM pipeline
    length_map = {"short": "~500 words", "medium": "~1000 words", "long": "~2000 words"}
    enriched_topic = (
        f"{req.topic}\n"
        f"[Options: depth={req.depth}, tone={req.tone}, "
        f"length={length_map.get(req.word_count, req.word_count)}, "
        f"citations={'yes' if req.citations else 'no'}]"
    )
    try:
        output = await asyncio.to_thread(app_graph.invoke, {
            "topic": enriched_topic, "mode": "", "needs_research": False,
            "queries": [], "as_of": date.today().isoformat(), "evidence": [],
            "plan": None, "md_with_placeholders": "", "sections": [],
            "merged_md": "", "recency_days": 7, "image_specs": [], "final_result": "",
        })
        markdown = output.get("final_result", "")
        # extract title from first H1
        title_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
        title = title_match.group(1) if title_match else req.topic
        return GenerateResponse(markdown=markdown, title=title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/outputs")
def list_outputs():
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    files = [
        {
            "filename": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
            "created_at": f.stat().st_ctime,
        }
        for f in outputs_dir.glob("*.md")
    ]
    files.sort(key=lambda x: x["modified"], reverse=True)
    return {"files": files}

@app.get("/outputs/{filename}")
def get_output(filename: str):
    file_path = Path("outputs") / filename
    if not file_path.exists() or not file_path.suffix == ".md":
        raise HTTPException(status_code=404, detail="File not found")
    return {"markdown": file_path.read_text(encoding="utf-8"), "title": filename.replace(".md", "")}

@app.delete("/outputs/{filename}")
def delete_output(filename: str):
    file_path = Path("outputs") / filename
    if not file_path.exists() or not file_path.suffix == ".md":
        raise HTTPException(status_code=404, detail="File not found")
    file_path.unlink()
    return {"deleted": filename}
