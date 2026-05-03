# ScriptSprout — Functional requirements (MVP milestone)

**Document type:** Milestone slice — **not** a second functional spec  
**Audience:** Engineering / QA during **MVP / VIDEO_2.1–2.2**

---

## Canonical specification

**Authoritative functional spec:** [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md)

**This file** lists **which sections and requirement IDs** apply to MVP so you can read the master once and use this as a **checklist**. If anything here disagrees with the master, **the master wins**.

**Related:** [`../BUSINESS_REQS.md`](../BUSINESS_REQS.md), [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md), [`MVP_BUSINESS_REQS.md`](./MVP_BUSINESS_REQS.md), [`MVP_TECH_REQS.md`](./MVP_TECH_REQS.md)

---

## MVP — include these master sections

| Master § | Topic | MVP notes |
|----------|--------|-----------|
| **§1** | Introduction, conventions | Applies in full. |
| **§2** | Actors and roles | **Guest** + **Author** required. **Admin** behaviors in §5 are **out of MVP** (no admin UI/routes yet). |
| **§3** | Cross-cutting UX (`FX-*`) | Applies in full — loading / error / empty / success, session loss, destructive confirm only if MVP UI has destructive actions. |
| **§4.1** | Registration and authentication (`A-*`) | Applies — register, login, logout, me; **A-5** email verification is **optional** for MVP unless you explicitly add it. |
| **§4.2** | Create and generate (`C-*`) | **C-1–C-4** apply. Synopsis (`C-2`) is **in scope for MVP** — `designs/` require it. Title, description, story, and synopsis are all required fields. |
| **§4.4** | History and detail (`H-*`) | Applies in full. |
| **§6** | Data and privacy (`P-*`) | Applies as written. |
| **§7** | Non-functional behavior, user-visible (`N-*`) | Applies in full — responsive async UX; laptop-scale viewports per **`designs/`**. |
| **§8** | Out of scope (functional) | Do **not** implement features listed there unless a future milestone explicitly adds them. |

---

## MVP — exclude these master sections (defer)

Do **not** implement for MVP:

| Master § | Reason |
|----------|--------|
| **§4.3** | Regenerate individual fields → **enhancements** |
| **§4.5** | Admin NLP / semantic investigation (`S-*`) → **enhancements** |
| **§4.6** | Thumbnail → **enhancements** |
| **§4.7** | Audio → **enhancements** |
| **§5** | Admin journeys (`M-*`, `X-*`) → **enhancements** |

---

## Visual contract

All MVP screens MUST follow the **`designs/`** folder at **repository root** (sibling to `docs/`) and **`designs/COLOR_PALETTE.md`**.

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline MVP functional milestone (`docs/reqs/mvp/`). |
