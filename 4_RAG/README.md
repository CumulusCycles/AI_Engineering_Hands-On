# RAG: Retrieval-Augmented Generation

Content for building RAG systems: retrieve relevant context, then generate answers with an LLM.

## Overview

**RAG** combines retrieval (e.g. vector search over your documents) with generation (LLM answers using that context). It reduces hallucination and keeps answers grounded in your data.

**Pipeline:** Documents → Chunk → Embed → Store (e.g. ChromaDB) → User question → Embed → Retrieve top-k → Build prompt (context + question) → LLM → Answer.

## Layout

```
4_RAG/
├── README.md
├── data/
│   └── AI_Agent_Insure.md    # sample document
└── demo/
    ├── .env.example           # copy to .env, add OPENAI_API_KEY
    ├── requirements.txt       # openai, chromadb, jupyterlab, python-dotenv, tiktoken
    ├── rag_utils.py           # load_document, chunk_*, embed, build_index
    ├── 1_Why_and_Pipeline.ipynb
    └── 2_RAG_Examples.ipynb
```

## What's Here

- **Shared code:** `demo/rag_utils.py` — `load_document`, `chunk_by_sentences`, `chunk_by_tokens`, `embed`, `build_index`. No duplicate setup in notebooks.
- **Notebook 1 — Why and pipeline:** Why RAG (no context vs with context), then one end-to-end pipeline (load → chunk → embed → store → retrieve → generate).
- **Notebook 2 — RAG examples:** Product Q&A, answers with citations, different question types; chunking (sentence vs token); when to evaluate retrieval.

**Data:** `data/AI_Agent_Insure.md`. Run Jupyter from the **4_RAG** directory so `rag_utils` can resolve `data/` (and so `load_dotenv()` finds `.env` if you put it in `4_RAG/`).

## Prerequisites

- Python 3.12+
- OpenAI API key in `.env` as `OPENAI_API_KEY`
- Optional: `uv` for venv and installs

## Setup

```bash
cd 4_RAG
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r demo/requirements.txt
```

Add your API key:

- **Option A:** `cp demo/.env.example demo/.env` and edit `demo/.env`, then start Jupyter from `demo/` so the kernel sees it.
- **Option B:** Create `4_RAG/.env` with `OPENAI_API_KEY=...` and start Jupyter from `4_RAG` (recommended so `data/` and `demo/` paths work).

## Run

```bash
# From 4_RAG (recommended)
uv run jupyter lab demo/
# Run 1_Why_and_Pipeline.ipynb then 2_RAG_Examples.ipynb
```

## Cost

Notebooks use `text-embedding-3-small` and `gpt-4o-mini`. Running both is in the **low cents** range.
