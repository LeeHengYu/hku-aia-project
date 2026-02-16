import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "https://hku-aia-gemini-backend-841899024016.asia-east2.run.app",
    },
  },
});
