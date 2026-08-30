import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = env.VITE_API_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/generate": {
          target: apiBase,
          changeOrigin: true,
          timeout: 300000,
          proxyTimeout: 300000,
        },
        "/outputs": {
          target: apiBase,
          changeOrigin: true,
          timeout: 60000,
        },
        "/images": {
          target: apiBase,
          changeOrigin: true,
        },
      },
    },
  };
});
