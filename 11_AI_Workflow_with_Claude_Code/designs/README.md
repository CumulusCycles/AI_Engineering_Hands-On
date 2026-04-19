# Designs — UI specification for ScriptSprout

This folder is the **visual source of truth** for the product. **Use this README as the entry point** when implementing or changing frontend UI—whether you were pointed here from functional requirements, prompts, or project rules—so layout, states, colors, and branding stay aligned with what the design team specified.

**How this relates to other docs**

- **`COLOR_PALETTE.md`** (in this folder) — exact colors, shadows, and usage rules. **Do not invent colors** outside this palette unless a mockup clearly introduces a one-off exception (then note it in code comments and keep it rare).
- **`docs/reqs/FUNCTIONAL_REQS.md`** — behavior, roles, and acceptance rules. If a mockup and the functional spec disagree on **security or data rules**, the functional spec wins; on **pure layout/visuals**, these designs win.
- **`mockup-pages/`** — **Canonical screen mockups**: one static **HTML** file per screen/state, plus shared **`mockup-pages/mockup-base.css`**. Read the HTML **and** the CSS to recover structure, hierarchy, spacing, and component patterns. Open files in a browser when you need a pixel-level visual check (shared styles load via relative path from each HTML file).
- **`brand/`** — **identity assets** used in the shipped app (e.g. logo, favicon, transparent mark). Mockup HTML references these via `../brand/…` when previewing in a browser.

If a listed mockup file is **not present yet**, treat this README as the **naming and coverage contract**—implement the corresponding screen from the description and add the asset when the design team delivers it.

---

## Folder layout

| Path | Purpose |
|------|--------|
| **`README.md`** | This file — how to use `designs/` and what each asset group means. |
| **`COLOR_PALETTE.md`** | Token-level color specification for the whole UI. |
| **`mockup-pages/`** | Static HTML mockups (`*.html`) + **`mockup-base.css`** — primary reference for layout and states. |
| **`mockup-pages/index.html`** | Local index linking to each mockup page (optional convenience). |
| **`brand/`** | Logos, favicon, and related marks for the live app chrome. |

---

## How to use mockup pages (for implementation)

1. Identify the **feature or route** you are building (e.g. registration, generation form, history detail).
2. Open the **mockup HTML** listed for that feature in the inventory below (`mockup-pages/<basename>.html`). Read **`mockup-pages/mockup-base.css`** for shared tokens and component styling used across pages.
3. Match **layout, spacing, typography scale, component grouping, and state treatment** (loading / error / empty / success) as shown in the markup and CSS.
4. Apply colors strictly from **`COLOR_PALETTE.md`** (the mockup CSS is aligned with it).
5. **Do not** introduce new UI patterns, extra chrome, or alternate flows that are not shown—if something is missing, align with **`docs/reqs/FUNCTIONAL_REQS.md`** and ask for a spec update rather than inventing layout.

Prompts and implementation notes should cite paths under **`designs/mockup-pages/`** (see the inventory below). Each screen/state uses the same **basename** as the inventory row (e.g. `auth-login.html`).

---

## For agents

- Models can read the **HTML and CSS** from the repository directly—structure, spacing, and component patterns are explicit in source.
- Use **`mockup-base.css`** together with each page: shared rules define nav, cards, buttons, grids, and admin chrome.
- **Optional:** Open a mockup in a browser (from `mockup-pages/`) if you need to **see** the composed page; relative links to **`../brand/`** resolve when the file is opened from disk or via a static server.

---

## Mockup inventory (`mockup-pages/`)

All paths below are relative to the **`designs/`** folder (e.g. `mockup-pages/auth-login.html`). Each row is one standalone page plus shared **`mockup-pages/mockup-base.css`**.

### Authentication (MVP)

| File | Description |
|------|-------------|
| `mockup-pages/auth-register.html` | Registration — username/password (or fields per spec), link to login. |
| `mockup-pages/auth-login.html` | Login — credentials form, link to register. |

### Generation (MVP)

| File | Description |
|------|-------------|
| `mockup-pages/generation-form-empty.html` | Author studio — prompt extraction empty; no content rows yet. |
| `mockup-pages/generation-form-loading.html` | Author studio — extraction in progress (`Extracting…`). |
| `mockup-pages/generation-form-error.html` | Author studio — extraction error with actionable message. |
| `mockup-pages/generation-results.html` | Author studio — draft approvals + story and media success state. |

### History (MVP)

| File | Description |
|------|-------------|
| `mockup-pages/history-empty.html` | Author studio — no content rows; CTA to create from extraction. |
| `mockup-pages/history-list.html` | Author studio — content row picker with context. |
| `mockup-pages/history-detail.html` | Author studio — draft review block for one item (synopsis / title / description). |

### Regenerate fields (Enhancement 1)

| File | Description |
|------|-------------|
| `mockup-pages/detail-regenerate.html` | Author studio — per-field regenerate controls; synopsis row emphasized. |

### Semantic search (Enhancement 2)

| File | Description |
|------|-------------|
| `mockup-pages/search-bar.html` | **Admin** — `Admin NLP query`: query field ready to run (semantic search is composed server-side for admins, not an author History feature). |
| `mockup-pages/search-results.html` | **Admin** — NLP response includes ranked **semantic hits** with context (cross-author scope). |
| `mockup-pages/search-empty.html` | **Admin** — NLP response with **no semantic matches** in query scope (empty hit list). |

### Thumbnails (Enhancement 3)

| File | Description |
|------|-------------|
| `mockup-pages/detail-thumbnail-empty.html` | Author studio — no thumbnail yet; generate control; placeholder. |
| `mockup-pages/detail-thumbnail-loading.html` | Author studio — thumbnail generation in progress. |
| `mockup-pages/detail-thumbnail.html` | Author studio — thumbnail visible. |
| `mockup-pages/history-list-thumbnails.html` | List-style rows with thumbnail previews or placeholders. |

### Audio narration (Enhancement 4)

| File | Description |
|------|-------------|
| `mockup-pages/detail-audio-empty.html` | Author studio — no audio yet; generate control; placeholder. |
| `mockup-pages/detail-audio-loading.html` | Author studio — audio generation in progress. |
| `mockup-pages/detail-audio.html` | Author studio — in-browser audio player mock. |

### Admin (Enhancement 5)

| File | Description |
|------|-------------|
| `mockup-pages/admin-dashboard.html` | Admin — metrics / KPIs panel. |
| `mockup-pages/admin-model-calls.html` | Admin — paginated model-call history. |
| `mockup-pages/admin-content-detail.html` | Admin — read-only cross-user content inspection. |
| `mockup-pages/admin-nav.html` | Chrome — admin entry only for admin role (home with admin nav). |

---

## Brand assets (`brand/`)

Use for **global** presentation: app header, footer, favicon, PWA/meta icons, and marketing hero—not as substitutes for **`mockup-pages/`** screen comps.

Typical files (names may vary slightly; keep this table aligned with what is checked in):

| File | Typical use |
|------|-------------|
| `brand/logo.png` | Primary logo lockup. |
| `brand/icon_transparent.png` | Mark on varied backgrounds. |
| `brand/favicon.png` | Browser tab / shortcut icon. |

---

## Agent checklist (before shipping UI)

- [ ] Read **`COLOR_PALETTE.md`** and restricted colors to that spec.
- [ ] Read every **relevant `mockup-pages/*.html`** plus **`mockup-pages/mockup-base.css`** for the feature and matched structure and states.
- [ ] Wired **`brand/`** assets where the shell or metadata need them.
- [ ] Loading, error, empty, and success states exist wherever **mockup pages** show them.
- [ ] No cross-user leakage of admin UI for non-admin sessions (see admin **mockup pages** + functional spec).

---

## Revision

| Version | Notes |
|---------|-------|
| 1.0 | Baseline: **`mockup-pages/`** (HTML + CSS), **`COLOR_PALETTE.md`**, **`brand/`**. |
