# ScriptSprout — Technical requirements (post-MVP enhancements)

**Document type:** Milestone scope — **not** a second architecture spec  
**Audience:** Engineering during **enhancement / VIDEO_4.1a–4.2** work  
**Assumption:** MVP stack and patterns from [`../mvp/MVP_TECH_REQS.md`](../mvp/MVP_TECH_REQS.md) / [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) are **already in production in the repo**.

---

## Canonical specifications (read these first)

| Document | Purpose |
|----------|---------|
| [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) | Full stack, security, data, AI, search, media, admin rules |
| [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md) | Observable behavior for every enhancement |
| [`../BUSINESS_REQS.md`](../BUSINESS_REQS.md) | Product vision and constraints |

**This file scopes engineering deltas only.** It must stay **consistent** with the master technical doc — no conflicting patterns.

**Enhancements functional slice:** [`ENHANCEMENTS_FUNCTIONAL_REQS.md`](./ENHANCEMENTS_FUNCTIONAL_REQS.md)

---

## Enhancement deltas (by track)

Implement **on top of** MVP using the **same** layering and guard patterns as master **§3–5**. Below is the **minimum** technical addition per track; details live in **[`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md)** (§§8–11).

### E1 — Regenerate individual fields

- **New** author-scoped operations: regenerate **title**, **description**, **story** independently.  
- Each operation: **ownership** dependency, **single-field** AI call, **model-call logging**, **field-local** UX per **[`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md)** **§4.3**.  
- **No** change to “MVP must stay simple” rule: avoid broad refactors unrelated to E1.

### E2 — Admin NLP / semantic investigation

- Add **embedded vector store** (e.g. Chroma) + **embedding** model via environment.  
- **Startup:** initialize store with relational bootstrap (master **§9**).  
- **Indexing:** upsert/delete vectors when content text changes — policy MUST match [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md) **§4.5** (automatic vs manual — pick one and document in README if ambiguous).  
- **Query / UX:** **Admin** NLP query surface (metrics + optional embedding-backed hits) MUST be **`require_admin`** (or equivalent); **never** return another author’s vectors to a **non-admin** caller. **Shipped author UX** does not include a dedicated author-library semantic search screen.

### E3 — Thumbnail

- Image generation via provider **images** API; store **blob + MIME** on content row (or chosen storage strategy per master **§10**).  
- **Generate** and **serve** (or inline) endpoints **both** ownership-guarded.  
- Env: image model, size/quality/style as needed.

### E4 — Audio (TTS)

- TTS via provider speech API; store **blob + MIME** (+ voice metadata if required by functional **§4.7**).  
- **Generate** and **serve** endpoints ownership-guarded.  
- Env: TTS model, default voice.

### E5 — Admin dashboard

- **Activate** `admin` **role enforcement** everywhere under admin surface (master **§6**).  
- **Bootstrap admin** user from environment in **controlled** environments if you use that pattern.  
- **Routes:** metrics, paginated model-call history, read-only content inspection — all **`require_admin`**-style dependency.  
- **Frontend:** dedicated admin routes, **hidden** nav for authors, redirect on unauthorized access.

---

## Environment variables (additions beyond MVP)

Keep all MVP variables. **Typical** additions (names illustrative — mirror `.env.example`):

```
# Embeddings + vector store
OPENAI_EMBEDDING_MODEL=...
CHROMA_PATH=...

# Images
OPENAI_IMAGE_MODEL=...
THUMBNAIL_SIZE=...
THUMBNAIL_QUALITY=...
THUMBNAIL_STYLE=...

# TTS
OPENAI_TTS_MODEL=...
TTS_VOICE_DEFAULT=...

# Admin bootstrap (if used)
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
```

Never commit `.env`.

---

## Quality bar (enhancements)

Unchanged from master **[`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) §14**: each new capability gets **happy path** + **401** + **ownership** (or **403** admin) tests as applicable.

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline post-MVP enhancement technical milestone (`docs/reqs/enhancements/`). |
