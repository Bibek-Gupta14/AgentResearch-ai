import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Generator from "./components/Generator";
import BlogViewer from "./components/BlogViewer";
import styles from "./App.module.css";

// In dev the Vite proxy handles relative URLs.
// In production (Cloudflare Pages) set VITE_API_URL to the Render backend URL.
const API = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [view, setView] = useState("generate"); // 'generate' | 'blog'
  const [markdown, setMarkdown] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [outputs, setOutputs] = useState([]);

  // Load existing outputs on mount; retry every 5 s until we get data
  useEffect(() => {
    fetchOutputs();
    const id = setInterval(async () => {
      const ok = await fetchOutputs();
      if (ok) clearInterval(id);
    }, 5000);
    return () => clearInterval(id);
  }, []);

  async function fetchOutputs() {
    try {
      const res = await fetch(`${API}/outputs`);
      if (res.ok) {
        const data = await res.json();
        const files = data.files || [];
        setOutputs(files);
        return files.length > 0 || true; // resolved successfully
      }
    } catch {
      // backend not ready yet — will retry
    }
    return false;
  }

  async function handleGenerate(topic, options = {}) {
    setLoading(true);
    setError("");
    setMarkdown("");
    setTitle("");
    setView("blog");

    try {
      const res = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, ...options }),
      });

      // Safely read body once — it may not be JSON on error
      const text = await res.text();
      if (!text)
        throw new Error(`Server returned empty response (${res.status})`);

      let body;
      try {
        body = JSON.parse(text);
      } catch {
        throw new Error(`Server error ${res.status}: ${text.slice(0, 200)}`);
      }

      if (!res.ok) {
        throw new Error(body.detail || `Server error ${res.status}`);
      }

      setMarkdown(body.markdown);
      setTitle(body.title);
      fetchOutputs();
    } catch (e) {
      setError(e.message);
      setView("generate");
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadOutput(filename) {
    try {
      const res = await fetch(`${API}/outputs/${encodeURIComponent(filename)}`);
      const text = await res.text();
      if (!text) {
        setError("Empty response from server");
        return;
      }
      const data = JSON.parse(text);
      if (!res.ok) {
        setError(data.detail || "Failed to load file");
        return;
      }
      setMarkdown(data.markdown);
      setTitle(data.title);
      setView("blog");
      setError("");
    } catch (e) {
      setError("Failed to load file: " + e.message);
    }
  }

  async function handleDelete(filename) {
    try {
      await fetch(`${API}/outputs/${encodeURIComponent(filename)}`, {
        method: "DELETE",
      });
      fetchOutputs();
      // If the deleted file is currently open, go back to generator
      if (filename.replace(".md", "") === title) handleNew();
    } catch (e) {
      console.error("Delete failed:", e);
    }
  }

  function handleNew() {
    setView("generate");
    setMarkdown("");
    setTitle("");
    setError("");
  }

  return (
    <div className={styles.layout}>
      <Sidebar
        outputs={outputs}
        onLoad={handleLoadOutput}
        onNew={handleNew}
        onDelete={handleDelete}
        onRefresh={fetchOutputs}
        activeTitle={title}
      />
      <main className={styles.main}>
        {view === "generate" || loading ? (
          <Generator
            onGenerate={handleGenerate}
            loading={loading}
            error={error}
          />
        ) : (
          <BlogViewer markdown={markdown} title={title} onNew={handleNew} />
        )}
      </main>
    </div>
  );
}
