# Model and configuration reference

How environment variables map to OpenAI calls, how models are chosen, and how runs are written to disk and returned as JSON.

This document describes the **Video Content Generator** for **chapter 9**.

Paths like **`src/config.py`** in the **Code map** name files inside the **`src/`** package directory (mapped to import name **`video_content_generator`** in `pyproject.toml`). Use **`uv sync`** and **`uv run video-content-generator`** from the chapter directory **`9_AI_Workflows/`** (where `pyproject.toml` lives).

Configuration is loaded from the environment via `AppConfig.from_env()` in `src/config.py` (`python-dotenv` + `os.environ`). See [`.env.example`](.env.example).

---

## Environment variables

| Variable | Role |
|----------|------|
| `OPENAI_API_KEY` | Required. Not a model id. |
| `OUTPUT_DIR` | Base folder for each run (default **`output`**, relative to the current working directory unless absolute). Each run is a subfolder: **`<sanitized_title>_<MM-DD-YYYY>/`** (see [Output bundle](#output-bundle)). |
| `BASE_MODEL` | Default for synopsis/title/description chain fallbacks, story, and guard when those vars are unset. Code default **`gpt-5-nano`** if `BASE_MODEL` is empty. |
| `MODEL_SYNOPSIS` | Step 1: synopsis. Falls back to **`BASE_MODEL`**. |
| `MODEL_TITLE` | Step 2: title. Falls back to **`MODEL_SYNOPSIS`**. |
| `MODEL_DESCRIPTION` | Step 3: description. Falls back to **`MODEL_SYNOPSIS`**. |
| `MODEL_STORY` | Full story (Responses API). Recommended: **`gpt-4o-mini`**. Falls back to **`BASE_MODEL`** when unset. |
| `MODEL_STORY_GUARD` | Guardrails check on the story (**`responses.parse`** + structured JSON). Falls back to **`BASE_MODEL`** (not `MODEL_STORY`). Prefer a **different** id than `MODEL_STORY` to avoid self-review. |
| `MAX_STORY_GEN` | Max story **generation** attempts (initial + retries after a failed guard). Default **`2`** in code if unset/invalid; minimum **`1`**. `2` = one retry after a failed check. |
| `MODEL_THUMBNAIL_IMAGE` | Thumbnail image model for `images.generate`. Default **`gpt-image-1-mini`**. |
| `MODEL_THUMBNAIL_TEXT_CHECK` | Model for post-check text detection on generated thumbnails. Falls back to **`BASE_MODEL`** when unset. |
| `THUMBNAIL_SIZE` | GPT Image size (default **`1536x1024`**; also **`auto`**, **`1024x1024`**, **`1024x1536`**). |
| `THUMBNAIL_QUALITY` | GPT Image quality: **`auto`**, **`low`**, **`medium`**, or **`high`** (default **`low`**). |
| `MAX_THUMBNAIL_GEN` | Max thumbnail generation attempts when visible text is detected by a post-check model. Default **`2`** (initial + one retry). The final attempt is kept even if text remains. |

API method references:
- [Responses API — `responses.create`](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [Responses API — `responses.parse`](https://developers.openai.com/docs/guides/structured-outputs)
- [Images API — `images.generate`](https://developers.openai.com/api/reference/resources/images/methods/generate)

---

## How models resolve

1. **`BASE_MODEL`** — from env, or **`gpt-5-nano`**.
2. **`MODEL_SYNOPSIS`** — env, or **`BASE_MODEL`**.
3. **`MODEL_TITLE`** — env, or **`MODEL_SYNOPSIS`**.
4. **`MODEL_DESCRIPTION`** — env, or **`MODEL_SYNOPSIS`**.
5. **`MODEL_STORY`** — env (recommended **`gpt-4o-mini`**), or **`BASE_MODEL`**.
6. **`MODEL_STORY_GUARD`** — env, or **`BASE_MODEL`**.
7. **`MODEL_THUMBNAIL_TEXT_CHECK`** — env, or **`BASE_MODEL`**.

Thumbnail image settings (**`MODEL_THUMBNAIL_IMAGE`**, **`THUMBNAIL_SIZE`**, **`THUMBNAIL_QUALITY`**) do not use `BASE_MODEL`; they default as listed in the table.

---

## Suggested models (cost vs quality)

| Role | Env | Typical choice |
|------|-----|----------------|
| Short steps (default) | `BASE_MODEL` | **`gpt-5-nano`** |
| Full story | `MODEL_STORY` | **`gpt-4o-mini`** or **`gpt-5-mini`** |
| Guard check | `MODEL_STORY_GUARD` | **`gpt-5-nano`** (or unset → same as `BASE_MODEL`) — different from `MODEL_STORY` when possible |
| Thumbnail | `MODEL_THUMBNAIL_IMAGE` | **`gpt-image-1-mini`** (default) |
| Thumbnail text check | `MODEL_THUMBNAIL_TEXT_CHECK` | **`gpt-5-nano`** (or unset → same as `BASE_MODEL`) |

**Starter `.env` pattern:** `BASE_MODEL=gpt-5-nano`, `MODEL_STORY=gpt-4o-mini`, leave synopsis/title/description/guard/text-check unset so short steps, guard, and thumbnail text-check use nano while story uses mini.

---

## Pipeline and APIs

| Order | Step | API | Model env chain |
|-------|------|-----|-----------------|
| 1 | Synopsis | `responses.create` | `MODEL_SYNOPSIS` |
| 2 | Title | `responses.create` | `MODEL_TITLE` |
| 3 | Description | `responses.create` | `MODEL_DESCRIPTION` |
| 4 | Full story | `responses.create` | `MODEL_STORY` |
| — | Guardrails | `responses.parse` (structured) | `MODEL_STORY_GUARD` |
| — | Thumbnail PNG | `images.generate` | `MODEL_THUMBNAIL_IMAGE`, `THUMBNAIL_SIZE`, `THUMBNAIL_QUALITY` |
| — | Thumbnail text check | `responses.create` (vision input) | `MODEL_THUMBNAIL_TEXT_CHECK` (fallback `BASE_MODEL`) |
| — | Files + JSON | local | — |

The guard may rerun the story up to **`MAX_STORY_GEN`** times. If every draft fails the guardrails check, the run aborts with a **`GuardrailsViolation`** error and no output bundle is written. **Thumbnail generation runs only after the full story text has passed the guardrails check.** If an error is raised earlier—e.g. a rare API failure so text generation never completes—the Images API is not called. Thumbnail generation uses a post-check for visible text and can retry up to **`MAX_THUMBNAIL_GEN`** attempts (default **2**). The text-check uses **`MODEL_THUMBNAIL_TEXT_CHECK`** (fallback **`BASE_MODEL`**, default **`gpt-5-nano`** in `.env.example`) for cost efficiency. The final thumbnail attempt is kept even if visible text remains. Thumbnails are written to a temp file, then copied into the run folder as **`thumbnail.png`**.

All OpenAI API calls retry automatically on transient errors (`RateLimitError`, `APIConnectionError`, `APITimeoutError`, `InternalServerError`) with exponential backoff (up to 3 attempts).

---

## Output bundle

Under **`OUTPUT_DIR`** (default **`output/`** relative to the current working directory):

- Folder name: **`{sanitized_title}_{MM-DD-YYYY}`** (hyphenated date; slashes are not valid in path names). If the folder exists, a suffix **`_2`**, **`_3`**, … is used.
- **`STORY.md`** — title, description, and story body.
- **`thumbnail.png`** — if image generation succeeded.

Implementation: **`src/output_bundle.py`**.

---

## CLI / embed response

After a successful run, **`uv run video-content-generator`** prints **`WorkflowJSONResult`** as JSON to **stdout** (`title`, `description`, `story`, `story_md_path`, `thumbnail_path`).

To embed without the CLI, import from the package root:

```python
from video_content_generator import AppConfig, StoryParameters, run_workflow
```

Call `run_workflow(client, cfg, params, approve_fn)` directly. `cfg` is an **`AppConfig`** instance (use `AppConfig.from_env()` or construct one programmatically). `approve_fn` is a callback `(str) -> bool` — return `True` to accept the generated text, `False` to regenerate. The CLI wires this to an interactive terminal prompt; a UI can supply its own logic.

---

## Structured guard output

**`GuardrailsCheckResult`** (Pydantic) is the schema for **`responses.parse`** on the guard step. Prose steps use plain **`responses.create`**. Other Pydantic types: **`StoryParameters`**, **`ApprovedPipelineBundle`**. See **`src/schemas.py`**. **`UserQuit`** and **`GuardrailsViolation`** live in **`src/exceptions.py`**.

---

## Terminal output

Status and progress messages go to **stderr** (`Using model: …`, `Images API: …`, story attempts, guard retries, bundle directory). The final **`WorkflowJSONResult`** JSON goes to **stdout**, keeping it pipeable (`uv run video-content-generator | jq .`).

---

## Code map

| Module | Purpose |
|--------|---------|
| `src/__init__.py` | Package exports (`run_workflow`, `AppConfig`, …) and `__version__` |
| `src/config.py` | `AppConfig` frozen Pydantic model (`from_env()` factory) |
| `src/exceptions.py` | `UserQuit`, `GuardrailsViolation` exceptions |
| `src/prompts.py` | Instructions, step prompts, thumbnail prompt, guardrails text |
| `src/api.py` | `responses.create` / `parse`, `images.generate` |
| `src/story.py` | Story loop + guard |
| `src/workflow.py` | Orchestration, bundle + `WorkflowJSONResult` |
| `src/output_bundle.py` | Run folder + `STORY.md` + `thumbnail.png` |
| `src/schemas.py` | Pydantic models |
| `src/cli.py` | Terminal I/O, parameter collection, approval prompt, `main()` |
