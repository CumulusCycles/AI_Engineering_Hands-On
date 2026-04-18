# Postman collections

## ScriptSprout API

- **File:** [`ScriptSprout.postman_collection.json`](ScriptSprout.postman_collection.json) — bump **`info.version`** when you materially change requests or tests (current **v1.33.0**).
- **Purpose:** Mirror FastAPI routes for demos (Swagger + Postman) and quick regression checks.

## Maintainer convention

Whenever routes are **added, removed, or meaningfully changed** in `backend/app/`:

1. Update this collection in the **same** change.
2. **Extend `backend/tests/`** (pytest) so HTTP behavior stays covered.

## Import and `baseUrl`

- In Postman: **Import → File** → select `ScriptSprout.postman_collection.json`.
- Set the **`baseUrl`** collection variable if the API is not on `http://127.0.0.1:8000`.

## Newman (`test-scripts/test-postman.sh`)

Run from **`ScriptSprout/`** (parent of `backend/`): [`../../test-scripts/test-postman.sh`](../../test-scripts/test-postman.sh).

**Default folders** (author-session workflow, in order):

| # | Folder |
|---|--------|
| 1 | `Auth` |
| 2 | `NLP extract` |
| 3 | `Content` |
| 4 | `Synopsis` |
| 5 | `Title + Description` |
| 6 | `Story` |
| 7 | `Thumbnail` |
| 8 | `Audio` |
| 9 | `Media` |
| 10 | `Semantic index` |
| 11 | `Semantic search` |

**Optional admin smoke** (adds `Admin / RBAC` and `Admin metrics`):

```bash
POSTMAN_INCLUDE_ADMIN_SMOKE=1 ./test-scripts/test-postman.sh
```

Uses seeded admin **`seedadmin` / `seedpassword123`** unless you set **`POSTMAN_ADMIN_USERNAME`** and **`POSTMAN_ADMIN_PASSWORD`**.

## Manual-only (not in default Newman pass)

These requests exist in the collection but are **not** selected by the default `test-postman.sh` folder list. **Admin NLP query** is the same: run it manually (playbook at the end of this file).

### Meta and introspection

- **`GET /health`**, **`GET /openapi.json`**
- **`GET /api/meta/db-status`**, **`GET /api/meta/chroma-status`** — **200** only if **`EXPOSE_META_WITHOUT_AUTH=true`** in the API `.env`; otherwise **404**. Newman meta tests accept **200 or 404**.
- After a successful **`POST /api/content/{id}/semantic-index`** with **`OPENAI_API_KEY`**, **`document_count`** (where exposed) can increase.

### Generation runs

- **`GET /api/admin/generation-runs/{{generationRunId}}`** — ordered guardrails events for a run.
- Set **`generationRunId`** by running **`Story`** with a **live** OpenAI key so the request returns **200** and the collection stores the id.

---

## Folder playbooks

### Auth

**Order** (populates the cookie jar):

1. **register**
2. **email-verification/request**
3. **email-verification/confirm**
4. **login**
5. **me**
6. **logout**

**Collection variables:** change **`authUsername`**, **`authPassword`**, **`authEmail`** for a fresh user (or pick a new username after **409** on duplicate register).

**Limits and passwords**

- Auth routes are rate-limited (default **5 req/min per IP**; **`AUTH_RATE_LIMIT`**).
- Author passwords: **≥8** characters with uppercase, lowercase, and a digit.
- Lockout: **5** failed logins → **15** minutes (**`MAX_FAILED_LOGINS`**, **`ACCOUNT_LOCKOUT_MINUTES`**).
- Session cookie **`Secure`** defaults to **`true`** — use **`SESSION_COOKIE_SECURE=false`** for local HTTP.

**Tokens**

- **`POST /api/auth/register`** does **not** return a verification token.
- **`POST /api/auth/email-verification/request`** returns **`preview_token`** — copy it to **`verificationToken`** before **email-verification/confirm** (or read from logs). In production email flows you would normally not return this in the API.
- **`PUT /api/auth/email`** can also return **`preview_token`** when re-verification is required.

**Admin seed:** **`ADMIN_PASSWORD`** must be **≥12** characters (with **`ADMIN_USERNAME`**).

### Content

With an **author** session:

1. **`POST /api/content/`** with **`prompt`** → saves **`contentId`**
2. **`GET /api/content/`** → **`ContentListPage`** (`items`, `total`, `limit`, `offset`); optional **`?status=draft`**
3. **`GET /api/content/{{contentId}}`** → **`ContentItemDetail`**

Start from **POST login (author)** in the folder, or complete **Auth** (register + login) first.

### Synopsis

Author session; **`contentId`** set:

1. **`POST /api/content/{{contentId}}/generate-synopsis`**
2. **`POST /api/content/{{contentId}}/approve-step`** with `{"step":"synopsis"}` (optional **`regenerate-step`**)

Needs **`OPENAI_API_KEY`**; otherwise **503** on generate, **400** on approve if no synopsis yet.

### Title + Description

After synopsis is approved:

1. **`POST /api/content/{{contentId}}/generate-title`** → **`approve-step`** `{"step":"title"}`
2. **`POST /api/content/{{contentId}}/generate-description`** → **`approve-step`** `{"step":"description"}`

Optional **`regenerate-step`** for title/description.

### Audio

Author session + story exists:

- **`POST /api/content/{{contentId}}/generate-audio`** with optional **`voice_key`**: `female_us`, `female_uk`, `male_us`, `male_uk`
- Needs **`OPENAI_API_KEY`**; safe mode usually **503**

### Media

After assets exist:

- **`GET /api/content/{{contentId}}/thumbnail`** and **`GET /api/content/{{contentId}}/audio`** — raw bytes **200**, or **404** if not generated.

### Semantic index

1. Author **login**
2. Content with non-empty **`title`**, **`description`**, **`story_text`** (see folder’s **`POST /api/content/`** example)
3. **`POST /api/content/{{contentId}}/semantic-index`**

With key: **200** + **`UpsertSemanticIndexResponse`**. Safe mode / Newman often **503**. Embeddings: **`OPENAI_EMBEDDING_MODEL`** (default **`text-embedding-3-small`**).

### Semantic search

1. Author **login**
2. **`POST /api/search/semantic`** with **`query`**; optional **`limit`**, **`genre`**, **`status`**

Empty index: **200** with empty **`items`** (no key required). Indexed docs but no key: **503**.

### NLP extract

1. Author **login**
2. **`POST /api/nlp/extract-story-parameters`**

Response includes **`follow_up`** (per **`missing_fields`**: `question`, `input_kind`, optional `suggested_options`). Needs **`OPENAI_API_KEY`**; optional **`OPENAI_NLP_MODEL`**. Admins get **403**.

### Admin content

Admin session:

1. **`GET /api/admin/content/`** → **`AdminContentListPage`**
2. **`GET /api/admin/content/{{adminContentId}}`** — **404** if id missing

Folder tests may set **`adminContentId`** from the first list hit; run **Content** first if the list is empty.

### OpenAI smoke + model_calls

Admin folder login, then:

1. **`POST /api/admin/openai/smoke`**
2. **`GET /api/admin/model-calls/`**

With **`OPENAI_API_KEY`**: smoke **200**, **`attempts_used`** (often **1**, **2** if retried), **`OpenAiSmokeResponse`** fields; each SDK attempt stored in **`model_calls`**. **`TRANSIENT_RETRY_MAX_ATTEMPTS`** (default **2**). No key: **503**. Tests may allow **502**. List response: **`ModelCallListPage`** (`items`, `total`, `limit`, `offset`).

### Admin / RBAC

Set **`adminUsername`** / **`adminPassword`** to match **`ADMIN_USERNAME`** / **`ADMIN_PASSWORD`** in `.env`, then in order:

1. **login (admin)** → **`GET /api/admin/ping`** (**200**)
2. **logout**
3. **login (author)** → **`GET /api/admin/ping`** (**403**)

Author login expects **`authUsername`** already registered (**Auth → register** if needed).

### Admin metrics

After **POST login (admin)** in that folder:

- **`GET /api/admin/metrics`** (default **7-day** window)
- **`GET /api/admin/metrics`** with **`start`** / **`end`** query params

Expect **200** + **`AdminMetricsResponse`**. Only included when **`POSTMAN_INCLUDE_ADMIN_SMOKE=1 ./test-scripts/test-postman.sh`**.

### Admin NLP query

1. Admin **login**
2. **`POST /api/admin/nlp-query`** with `{"query":"…"}`

With **`OPENAI_API_KEY`**: **200** + **`AdminNlpQueryResponse`** (optional **`metrics`** / **`semantic_search`**); no key: **503**. Bad **`metrics_*_iso`** values from the model are ignored with a warning log; bad windows fall back like **`GET /api/admin/metrics`**. **Not** run by **`test-scripts/test-postman.sh`**.
