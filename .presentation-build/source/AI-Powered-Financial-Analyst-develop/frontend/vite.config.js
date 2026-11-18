import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  test: {
    // No test files exist yet — this is a Phase 1 skeleton (see App.jsx).
    // Real component tests land alongside the dashboard/auth pages in a
    // later phase; until then, an empty test suite shouldn't fail CI.
    passWithNoTests: true,
  },
});