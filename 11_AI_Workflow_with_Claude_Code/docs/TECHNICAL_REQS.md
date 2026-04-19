# ScriptSprout — Technical Requirements

**Document type:** Architecture and engineering constraints (pre-implementation)  
**Audience:** Engineering, DevOps, security review  
**Status:** Draft — defines **how** the system should be built at a **structural** level, without prescribing a prior codebase.

**Related:** `BUSINESS_REQS.md`, `FUNCTIONAL_REQS.md`

---

## 1. Technical goals

| ID | Goal |
|----|------|
| TG-1 | **Maintainable** monolith-style web app: clear **separation** between HTTP boundary, domain logic, persistence, and integrations. |
| TG-2 | **Secure by default** for a browser client: authenticated **author** data never crosses **ownership** boundaries; **admin** powers are **explicit** and **auditable**. |
| TG-3 | **Testable** core behavior with automated checks suitable for CI. |
| TG-4 | **Operable** AI usage: every provider call SHOULD be **recorded** with enough metadata for cost and incident review (see §8). |

---

## 2. Recommended technology stack

The architecture team selects the following stack unless a written exception is approved:

| Layer | Choice | Notes |
|-------|--------|--------|
| **Backend language** | Python 3.11+ | |
| **HTTP framework** | FastAPI | Async-capable ASGI app. |
| **Persistence ORM** | SQLAlchemy 2.x | Explicit models; avoid ad-hoc SQL in route handlers. |
| **Settings** | Pydantic Settings (or equivalent) | **No secrets** in source; configuration from environment. |
| **Primary database** | SQLite for pilot | File-backed; path configurable. MUST support **schema bootstrap** on startup for greenfield installs. |
| **Vector search** | Embedded vector store (e.g. Chroma persistent on disk) | For **embedding-backed retrieval** over indexed content (metadata supports **author scoping** where APIs allow it; **admin** investigation uses **admin-only** routes and policies). |
| **AI provider** | OpenAI (or compatible) via official SDK | Text generation, embeddings, image generation, TTS as required by functional doc. |
| **Frontend** | React + TypeScript + Vite | SPA or SPA-like client behind `npm` toolchain. |
| **Routing** | Client-side router | Protected routes for authenticated experiences. |
| **Testing** | Backend: pytest + HTTP client; Frontend: unit/component tests; optional E2E later | CI SHOULD run **lint + unit tests** at minimum. |

Engineering MAY adjust minor library versions but MUST preserve the **layering** and **security** rules in this document.

---

## 3. High-level architecture

### 3.1 Logical layers (backend)

| Layer | Responsibility |
|-------|----------------|
| **HTTP routes** | Authn/z checks, parse/validate input, map to HTTP status, **no** embedded business rules beyond trivial guards. |
| **Services** | Business workflows: generation, regeneration, media, indexing, orchestration of multi-step AI flows. |
| **Repositories** | CRUD and queries; **no** HTTP concepts. |
| **Integration adapters** | AI provider calls isolated here; retries/timeouts centralized where possible. |
| **Schemas** | Pydantic (or equivalent) request/response models — **single source** for API contracts. |

### 3.2 Frontend structure

| Rule | Requirement |
|------|-------------|
| FE-1 | **API access** MUST live in dedicated **client modules** (not scattered `fetch` in leaf components). |
| FE-2 | Shared **TypeScript types** SHOULD mirror API contracts for the portions implemented. |
| FE-3 | **Route guards** MUST enforce authenticated vs guest vs admin routes consistently with functional requirements. |

---

## 4. API design principles

| ID | Requirement |
|----|-------------|
| API-1 | Public HTTP surface SHOULD be grouped under a **stable prefix** (e.g. `/api/...`) for both **author** and **admin** resources; alternative consistent prefixes are acceptable if documented in the repo README. |
| API-2 | **Author-owned resources** MUST be loaded through a **shared dependency** that enforces **404-or-deny** semantics for wrong ownership (avoid **200** with empty body on cross-owner IDs). |
| API-3 | **Admin-only** operations MUST use a **separate guard** from author guards; role checks MUST NOT be copy-pasted per route in fragile ad-hoc form — a **single** admin dependency pattern is expected. |
| API-4 | Error payloads SHOULD follow a **consistent JSON shape** (code + human message) without leaking stack traces in production configuration. |

Exact path strings and OpenAPI export are **implementation details** left to engineering, provided behaviors in `FUNCTIONAL_REQS.md` are satisfied.

---

## 5. Authentication and sessions

| ID | Requirement |
|----|-------------|
| SEC-1 | Use **server-side sessions** with an **HTTP-only, Secure (when deployed with HTTPS), SameSite-aware** session cookie. Session identifier MUST be **opaque** (random), not a JWT containing PII. |
| SEC-2 | Password storage MUST use a **slow, salted** one-way hashing algorithm (e.g. bcrypt or argon2). |
| SEC-3 | **Rate limiting** MUST apply to **authentication endpoints** (per IP or equivalent) to reduce brute-force risk. |
| SEC-4 | Account lockout or backoff after repeated failed logins SHOULD be implemented; parameters MUST be configurable. |
| SEC-5 | Session **TTL** and cookie **name** MUST be configurable via environment. |

---

## 6. Authorization model

| ID | Requirement |
|----|-------------|
| AUTHZ-1 | Users carry a **role** (at minimum **`author`** and **`admin`**). Engineering MAY add future roles only with spec updates. |
| AUTHZ-2 | **Admin bootstrap** (initial admin user) SHOULD be supported via **environment-provided credentials** on first boot in controlled environments; production rollout MUST follow safer procedures if required by the business. |
| AUTHZ-3 | Any **cross-author read** is **admin-only** and MUST be logged at least at the HTTP/audit level where feasible. |

---

## 7. Data model (conceptual)

Engineering MUST implement persistence that supports at least:

| Entity (conceptual) | Key fields / notes |
|----------------------|-------------------|
| **User** | Unique username, password hash, role, optional email + verification flags if functional email flow is implemented. |
| **Session** | FK to user, expiry, revocation timestamp. |
| **ContentItem** | FK to author; brief fields; generated text fields (title, description, synopsis optional, story); optional binary **thumbnail** + MIME; optional binary **audio** + MIME + voice metadata; **status** string for pipeline stage; timestamps. |
| **ModelCall** (or equivalent) | Acting user, operation class, model name, success flag, latency, token counts if available, error classification, timestamp; optional link to a **generation run** record if multi-step flows are implemented. |
| **GenerationRun / events** (optional but recommended if guardrails exist) | Tie multiple attempts and guardrail passes to one logical “run” for support. |
| **AuditEvent** (optional) | Structured security/ops events if business requires richer forensics. |

Exact column names and indexes are **implementation choices**; relationships above are **normative intent**.

---

## 8. AI integration

| ID | Requirement |
|----|-------------|
| AI-1 | All model calls MUST go through **shared client configuration** (API key from environment, timeouts, consistent user-agent metadata if applicable). |
| AI-2 | **Retries** SHOULD be applied for transient provider errors with **caps**; non-retryable errors MUST surface cleanly to the route layer. |
| AI-3 | **Model names** and modality-specific options (embedding model, image model, TTS voice defaults) MUST be **environment-driven** for pilot flexibility. |
| AI-4 | **Logging** of each call to durable storage is **required** for operational maturity (see business goals). |

---

## 9. Semantic index and search

| ID | Requirement |
|----|-------------|
| SEM-1 | Embedding vectors MUST be computed with a **documented embedding model** consistent across index and query. |
| SEM-2 | Vector store document IDs MUST be **deterministic** enough to **upsert** and **delete** when content changes (e.g. stable primary keys from relational data). |
| SEM-3 | **Author-role** callers MUST NOT obtain **cross-author** hits from any semantic path. **Admin** semantic investigation (including natural-language composed queries) MUST require **admin** authorization and MUST remain on **admin** routes/tools. **Shipped author UX** does not include a dedicated author-library semantic search screen. |

---

## 10. Media (thumbnail and audio)

| ID | Requirement |
|----|-------------|
| MED-1 | Generated binaries SHOULD be stored **in-database** for pilot simplicity **or** in object storage if engineering prefers — choice MUST be documented and migration path understood. |
| MED-2 | MIME types MUST be stored alongside blobs for correct HTTP `Content-Type` when served. |
| MED-3 | Media endpoints MUST enforce the **same ownership** rules as the parent content item. |

---

## 11. Security, headers, and CORS

| ID | Requirement |
|----|-------------|
| OPS-1 | Production configuration SHOULD enable **security headers** appropriate for an API behind HTTPS. |
| OPS-2 | **CORS** MUST restrict origins in production; local development MAY allow localhost origins via configuration. |
| OPS-3 | Dangerous admin operations MUST be **feature-flagged off** by default (environment explicit opt-in). |

---

## 12. Observability and health

| ID | Requirement |
|----|-------------|
| OBS-1 | **Health** endpoints SHOULD exist for load balancers (liveness) and MAY aggregate dependency checks in non-production. |
| OBS-2 | Structured **application logging** (level configurable) SHOULD include **request correlation** where feasible. |

---

## 13. Configuration (environment variables — categories)

Engineering MUST supply `.env.example` documenting categories such as:

- **HTTP / app**: host, port, environment name, CORS allowlist.
- **Database**: SQLite file path (or URL if changed later).
- **Sessions**: cookie name, TTL, secure flag, SameSite policy.
- **Auth security**: rate limit, lockout thresholds.
- **AI provider**: API key, default chat model, embedding model, image model, TTS model/voices.
- **Vector store**: filesystem path for embedded store.
- **Admin**: bootstrap credentials, feature flags for destructive tools.
- **Email** (if implemented): SMTP or provider settings, token TTLs.

Exact variable names are **implementation details** but MUST appear in `.env.example` with **safe placeholders**.

---

## 14. Testing and quality gates

| ID | Requirement |
|----|-------------|
| QA-1 | Backend MUST have automated tests for: **happy path** per major route group, **401** without session, and **ownership denial** for at least one author-owned resource type. |
| QA-2 | Frontend SHOULD test: **submit success**, **validation failure**, and **loading/error** states for at least the generation flow per `FUNCTIONAL_REQS.md` and **`designs/`**. |
| QA-3 | Linting MUST be clean for changed code before merge (project-specific tools: e.g. Ruff, ESLint). |

---

## 15. Deployment assumptions (pilot)

| ID | Requirement |
|----|-------------|
| DEP-1 | Initial target is **single-node** deployment with HTTPS terminated at a reverse proxy or platform edge. |
| DEP-2 | SQLite and on-disk vector paths MUST reside on **durable volumes** if containerized. |

---

## 16. Non-binding examples (illustrative only)

The following are **not** normative path names — they illustrate grouping:

- Author REST resources under a prefix such as `/api/...` for **content**, **generation actions**, **media**, **indexing** (embedding upkeep for downstream investigation).
- Admin REST resources under `/api/admin/...` for **metrics**, **model-call listings**, **read-only content inspection**, **NLP query** (metrics / semantic composition).

Engineering chooses final routes and OpenAPI tags.

---

## 17. Revision history

| Version | Date | Notes |
|---------|------|-------|
| 0.1 | — | Initial technical requirements for greenfield build. |
| 0.2 | — | Renamed file to `TECHNICAL_REQS.md` (naming convention). |
