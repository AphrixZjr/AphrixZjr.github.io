# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

This is a **personal portfolio / content-archive website**. The Astro site has been **scaffolded from the design docs and builds cleanly** (`npm run build` → 3 static pages). The **homepage (`/`) is fully laid out** with placeholder content (name, bio, external links, placeholder portrait/cover SVGs); `/projects` and `/more` render the shared `Card` master over placeholder `.yaml` entries. Remaining work is mostly **replacing placeholders with real content** (text, images, `cv.pdf`) and adding content entries — not re-architecting.

The two documents in `doc/` remain the source of truth; read them before changing visual structure:

- **`doc/VIS_DESIGN.md`** — the *visual intent* ("what mood we want"). Style: **Acid Memphis × Editorial Brutalism**. Defines the §1–§11 design principles. **§11 (judgment criteria) is the final arbiter** when anything conflicts.
- **`doc/FRONTEND_DESIGN.md`** — the *implementation mapping* ("how to realize it in Astro + native CSS"). Concrete tokens, components, frontmatter schema, and file structure. Cross-references VIS_DESIGN section numbers throughout.

When the two conflict, VIS_DESIGN's §11 criteria win:
1. Content updates require no re-layout.
2. The page is instantly recognizable as *not* a generic AI interface.
3. Style elements never obstruct the reading path.

## Planned tech stack (per FRONTEND_DESIGN §0, §7)

- **Astro** — build-time rendering, static output hosted on **GitHub Pages** (repo name `AphrixZjr.github.io`).
- **Native CSS custom properties** for design tokens — **no Tailwind**. All visual values live as tokens; components consume variables and never hardcode numbers.
- **Astro content collections + Zod** for content; new content = a new `.yaml`/`.json` data file under the same schema, inheriting the visual framework automatically.
- **Zero runtime JS** by default; effects are CSS-only.
- **Self-hosted fonts via Fontsource** (build-time bundled, no runtime requests).

Planned `src/` layout is specified in FRONTEND_DESIGN §7 — follow it when scaffolding.

## Non-negotiable design constraints

These are hard rules from the design docs. Enforce them in any code you write or review:

- **Tokens are the single style source.** Define everything in `src/styles/tokens.css`. Components reference `var(--…)`; literal magic numbers in components are a violation.
- **Brutalist surface language:** site-wide `--radius: 0`. **Forbidden everywhere:** `border-radius > 0`, `filter: blur`, any `box-shadow` with a blur radius, glass/frosted effects. Hierarchy is built only from `border + hard offset-shadow + color contrast`.
- **Operating color palette** (a deliberate tightening of VIS §3's 6 equal neons): **4 load-bearing colors** (`--c-anchor` electric blue-violet, `--c-acid` acid yellow-green, `--c-ink` true black, `--c-paper` warm paper-white) carry ~95% of the surface; **4 accent colors** (rose/pink/mint/orange) are quota-limited to ≤~5% area per screen. `--c-acid` is the single strongest attention trigger — **use it sparingly; the less it appears, the louder it is.**
- **Card cover accent colors come from a frontmatter enum** (`["anchor","acid","rose","pink","mint","orange"]`) — **no free-form hex per content item.** This is what prevents per-item color drift.
- **Deterministic "breaking the grid."** Content-flow asymmetry (image left/right alternation, indents, offsets) is derived from index / `nth-child` only — **never hand-placed coordinates**. Break rules are centralized in `src/styles/breaks.css`. In the content flow, **rotation, text-wrap, and per-item manual collage are forbidden**; `transform: rotate()` is allowed only on a single static homepage decoration with a hardcoded token angle.
- **One component master per content type.** Cards (`projects` / `more`) share one `Card.astro` and one Zod schema; differences come only from preset fields (`accent`, `tags`, `featured`, `year`). Never author a bespoke layout for a single card.
- **Three-tier type system:** `--font-display` (Unbounded, posters/headings) / `--font-body` (Schibsted Grotesk, with PingFang SC / YaHei fallback for occasional Chinese) / `--font-mono` (Martian Mono, meta/tags/notes). No ultra-thin weights.
- **English-first site;** Chinese appears only sparsely in the bio/about-me, covered by the body font fallback — no separate CJK display font.
- **Cards link externally:** `target="_blank"` always with `rel="noopener noreferrer"` and an "(opens in new tab)" SR label; cards always carry the `mark-arrow ↗`.
- **CV is a download, not a page:** `<a href="/cv.pdf" download>` from both the Nav and the homepage entry card — no route.
- **Animation is restrained,** CSS-only: a one-time staggered homepage entrance and a hard-shadow "press" hover (`steps()`, not easing). Respect `prefers-reduced-motion`.

## Pages (FRONTEND_DESIGN §4.3)

- `/` — homepage: hand-tuned asymmetric single page (the *only* place manual asymmetry is allowed); personal image + about-me + 3 `EntryCard`s (Project/More routes, CV download) + `LinkList` of external links.
- `/projects` — `SectionHeader` + single-column `Card` list (academic projects).
- `/more` — same structure as projects, different default accent (non-academic work).

## Build/run commands

- `npm install` — install deps (Astro + three Fontsource packages; no Tailwind).
- `npm run dev` — local dev server with HMR.
- `npm run build` — static output to `dist/` (what GitHub Pages serves).
- `npm run preview` — serve the built `dist/` locally.

## Implemented layout (actual `src/`)

Matches FRONTEND_DESIGN §7. Key files when extending:

- `src/styles/` — `tokens.css` (the single style source), `base.css` (reset + paper ground + `.accent-*` helpers + `.mark-*` markers + the **`.texture-margins` card-page shell**, §10.2), `breaks.css` (deterministic `nth-child` grid-breaking).
- `src/components/` — `Card.astro` (the one card master), `Tag.astro`, `SectionHeader.astro`, `Nav.astro`, `EntryCard.astro` (homepage main visual), `LinkList.astro` (homepage secondary), `Markers.astro` (inline arrow/star glyphs via `currentColor`).
- `src/layouts/BaseLayout.astro` — imports tokens/base/breaks + Fontsource weights (display 700/800/900, body 400/600, mono 400/500) + `Nav`.
- **§10 visual reinforcement (formal — no separate stylesheet, no rollback toggle):**
  - **§10.1 hero split** lives in `index.astro`'s scoped `<style>` (homepage owns it): full-bleed band, blue-violet 2/3 text + acid 1/3 portrait. The portrait is scaled up *visually* (`transform: scale(1.25)`, so the band height is unchanged) and anchored bottom-left (overflow clipped). To keep acid as the page's sole climax, the CV `EntryCard` is `accent="rose"` and the about-me `.hl` highlight is de-acided.
  - **§10.2 texture margins** = the `.texture-margins` shell in `base.css`, wrapped around `projects.astro`/`more.astro`: a clashing-color irregular curved **blotch** texture (`public/textures/blotches.svg`, generated by `scripts/gen_blotches.py`) in the side margins; full-height flex so the opaque paper reading column always fills the fold. Header + cards centered in a narrower track inside the wider (1080px) panel for symmetric gutters.
- **Content lives in repo-root `./content/`** (not `src/content/`), via the Astro content-layer `glob` loader. `content/config.ts` holds the schemas + collections; `src/content.config.ts` is a one-line re-export of it (Astro requires the config under `src/`). Collections: `projects`/`more` (card schema) + `home` (singleton, `content/home.yaml` → `name`/`tagline`/`aboutme`/`links`). `index.astro` reads the homepage text via `getCollection("home")[0]` — **no hardcoded copy in templates**.
- `src/pages/` — `index.astro` (homepage), `projects.astro`, `more.astro`.
- `public/` — `cv.pdf` (placeholder), `images/` (placeholder SVG cover; **`portrait{1,2}.jpg` sources + `portrait{1,2}-acid.png` processed**), `textures/grain.svg` + **`blotches.svg`** (generated), `favicon.svg`.

## Portrait pipeline (offline, §10.1)

`scripts/process_portraits.py` (Python: Pillow + numpy + `rembg`/`onnxruntime`, models cached in `~/.u2net/`) turns `public/images/portraitN.jpg` into the transparent `portraitN-acid.png` used by the hero. It is a **3-layer misregistration composite**: top = white-black grayscale (keeps the face legible), middle = dot grid nudged right, bottom = white-pink grayscale nudged left. Matte = `isnet-general-use` raw mask + a per-image **alpha levels boost** (`alpha_lo/alpha_hi` in the `PORTRAITS` dict) that recovers low-confidence regions (e.g. a dark skirt at ~0.3 alpha) and hardens hair edges. Tunables (offset, dots, contrast) are constants at the top. The hero portrait is one swappable line in `index.astro` (`heroPortrait`). Re-run: `python scripts/process_portraits.py`. (`scripts/_preview/` holds on-acid review composites; not deployed.)

The card-page margin texture is regenerated by `scripts/gen_blotches.py` (Python: stdlib only; seeded for reproducibility) → `public/textures/blotches.svg`. Re-run to reshuffle/retune the blotches.

**Replacing placeholders:** swap the SVGs in `public/images/` and the real `public/cv.pdf`; edit homepage copy (`name`/`tagline`/`aboutme`/`links`) in `content/home.yaml`; add cards by dropping new `.yaml` files under `content/projects/` or `content/more/` (same schema — visual framework is inherited, no layout work). New portrait photos → drop `portraitN.jpg`, add an entry to `PORTRAITS`, re-run the pipeline.
