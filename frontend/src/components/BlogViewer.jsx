import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./BlogViewer.module.css";

export default function BlogViewer({ markdown, title, onNew }) {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("preview"); // 'preview' | 'raw'

  function handleCopy() {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  function handleDownload() {
    // Convert the rendered prose div to a print window → Save as PDF
    const proseEl = document.getElementById("blog-prose");
    const content = proseEl ? proseEl.innerHTML : `<pre>${markdown}</pre>`;

    const win = window.open("", "_blank");
    win.document.write(`<!doctype html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>${title || "blog"}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; color: #1a1a1a; line-height: 1.7; padding: 48px 64px; max-width: 800px; margin: 0 auto; font-size: 14px; }
    h1 { font-size: 26px; font-weight: 600; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid #e5e5e5; letter-spacing: -0.02em; }
    h2 { font-size: 18px; font-weight: 600; margin: 28px 0 10px; color: #111; }
    h3 { font-size: 15px; font-weight: 600; margin: 20px 0 8px; }
    p { margin-bottom: 12px; color: #333; }
    ul, ol { padding-left: 20px; margin-bottom: 12px; }
    li { margin-bottom: 5px; color: #333; }
    a { color: #5b4fe9; text-decoration: none; }
    blockquote { border-left: 2px solid #7c6af7; padding: 8px 16px; margin: 14px 0; background: #f7f6ff; border-radius: 0 4px 4px 0; color: #555; font-size: 13px; }
    code { font-family: 'JetBrains Mono', monospace; font-size: 12px; background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
    pre { background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; margin: 14px 0; }
    pre code { background: none; padding: 0; }
    img { max-width: 100%; border-radius: 6px; margin: 14px auto; display: block; }
    em { color: #666; font-size: 12px; display: block; text-align: center; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 14px 0; }
    th { background: #f4f4f4; padding: 8px 12px; text-align: left; border: 1px solid #e5e5e5; font-weight: 500; }
    td { padding: 8px 12px; border: 1px solid #e5e5e5; color: #333; }
    @media print {
      body { padding: 0; }
      a { color: #5b4fe9; }
    }
  </style>
</head>
<body>${content}</body>
</html>`);
    win.document.close();
    win.focus();
    setTimeout(() => {
      win.print();
      win.close();
    }, 400);
  }

  return (
    <div className={styles.wrap}>
      {/* Toolbar */}
      <div className={styles.toolbar}>
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === "preview" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("preview")}
          >
            Preview
          </button>
          <button
            className={`${styles.tab} ${activeTab === "raw" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("raw")}
          >
            Markdown
          </button>
        </div>

        <div className={styles.actions}>
          <button className={styles.action} onClick={handleCopy}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <button className={styles.action} onClick={handleDownload}>
            ↓ PDF
          </button>
          <button
            className={`${styles.action} ${styles.actionPrimary}`}
            onClick={onNew}
          >
            + New Blog
          </button>
        </div>
      </div>

      {/* Content */}
      <div className={styles.content}>
        {activeTab === "preview" ? (
          <div className={styles.prose} id="blog-prose">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                img: ({ node, ...props }) => (
                  <img
                    {...props}
                    className={styles.img}
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                ),
                a: ({ node, ...props }) => (
                  <a {...props} target="_blank" rel="noopener noreferrer" />
                ),
                code: ({ node, inline, className, children, ...props }) => {
                  if (inline)
                    return (
                      <code className={styles.inlineCode} {...props}>
                        {children}
                      </code>
                    );
                  return (
                    <pre className={styles.codeBlock}>
                      <code {...props}>{children}</code>
                    </pre>
                  );
                },
              }}
            >
              {markdown}
            </ReactMarkdown>
          </div>
        ) : (
          <pre className={styles.raw}>{markdown}</pre>
        )}
      </div>
    </div>
  );
}
