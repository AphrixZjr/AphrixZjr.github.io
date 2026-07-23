import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// ── Content lives in the repo-root ./content (not src/content). Astro requires
// the collections config under src/, so src/content.config.ts re-exports this. ──

// Card cover accent comes from this enum only — no free-form hex per item.
// This is what prevents per-content color drift (VIS §8 / FRONTEND_DESIGN §1.1).
const accent = z.enum(["anchor", "acid", "rose", "pink", "mint", "orange"]);

// One Zod schema, shared by `projects` and `more` (one component master).
// Differences come only from preset fields: accent, tags, featured, year.
const card = z.object({
  title:    z.string(),
  summary:  z.string().max(140),
  href:     z.string().url(),            // external link (required) — cards open externally
  image:    z.string(),                  // cover image (/images/…)
  tags:     z.array(z.string()).max(5).default([]),
  accent:   accent.default("anchor"),    // cover color: enum only, no free hex
  featured: z.boolean().default(false),  // star + colored hard shadow
  year:     z.coerce.number().optional(),
  order:    z.number().default(0),       // descending: give new top entries the next number
});

// Homepage text content — no hardcoded copy in index.astro.
const home = z.object({
  name:    z.string(),
  tagline: z.string(),
  aboutme: z.array(z.string()).default([]),   // paragraphs; a trailing CJK line is fine
  links:   z.array(z.object({                 // homepage external links (§3.6)
    label: z.string(),
    href:  z.string(),
    order: z.number().default(0),
  })).default([]),
});

export const collections = {
  projects: defineCollection({ loader: glob({ pattern: "**/*.yaml", base: "./content/projects" }), schema: card }),
  more:     defineCollection({ loader: glob({ pattern: "**/*.yaml", base: "./content/more" }),     schema: card }),
  home:     defineCollection({ loader: glob({ pattern: "*.yaml",    base: "./content" }),           schema: home }),
};
