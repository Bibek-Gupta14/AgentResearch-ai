import { useState, useMemo } from "react";
import styles from "./Sidebar.module.css";

function groupByDate(files) {
  const now = new Date();
  const today = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
  ).getTime();
  const week = today - 6 * 24 * 60 * 60 * 1000;
  const groups = { Today: [], "This Week": [], Older: [] };
  for (const f of files) {
    const ts = f.created_at ? f.created_at * 1000 : 0;
    if (ts >= today) groups["Today"].push(f);
    else if (ts >= week) groups["This Week"].push(f);
    else groups["Older"].push(f);
  }
  return groups;
}

export default function Sidebar({
  outputs,
  onLoad,
  onNew,
  onDelete,
  onRefresh,
  activeTitle,
}) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!search.trim()) return outputs;
    const q = search.toLowerCase();
    return outputs.filter((f) => f.filename.toLowerCase().includes(q));
  }, [outputs, search]);

  const groups = useMemo(() => groupByDate(filtered), [filtered]);
  const hasAny = filtered.length > 0;

  return (
    <aside className={styles.sidebar} aria-label="Sidebar navigation">
      {/* ── Brand header ── */}
      <div className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.brandIcon}>✦</span>
          <div>
            <p className={styles.brandName}>AgentResearch</p>
            <p className={styles.brandTag}>.ai</p>
          </div>
        </div>
        <button
          className={styles.refreshBtn}
          onClick={onRefresh}
          aria-label="Refresh blog list"
          title="Refresh"
        >
          ↻
        </button>
      </div>

      {/* ── New Research button ── */}
      <div className={styles.newWrap}>
        <button
          className={styles.newBtn}
          onClick={onNew}
          aria-label="New research blog"
        >
          <span className={styles.newBtnIcon}>✎</span>
          New Research
        </button>
      </div>

      {/* ── Search ── */}
      <div className={styles.searchWrap}>
        <span className={styles.searchIcon} aria-hidden="true">
          ⌕
        </span>
        <input
          className={styles.search}
          type="search"
          placeholder="Search blogs…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search recent blogs"
        />
        {search && (
          <button
            className={styles.searchClear}
            onClick={() => setSearch("")}
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      {/* ── Blog list ── */}
      <nav className={styles.nav} aria-label="Recent blogs">
        {!hasAny ? (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>📄</span>
            <p className={styles.emptyTitle}>
              {search ? "No results" : "No blogs yet"}
            </p>
            <p className={styles.emptyHint}>
              {search
                ? "Try a different search"
                : "Generate your first research blog"}
            </p>
          </div>
        ) : (
          Object.entries(groups).map(([label, items]) =>
            items.length === 0 ? null : (
              <div key={label} className={styles.group}>
                <p className={styles.groupLabel}>{label}</p>
                <ul className={styles.list}>
                  {items.map((f) => {
                    const name = f.filename.replace(".md", "");
                    const isActive = name === activeTitle;
                    return (
                      <li key={f.filename} className={styles.listItem}>
                        <button
                          className={`${styles.item} ${isActive ? styles.active : ""}`}
                          onClick={() => onLoad(f.filename)}
                          aria-current={isActive ? "page" : undefined}
                        >
                          <span className={styles.itemIcon} aria-hidden="true">
                            📝
                          </span>
                          <span className={styles.name}>{name}</span>
                        </button>
                        {onDelete && (
                          <button
                            className={styles.deleteBtn}
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(f.filename);
                            }}
                            aria-label={`Delete ${name}`}
                            title="Delete"
                          >
                            ✕
                          </button>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            ),
          )
        )}
      </nav>

      {/* ── Footer ── */}
      <div className={styles.footer}>
        <div className={styles.footerRow}>
          <span className={styles.footerIcon}>⚡</span>
          <span className={styles.footerText}>
            LangGraph · Groq · HuggingFace
          </span>
        </div>
      </div>
    </aside>
  );
}
