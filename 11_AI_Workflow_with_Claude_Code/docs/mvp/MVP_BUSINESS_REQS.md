# ScriptSprout — Business requirements (MVP milestone)

**Document type:** Milestone scope — **not** a second product definition  
**Audience:** Engineering during **MVP / Video 12** work

---

## Canonical specifications (read these first)

The **full product** intent lives in the master trio (parent `docs/` folder):

| Document | Purpose |
|----------|---------|
| [`../BUSINESS_REQS.md`](../BUSINESS_REQS.md) | Vision, personas, goals, glossary, in/out of scope for the **whole** product |
| [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md) | Observable behavior, roles, UX rules — **authoritative** for “what must happen” |
| [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) | Stack, architecture, security, data concepts, quality bar |

**This file does not replace those documents.** It tells you **which business outcomes MVP must satisfy** and what to **defer** without re-reading the full corpus.

**MVP functional slice (behaviors):** see [`MVP_FUNCTIONAL_REQS.md`](./MVP_FUNCTIONAL_REQS.md) — still a pointer + checklist, not a duplicate spec.

---

## MVP — business outcomes (must hold)

When MVP is done, a **pilot author** can:

1. **Register and sign in**, stay signed in across refresh until logout or expiry, and **sign out**.
2. Submit a **structured brief** (subject, genre, audience, length proxy — exact fields follow `designs/`).
3. Receive a **generated text bundle** for YouTube-style use: at minimum **title**, **description**, and **story** in one operation.
4. See **loading, error, empty, and success** states for generation and history (aligned with `designs/` and `FUNCTIONAL_REQS.md`).
5. **Persist** every item automatically; **reopen** any past item from **their own** history only.
6. Trust that **no author** can access another author’s items — per **`BUSINESS_REQS.md` §7** (data ownership) and **`BUSINESS_REQS.md` §9** (pilot success: no cross-author data leakage).

---

## Explicitly **out of scope for MVP** (defer to enhancements)

Do **not** implement in MVP; they are covered after MVP in [`../enhancements/ENHANCEMENTS_BUSINESS_REQS.md`](../enhancements/ENHANCEMENTS_BUSINESS_REQS.md) / [`../enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`](../enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md):

- Per-field **regeneration** (title / description / story independently)
- **Admin NLP / semantic investigation** (embedding-backed retrieval for **admin** support flows)
- **Thumbnail** and **audio** generation
- **Admin** role, dashboard, cross-author inspection, and related operational tooling

Optional capabilities described in the master docs (email verification, advanced admin tools, etc.) remain **governed by the master** documents — treat as **out of MVP** unless you explicitly pull them into a later milestone.

---

## Revision

| Version | Notes |
|---------|--------|
| 0.2 | Restructured as milestone pointer + scope; master trio is canonical. |
| 0.3 | Moved under `docs/mvp/`; enhancements pointers renamed to `ENHANCEMENTS_*`. |
| 0.4 | Master filenames use `*_REQS.md`; functional slice is `MVP_FUNCTIONAL_REQS.md`. |
| 0.5 | Outcome #6: cite master business §7 / §9 (not G-2 / P-1). |
