import { useState, useRef, useEffect } from "react";
import styles from "./Generator.module.css";

const MAX_CHARS = 300;

const SUGGESTIONS = [
  { icon: "🤖", text: "The state of open-source LLMs in 2026" },
  { icon: "🔗", text: "How LangGraph enables multi-agent workflows" },
  { icon: "📊", text: "Building RAG pipelines with LlamaIndex and pgvector" },
  { icon: "⚖️", text: "Claude vs GPT-4o vs Gemini: developer comparison 2026" },
  { icon: "🎯", text: "Fine-tuning Llama 3 on custom datasets" },
];

const DEPTH_OPT = ["quick", "standard", "deep"];
const TONE_OPT = ["technical", "casual", "formal"];
const LENGTH_OPT = [
  { value: "short", label: "~500w" },
  { value: "medium", label: "~1000w" },
  { value: "long", label: "~2000w" },
];

export default function Generator({ onGenerate, loading, error }) {
  const [topic, setTopic] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState({
    depth: "standard",
    tone: "technical",
    citations: true,
    wordCount: "medium",
  });
  const textareaRef = useRef(null);

  // Auto-resize textarea height
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 220) + "px";
  }, [topic]);

  // Esc clears input when textarea is focused
  useEffect(() => {
    function onKey(e) {
      if (
        e.key === "Escape" &&
        document.activeElement === textareaRef.current
      ) {
        setTopic("");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const remaining = MAX_CHARS - topic.length;
  const isNearLimit = remaining < 50;
  const isOverLimit = remaining < 0;

  function handleSubmit(e) {
    e.preventDefault();
    if (!topic.trim() || loading || isOverLimit) return;
    onGenerate(topic.trim(), options);
  }

  function setOpt(key, val) {
    setOptions((o) => ({ ...o, [key]: val }));
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.bgGlow} aria-hidden="true" />
      <div className={styles.center}>
        <h1 className={styles.title}>AgentResearch.ai</h1>
        <p className={styles.sub}>
          Enter a topic and get a full AI-generated research blog with images.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* ── Textarea with char counter + clear btn ── */}
          <div className={styles.inputWrap}>
            <textarea
              ref={textareaRef}
              className={`${styles.textarea} ${isOverLimit ? styles.textareaError : ""}`}
              placeholder="e.g. The evolution of transformer architectures in 2026…"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              rows={2}
              disabled={loading}
              aria-label="Research topic"
              aria-describedby="char-counter topic-hint"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey))
                  handleSubmit(e);
              }}
            />
            {topic && !loading && (
              <button
                type="button"
                className={styles.clearBtn}
                onClick={() => {
                  setTopic("");
                  textareaRef.current?.focus();
                }}
                aria-label="Clear input (Escape)"
              >
                ✕
              </button>
            )}
            <div
              id="char-counter"
              className={`${styles.charCount} ${isNearLimit ? styles.charWarn : ""} ${isOverLimit ? styles.charOver : ""}`}
              aria-live="polite"
              aria-label={`${remaining} characters remaining`}
            >
              {remaining}
            </div>
          </div>

          {/* ── Footer row: options toggle + shortcut hint + submit ── */}
          <div className={styles.formFooter}>
            <button
              type="button"
              className={`${styles.optionsBtn} ${showOptions ? styles.optionsBtnActive : ""}`}
              onClick={() => setShowOptions((v) => !v)}
              aria-expanded={showOptions}
              aria-controls="options-panel"
            >
              ⚙ Options {showOptions ? "▲" : "▼"}
            </button>
            <span id="topic-hint" className={styles.shortcutHint}>
              ⌘↵ generate · esc clear
            </span>
            <button
              type="submit"
              className={styles.btn}
              disabled={!topic.trim() || loading || isOverLimit}
              aria-label="Generate research blog"
            >
              {loading ? (
                <span className={styles.spinner} aria-hidden="true" />
              ) : (
                "↗ Generate"
              )}
            </button>
          </div>
        </form>

        {/* ── Advanced options panel ── */}
        {showOptions && (
          <div
            id="options-panel"
            className={styles.optionsPanel}
            role="group"
            aria-label="Advanced generation options"
          >
            <OptionRow label="Research depth">
              <Segmented
                options={DEPTH_OPT}
                value={options.depth}
                onChange={(v) => setOpt("depth", v)}
              />
            </OptionRow>
            <OptionRow label="Tone">
              <Segmented
                options={TONE_OPT}
                value={options.tone}
                onChange={(v) => setOpt("tone", v)}
              />
            </OptionRow>
            <OptionRow label="Length">
              <Segmented
                options={LENGTH_OPT}
                value={options.wordCount}
                onChange={(v) => setOpt("wordCount", v)}
              />
            </OptionRow>
            <OptionRow label="Include citations">
              <Toggle
                checked={options.citations}
                onChange={() => setOpt("citations", !options.citations)}
              />
            </OptionRow>
          </div>
        )}

        {/* ── Loading ── */}
        {loading && (
          <div className={styles.progress} aria-live="polite">
            <div className={styles.progressBar} aria-hidden="true" />
            <p className={styles.progressText}>
              Researching, writing, and generating images… ~2 min
            </p>
          </div>
        )}

        {/* ── Error ── */}
        {error && (
          <div className={styles.error} role="alert" aria-live="assertive">
            <span className={styles.errorIcon} aria-hidden="true">
              ⚠
            </span>
            <div>
              <p className={styles.errorTitle}>Generation failed</p>
              <p className={styles.errorMsg}>{error}</p>
              <p className={styles.errorHint}>
                Ensure the backend is running on port 8000 and API keys are set
                in <code>.env</code>.
              </p>
            </div>
          </div>
        )}

        {/* ── Suggestion chips ── */}
        {!loading && (
          <div className={styles.suggestions}>
            <p className={styles.suggestLabel} id="suggestions-label">
              Try one of these
            </p>
            <div
              className={styles.chips}
              role="list"
              aria-labelledby="suggestions-label"
            >
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.text}
                  role="listitem"
                  className={styles.chip}
                  onClick={() => {
                    setTopic(s.text);
                    textareaRef.current?.focus();
                  }}
                  disabled={loading}
                  aria-label={`Use topic: ${s.text}`}
                >
                  <span className={styles.chipIcon} aria-hidden="true">
                    {s.icon}
                  </span>
                  {s.text}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Helper components ─────────────────────────────────────────────────────── */

function OptionRow({ label, children }) {
  return (
    <div className={styles.optionRow}>
      <span className={styles.optionLabel}>{label}</span>
      {children}
    </div>
  );
}

function Segmented({ options, value, onChange }) {
  return (
    <div className={styles.segmented} role="group">
      {options.map((opt) => {
        const val = typeof opt === "string" ? opt : opt.value;
        const label = typeof opt === "string" ? opt : opt.label;
        return (
          <button
            key={val}
            type="button"
            className={`${styles.seg} ${value === val ? styles.segActive : ""}`}
            onClick={() => onChange(val)}
            aria-pressed={value === val}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}

function Toggle({ checked, onChange }) {
  return (
    <button
      type="button"
      className={`${styles.toggle} ${checked ? styles.toggleOn : ""}`}
      onClick={onChange}
      role="switch"
      aria-checked={checked}
    >
      <span className={styles.toggleKnob} />
    </button>
  );
}
