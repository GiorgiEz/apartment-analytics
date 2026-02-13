import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
    root: "src",

    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src"),
            "@js": path.resolve(__dirname, "src/js"),
            "@components": path.resolve(__dirname, "src/js/components"),
            "@helpers": path.resolve(__dirname, "src/js/helpers"),
            "@partials": path.resolve(__dirname, "src/partials"),
            "@css": path.resolve(__dirname, "src/css"),
            "@charts": path.resolve(__dirname, "src/charts"),
        },
    },

    server: {
        port: 5173,
        strictPort: true,
        proxy: {
            "/api": {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
            },
        },
    },

    build: {
        outDir: "../dist",
        emptyOutDir: true,
    },
});
