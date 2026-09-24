import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const chemistryApiTarget = env.VITE_CHEMISTRY_API_BASE_URL || "http://127.0.0.1:8002";

  return {
    base: env.VITE_BASE_PATH || "/",
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api/chemistry": {
          target: chemistryApiTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
