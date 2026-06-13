// Astro requires the content-collections config under src/, but the actual
// collections + schemas live in the repo-root ./content/config.ts (so all
// content — data and its schema — sits together outside src/). Re-export it.
export { collections } from "../content/config";
