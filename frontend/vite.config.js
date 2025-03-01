import { defineConfig } from "vite";
import { resolve } from "path";
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  // root: "src/",
  plugins: [
    tailwindcss()
  ],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, "popup.html"),
        // options: resolve(__dirname, "options.html"),
      },
      output: {
        entryFileNames: "[name].js",
      },
    },
  },
});
