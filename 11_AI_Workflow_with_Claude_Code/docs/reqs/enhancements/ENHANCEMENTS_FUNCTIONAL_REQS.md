# ScriptSprout — Functional requirements (post-MVP enhancements)

**Document type:** Milestone slice — **not** a second functional spec  
**Audience:** Engineering / QA during **enhancement / Video 13**  
**Assumption:** **MVP** behaviors in [`../mvp/MVP_FUNCTIONAL_REQS.md`](../mvp/MVP_FUNCTIONAL_REQS.md) are **already implemented**.

---

## Canonical specification

**Authoritative functional spec:** [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md)

**This file** lists **which master sections** apply to the **enhancement track** (E1–E5) in the usual teaching order. If anything here disagrees with the master, **the master wins**.

**Related:** [`ENHANCEMENTS_BUSINESS_REQS.md`](./ENHANCEMENTS_BUSINESS_REQS.md), [`ENHANCEMENTS_TECH_REQS.md`](./ENHANCEMENTS_TECH_REQS.md)

---

## Enhancements — map to master sections

| Track | Master § | Requirement IDs (reference) |
|-------|-----------|------------------------------|
| **E1 Regenerate** | **§4.3** | `R-*` |
| **E2 Admin NLP / semantic investigation** | **§4.5** | `S-*` |
| **E3 Thumbnail** | **§4.6** | `T-*` |
| **E4 Audio** | **§4.7** | `U-*` |
| **E5 Admin** | **§5** | `M-*`; optional advanced tools **`X-*`** only if business enables them |

**Cross-cutting:** **§3** (`FX-*`) continues to apply to **all** new screens and async flows.

**Privacy:** **§6** (`P-*`) applies; admin read paths must still avoid unnecessary PII exposure.

---

## Still deferred (unless you add a new milestone)

Items intentionally **not** part of the default E1–E5 teaching track (see master **§8** and enhancements business doc):

- Public discovery, billing, collaborative editing, etc.  
- **Email verification** as a full program (**§4.1 A-5**) when it was outside the MVP slice — add only when spec’d.  
- **Destructive admin** / **cleanse** (**§5 X-1**) — only with explicit business + technical gating.

---

## Visual contract

Enhancement screens MUST follow the **`designs/`** folder at **repository root** and **`designs/COLOR_PALETTE.md`**.

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline post-MVP enhancement functional milestone (`docs/reqs/enhancements/`). |
