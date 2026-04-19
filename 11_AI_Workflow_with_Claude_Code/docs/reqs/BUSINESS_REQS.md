# ScriptSprout — Business Requirements

**Document type:** Business requirements (pre-implementation)  
**Audience:** Product, design, architecture, and engineering  
**Status:** Draft for greenfield delivery — describes *what* the business wants and *why*, not how code is organized.

---

## 1. Executive summary

**ScriptSprout** is a web application that helps **video creators** (initially oriented toward **YouTube-style story content**) go from a **short creative brief** to **publishable text and supporting media**: titles, descriptions, long-form narrative copy, optional **cover imagery**, optional **spoken narration**, and tools to **find past work** when the creator’s library grows.

The business wants a **trustworthy, author-owned workspace**: each creator sees **only their own** drafts and finished items, with **clear feedback** when AI or network work is in progress. Separately, **operations staff** need **read-heavy insight** into usage and AI activity so the product can be supported responsibly as adoption grows.

This document states **outcomes and constraints**. **Functional behavior** is specified in `FUNCTIONAL_REQS.md`. **Technical decisions** are specified in `TECHNICAL_REQS.md`. **Visual intent** is communicated through **design mockups** supplied by the graphic design partner (see `designs/`).

---

## 2. Problem statement

- Creators routinely need **coherent packages** of title, description, and story-style copy aligned to a **subject, tone, audience, and intended runtime** — doing that repeatedly without assistance is slow.
- As libraries grow, **browsing and history** need to stay fast and trustworthy; **meaning-based investigation** for support and operations is handled on **admin** surfaces (not a separate author “search my library by meaning” UI in the shipped product).
- Teams supporting the product need **visibility** into **AI usage** and **content volume** without standing inside every author account.

---

## 3. Goals (measurable directionally)

| ID | Goal |
|----|------|
| G-1 | An **authenticated creator** can produce a **structured content package** from a guided brief in one session, with **visible progress and recoverable errors**. |
| G-2 | Creators can **browse, open, and revisit** prior work via **list and detail** surfaces; **operations** gain **meaning-based investigation** on **admin** tools when diagnosing issues across indexed content. |
| G-3 | **Optional media** (still image “cover,” audio read-through) SHOULD be generatable from approved text, where product policy and cost allow. |
| G-4 | **Operations** can review **aggregate metrics** and **AI call history** and inspect **individual content records** when investigating support issues — **without** normal author accounts gaining that breadth. |
| G-5 | The business can **explain and defend** handling of accounts, sessions, and AI data at a high level (privacy posture, retention stance) to stakeholders. |

---

## 4. Primary personas

| Persona | Needs | Non-goals (for this product) |
|---------|--------|------------------------------|
| **Author / creator** | Register, sign in, create and refine content, optional media, browse own history, sign out | Managing another author’s items |
| **Operations / admin** | Dashboard-style insight, model-usage visibility, read paths across authors for diagnosis, **strictly gated** dangerous maintenance actions | Day-to-day creative work on behalf of authors unless explicitly designed later |

---

## 5. Scope — in scope

- **Author identity** and **session-backed** access to the app.
- **Content items** owned by an author, with **text fields** suitable for publishing workflows (including optional intermediate steps such as synopsis or staged approvals — exact staging is a **functional** decision).
- **AI-assisted generation** and **targeted regeneration** of individual text fields where that improves iteration speed.
- **Admin NLP query** (metrics and/or **embedding-backed semantic investigation**) on **admin-only** surfaces.
- **Optional** image and **optional** audio generation tied to author-owned content.
- **Admin-facing** summaries and **drill-down** inspection aligned to support and governance needs.

---

## 6. Scope — out of scope or deferred (unless business explicitly reprioritizes)

- A **public marketplace** of stories or social graph.
- **Team workspaces** with shared ownership (single-owner author model is the baseline).
- **Mobile-native** clients (responsive web is sufficient unless business expands scope).
- **Legal review** of generated output — the product assists; **creators remain responsible** for compliance with platform rules and law.

---

## 7. Business rules and policies

- **Data ownership:** All author-generated rows and media belong to that author; the product MUST NOT expose one author’s content to another through author UI or APIs.
- **AI transparency (business level):** The business expects **persisted evidence** of AI calls (who triggered, what class of operation, success/failure, timing) sufficient for **cost and incident** conversations — detailed schema is technical.
- **Admin power:** Any **destructive** or **environment-altering** capability MUST be **off by default** or behind **explicit configuration** and **strong role checks** — exact controls are technical, the business rule is **least privilege**.
- **Optional identity hardening:** Email verification and account-recovery flows are **desirable** for production maturity; initial releases MAY ship a **minimal** trust model if timeboxed, provided the business accepts the risk (see functional doc for behavior if included).

---

## 8. Dependencies and assumptions

- Creators have access to a **modern browser** and a **stable network**.
- The organization will supply **AI provider** credentials and acceptable **model policy** (which models, which modalities).
- **Design mockups** in `designs/` are the **visual contract** for layout and primary states; engineering interprets them together with functional requirements.

---

## 9. Success criteria (acceptance at business level)

- A **pilot cohort** can complete: **sign up → create item → generate/refine text → (optional) add media → find item again** without support intervention for the happy path.
- **No cross-author data leakage** in pilot testing.
- **Operations** can answer: “How much AI did we use last week?” and “What happened on this support ticket’s content item?” using admin surfaces.

---

## 10. Glossary

| Term | Meaning |
|------|---------|
| **Author** | Registered creator using the author application surface. |
| **Content item** | One logical work unit (brief + generated fields + optional media) owned by an author. |
| **Admin** | Privileged operations role — not used for routine creative work. |
| **Semantic investigation (admin)** | Embedding-backed retrieval and ranking (not only substring match), composed inside **admin** NLP/support flows. |

---

## 11. Revision history

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | — | Baseline business requirements (`docs/reqs/BUSINESS_REQS.md`). |
