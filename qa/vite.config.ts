import { defineConfig, mergeConfig } from "vite";
import base from "../vite.config";

export default mergeConfig(base, defineConfig({
  server: {
    host: "127.0.0.1", port: 5178, strictPort: true,
    proxy: { "/api": "http://127.0.0.1:8011", "/__qa__": "http://127.0.0.1:8011" },
  },
  plugins: [{
    name: "label-offline-demo",
    transformIndexHtml() {
      return [{
        tag: "div", injectTo: "body-prepend",
        attrs: { role: "note", "aria-label": "Fixture demo mode", style: "position:sticky;top:0;z-index:9999;padding:10px;background:#fff0b3;color:#322700;text-align:center;font:600 14px sans-serif" },
        children: "FIXTURE / OFFLINE DEMO — curated NASA records; partial evidence index; no numeric measurements. Moon Base values are hypothetical.",
      }];
    },
  }],
}));
