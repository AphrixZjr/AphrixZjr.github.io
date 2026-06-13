// @ts-check
import { defineConfig } from "astro/config";

// User/org GitHub Pages site (AphrixZjr.github.io) deploys at the domain root,
// so no `base` path is needed. Static output, zero runtime JS by default.
export default defineConfig({
  site: "https://AphrixZjr.github.io",
  trailingSlash: "ignore",
});
