import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In production the SPA is served by FastAPI from the same origin, so every
// request is relative and there is no CORS at all. In development Vite proxies
// /api to the local backend to reproduce that same-origin behaviour.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:9600",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
