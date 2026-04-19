# ScriptSprout — Functional Requirements

**Document type:** Functional / product behavior (pre-implementation)  
**Audience:** Design, engineering, QA — together with **design mockups** in `designs/`  
**Status:** Draft — specifies **observable behavior**, not internal code structure.

**Related:** `BUSINESS_REQS.md`, `TECHNICAL_REQS.md`

---

## 1. Introduction

This document defines **what the system does** from the perspective of **users and integrators**: journeys, screens, states, permissions, and **acceptance-oriented** requirements. Visual layout, spacing, and branding MUST align with **`designs/`** (graphic design deliverables). Where mockups and this document differ, **designs win for UI**, and **this document wins for security and data rules** — conflicts MUST be escalated in spec, not silently “fixed” in code.

**Convention:** **MUST** / **MUST NOT** are hard requirements. **SHOULD** / **MAY** indicate expected or optional behavior.

---

## 2. Actors and roles

| Actor | Role key (conceptual) | Capabilities summary |
|-------|----------------------|------------------------|
| **Guest** | unauthenticated | Register, log in, view public marketing shell if any |
| **Author** | author | Full creative lifecycle on **own** content only |
| **Admin** | admin | Metrics, AI history, cross-author **read** inspection, optional gated maintenance |

The system MUST enforce that **author** capabilities never operate on another author’s primary content without an explicit future feature. **Admin** capabilities MUST be blocked for author-only sessions.

---

## 3. Cross-cutting UX (all authenticated surfaces)

| ID | Requirement |
|----|-------------|
| FX-1 | Every **async** operation (generation, regeneration, media, search) MUST present **loading**, **success**, **empty** (where applicable), and **recoverable error** states consistent with **`designs/`**. |
| FX-2 | Forms MUST validate **obvious** input constraints before submission (required fields, numeric ranges where applicable); server-side validation remains authoritative (see technical doc). |
| FX-3 | After **session loss** or **401**, the client MUST NOT leave the user in a broken shell; the user SHOULD be guided to **sign in** again before retrying protected actions. |
| FX-4 | Destructive actions (delete, reset, admin cleanse if present) MUST require **confirmation** patterns shown in **`designs/`** when mockups specify them. |

---

## 4. Author journeys

### 4.1 Registration and authentication

| ID | Requirement |
|----|-------------|
| A-1 | A guest MUST be able to **register** with credentials and constraints defined in technical requirements (password rules, uniqueness). |
| A-2 | A guest MUST be able to **log in** and establish a **server-side session** reflected in the client per technical requirements. |
| A-3 | An author MUST be able to **log out**, invalidating the session server-side. |
| A-4 | An author MUST be able to view **current account summary** (e.g. username / email) where the UI provides it. |
| A-5 | **Email verification** (request + confirm) SHOULD be supported if the business enables it; if not in v1, the system MUST still behave safely for unverified addresses (e.g. no elevated actions relying on email trust). |

**Acceptance (happy path):** Register → land in authenticated experience → refresh still authenticated until expiry or logout → logout → protected routes inaccessible.

---

### 4.2 Create and generate a content item

| ID | Requirement |
|----|-------------|
| C-1 | An author MUST be able to start a new **content item** from a **brief** capturing at least: narrative **subject**, **genre** (or style family), **audience** (e.g. age band), and **intended runtime** (or length proxy). Exact field names MAY match **`designs/`**. |
| C-2 | The system MUST support **AI-assisted generation** of a **text bundle** suitable for publishing: at minimum **title**, **description**, and **story body**; **synopsis** or other staging steps SHOULD be supported if shown in **`designs/`** or required by business. |
| C-3 | Generation MUST show **in-flight** state and MUST surface **actionable errors** (e.g. quota, network, validation) without leaking internal stack traces to the client. |
| C-4 | The system SHOULD support **guardrails or quality passes** (e.g. structured checks, retries with limits) when business policy requires safer storytelling; if present, failures MUST be understandable to the author. |

**Acceptance:** Author submits brief → receives coherent title/description/story (and optional synopsis) → can open item detail later and see the same data.

---

### 4.3 Regenerate parts of an item

| ID | Requirement |
|----|-------------|
| R-1 | Where **`designs/`** show per-field actions, the author MUST be able to **regenerate** **title**, **description**, and **story** (and synopsis if applicable) **independently**. |
| R-2 | Regenerating one field MUST NOT silently discard other fields unless the functional **staging rules** explicitly define cascade behavior; any cascade SHOULD match copy in **`designs/`** or explicit spec notes. |
| R-3 | Each regeneration SHOULD display **field-local loading** so the author can continue reading other parts of the item. |

---

### 4.4 History and detail

| ID | Requirement |
|----|-------------|
| H-1 | An author MUST see a **list** of their content items with enough summary to choose one (e.g. subject/title snippet, date). |
| H-2 | An author MUST open a **detail** view showing brief inputs and generated outputs (aligned with **`designs/`**). |
| H-3 | **Empty history** MUST match the empty state in **`designs/`**. |

---

### 4.5 Admin NLP query (metrics / semantic investigation)

| ID | Requirement |
|----|-------------|
| S-1 | **Admin** MUST be able to submit **natural-language questions** from the **Admin NLP query** UX (per **`designs/`**). The system MAY respond with a **plan summary**, optional **metrics snapshot**, and/or **semantic hits** composed **server-side** (same surface as the shipped app). |
| S-2 | Any **semantic** portion MUST require an **admin** session and MUST **not** expose one author’s content to another through **author** UI. Hit lists SHOULD include enough context (e.g. id, title/snippet) for support triage when feasible. |
| S-3 | **No semantic matches**, empty metrics windows, and **parse/plan** failures MUST use clear treatments consistent with **`designs/`** (e.g. `mockup-pages/search-empty.html` patterns). |
| S-4 | Author-owned content SHOULD become **indexed for embeddings** after agreed triggers so **admin** investigation stays meaningful; any **author-visible** copy about indexing MUST stay consistent with the technical indexing policy. |

---

### 4.6 Thumbnail (still image)

| ID | Requirement |
|----|-------------|
| T-1 | From item detail, the author SHOULD be able to request a **thumbnail** derived from the story (or synopsis if that is the agreed source of truth). |
| T-2 | The UI MUST show **progress** and **failure** states per **`designs/`**. |
| T-3 | The history list SHOULD show a **preview** when a thumbnail exists and a **placeholder** when not, per **`designs/`**. |

---

### 4.7 Audio narration

| ID | Requirement |
|----|-------------|
| U-1 | From item detail, the author SHOULD be able to request **text-to-speech** audio for the story (or an agreed excerpt policy). |
| U-2 | Playback MUST use a **standard in-browser** audio experience with controls consistent with **`designs/`**. |
| U-3 | The author SHOULD be able to choose among **allowed voices** if **`designs/`** show voice selection; otherwise a **sensible default** MAY apply. |

---

## 5. Admin journeys

### 5.1 Access and navigation

| ID | Requirement |
|----|-------------|
| M-1 | Only **admin** sessions MUST reach admin screens and admin-only API operations. |
| M-2 | Author UI MUST **hide** admin entry points unless the session is admin; direct navigation to admin URLs by non-admins MUST fail safely (redirect or error per **`designs/`**). |

---

### 5.2 Dashboard and observability

| ID | Requirement |
|----|-------------|
| M-3 | Admin MUST see **time-bounded metrics** (e.g. volume of content, AI activity summaries) appropriate to pilot operations — exact KPIs MAY follow **`designs/`**. |
| M-4 | Admin MUST be able to browse **AI call history** with **pagination** sufficient for investigation. |
| M-5 | Admin MUST be able to open a **read-only** view of a **content item** across authors for support (fields as agreed with business/compliance). |

---

### 5.3 Optional advanced admin tools

| ID | Requirement |
|----|-------------|
| X-1 | **Destructive reset** or “cleanse” operations, if offered, MUST be **disabled by default** at the environment level and MUST require **admin + explicit configuration** + **strong confirmation** in UI. |
| X-2 | **Structured “query” or NLP-assisted investigation** tools for admins SHOULD follow **`designs/`**; if shipped, outputs MUST remain **read-only** unless a separate business case authorizes writes. |

---

## 6. Data and privacy (functional)

| ID | Requirement |
|----|-------------|
| P-1 | **Personal data** shown in UI MUST match what the account holds; exports outside the app are out of scope unless added later. |
| P-2 | Error messages shown to authors and admins MUST **avoid** exposing internal identifiers or secrets unnecessarily. |

---

## 7. Non-functional behavior (user-visible)

| ID | Requirement |
|----|-------------|
| N-1 | Primary interactions SHOULD remain responsive under **normal** pilot load; long AI operations SHOULD use **async UX**, not blocking the entire shell. |
| N-2 | The application SHOULD remain usable on **common laptop viewport sizes** reflected in **`designs/`**. |

---

## 8. Out of scope (functional)

- Collaborative **real-time** editing.
- **Public** content discovery between authors.
- **Billing** and subscription management (unless business adds a module later).

---

## 9. Revision history

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | — | Baseline functional requirements (`docs/reqs/FUNCTIONAL_REQS.md`). |
