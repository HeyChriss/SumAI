import { defineConfig } from "vite";

export default defineConfig({
  root: "src/",
  plugins: [
    tailwindcss(),
  ],
  build: {
    outDir: "../dist",
    rollupOptions: {
      input: {

      }
    }
  }
});
