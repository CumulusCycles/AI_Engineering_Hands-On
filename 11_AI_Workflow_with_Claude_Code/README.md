# Greenfield build with Claude Code

This folder is a **self-contained starting point** for implementing a full-stack web application **from prompts**, using **Claude Code** alongside the specifications and UI artifacts checked in here.

**What exists today:** only **`docs/`** (requirements and milestone slices) and **`designs/`** (visual source of truth: mockups, palette, brand assets). **Application source code is not part of this package**—you (or your audience) generate it in a working tree with Claude Code, guided by those documents.

There is **no** assumed prior codebase, sibling project, or external chapter to reconcile with. Treat everything under this directory as the **sole** specification set for the build.

---

## Goals

- **Ship in two beats:** first an **MVP** milestone (author auth, single-pass generation, history/detail, persistence, model-call logging), then **post-MVP enhancements** (regeneration, admin NLP/semantic tooling, thumbnails, audio, admin dashboard)—each mapped to the docs under `docs/mvp/` and `docs/enhancements/`.
- **Honor two contracts:** **`docs/`** for behavior, security, data rules, and architecture; **`designs/`** for layout, states, colors, and branding (with the conflict rule defined in [`designs/README.md`](designs/README.md): functional spec wins on security/data; designs win on pure visuals).
- **Use Claude Code deliberately:** small, verifiable steps; explicit file context in prompts; frequent test and lint runs; commits at natural boundaries—aligned with how teams ship **modern** web apps, not a single mega-prompt.

---

## What to read first

| Order | Path | Role |
|------:|------|------|
| 1 | [`docs/BUSINESS_REQS.md`](docs/BUSINESS_REQS.md) | Vision, personas, scope, business rules |
| 2 | [`docs/FUNCTIONAL_REQS.md`](docs/FUNCTIONAL_REQS.md) | Observable behavior, roles, journeys, acceptance-oriented requirements |
| 3 | [`docs/TECHNICAL_REQS.md`](docs/TECHNICAL_REQS.md) | Stack, layering, auth, APIs, data concepts, AI, testing, deployment |
| 4 | [`designs/README.md`](designs/README.md) | How to use mockups, palette, and brand assets |

**Milestone slices (do not skip the master trio above):**

| Milestone | Business | Functional | Technical |
|-----------|----------|------------|-----------|
| **MVP** | [`docs/mvp/MVP_BUSINESS_REQS.md`](docs/mvp/MVP_BUSINESS_REQS.md) | [`docs/mvp/MVP_FUNCTIONAL_REQS.md`](docs/mvp/MVP_FUNCTIONAL_REQS.md) | [`docs/mvp/MVP_TECH_REQS.md`](docs/mvp/MVP_TECH_REQS.md) |
| **Enhancements** | [`docs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md`](docs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md) | [`docs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`](docs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md) | [`docs/enhancements/ENHANCEMENTS_TECH_REQS.md`](docs/enhancements/ENHANCEMENTS_TECH_REQS.md) |

The MVP and enhancement files **point into** the master documents; they do not replace them. If anything disagrees, **the master `docs/*_REQS.md` files win**.

---

## Suggested workflow with Claude Code

1. **Bootstrap context** — In Claude Code, ground the session in the master trio plus [`designs/README.md`](designs/README.md). Prefer **attaching or referencing specific paths** over vague “build the app” prompts.
2. **MVP before enhancements** — Follow [`docs/mvp/`](docs/mvp/) as the first delivery slice; only then use [`docs/enhancements/`](docs/enhancements/) for the ordered enhancement tracks (E1–E5) described there.
3. **One capability at a time** — e.g. session + ownership guards before new surfaces; generation happy path before polish. After each step: **run tests/lint** (thresholds are in `TECHNICAL_REQS.md` §14 and the MVP/enhancement tech slices).
4. **UI work** — Open relevant files under [`designs/mockup-pages/`](designs/mockup-pages/) in a browser; mirror structure and states; follow [`designs/COLOR_PALETTE.md`](designs/COLOR_PALETTE.md) and [`designs/brand/`](designs/brand/) for visuals.
5. **Secrets and config** — Never commit API keys or real `.env` values. The technical requirements describe **categories** of configuration; mirror them in a root `.env.example` when you scaffold the repo.
6. **Teach / record clearly** — When producing a walkthrough, narrate **which doc** justified each prompt and how you **verified** the result (tests, manual check against a mockup, or both).

---

## Prerequisites (typical)

Details live in [`docs/TECHNICAL_REQS.md`](docs/TECHNICAL_REQS.md) (stack §2). At a high level you will need:

- **Claude Code** (or equivalent agentic coding workflow you standardize on for the recording)
- **Runtime tooling** consistent with the technical spec (e.g. Python and Node ecosystems as specified there)
- **Provider credentials** for AI and, in later milestones, embeddings/media APIs—via environment variables, not source control

---

## Repository layout (artifacts only)

```
docs/           # Business, functional, technical requirements + MVP / enhancement slices
designs/        # Mockups, CSS baseline, color palette, brand assets — UI contract
LICENSE         # License for materials in this folder
```

Generated application folders (for example `backend/` and `frontend/` as described in the MVP technical slice) appear **after** you begin implementation; they are not shipped as part of this artifact-only package.

---

## License

See [`LICENSE`](LICENSE).
