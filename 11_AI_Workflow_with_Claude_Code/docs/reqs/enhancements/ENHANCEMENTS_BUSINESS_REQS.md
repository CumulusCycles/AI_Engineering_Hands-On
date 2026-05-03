# ScriptSprout — Business requirements (post-MVP enhancements)

**Document type:** Milestone scope — **not** a second product definition  
**Audience:** Engineering during **enhancement / VIDEO_4.1a–4.2** work  
**Assumption:** **MVP is complete** (author auth, single-pass generation, history/detail, persistence, model logging).

---

## Canonical specifications (read these first)

| Document | Purpose |
|----------|---------|
| [`../BUSINESS_REQS.md`](../BUSINESS_REQS.md) | Full vision, personas, goals, glossary |
| [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md) | **All** behaviors, including enhancements |
| [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) | Full technical rules and NFRs |

**This file scopes the enhancement track only.** It does not restate the master business document.

**Enhancements functional slice:** [`ENHANCEMENTS_FUNCTIONAL_REQS.md`](./ENHANCEMENTS_FUNCTIONAL_REQS.md)

---

## Enhancement track — business outcomes (must hold)

Deliver **independent** increments (each shippable on its own), in **this order** unless the business reprioritizes:

| # | Enhancement | Author / admin outcome |
|---|-------------|-------------------------|
| **E1** | **Regenerate fields** | Author can refresh **title**, **description**, or **story** alone with **field-local** loading and errors; other fields stay intact unless master functional doc defines cascade. |
| **E2** | **Admin NLP / semantic investigation** | **Admin** runs natural-language queries (metrics and/or embedding-backed hits) via **Admin NLP query**; results and empty states are clear; **authors** do not get a separate “search my library by meaning” UI in the shipped product. |
| **E3** | **Thumbnail** | Author generates a **still** image from approved text; preview on list + full view on detail per `designs/`. |
| **E4** | **Audio narration** | Author generates **TTS** from story (or agreed excerpt policy); in-browser playback per `designs/`. |
| **E5** | **Admin dashboard** | **Admin** role can see **metrics**, **paginated AI history**, and **read-only** cross-author content inspection; **authors** never see admin surfaces. |

Each enhancement MUST respect master **business rules**: ownership, least-privilege admin, AI transparency at a high level.

---

## Explicitly **out of this enhancement track** (unless pulled in later)

The following are **still not required** unless you add a new milestone:

- Full **email verification** program  
- **Rich admin analytics / NLP studio** beyond the shipped **Admin NLP query + dashboards**  
- **Destructive cleanse** / wipe tooling (if ever added, master **BUSINESS** + **FUNCTIONAL** + **TECH** gate it behind flags)

The **master trio** remains authoritative for anything listed there.

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline post-MVP enhancement business milestone (`docs/reqs/enhancements/`). |
