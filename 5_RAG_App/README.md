# RAG App

A small Streamlit app that runs the RAG pipeline over the markdown files in `data/`. One scope: sentence chunking, top-8 retrieval, question → answer + sources.

## Scope

- **Data:** All `*.md` files in `data/` (loaded and concatenated).
- **Chunking:** Sentence-based.
- **Retrieval:** Top 8 chunks per question.
- **UI:** Question input → Answer + expandable "Sources" (retrieved chunks).

## Prerequisites

- Python 3.12+
- OpenAI API key in `.env` as `OPENAI_API_KEY`

## Setup

```bash
cd 5_RAG_App
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY
```

## Run

```bash
streamlit run app.py
```

Open the URL shown (default http://localhost:8501). The index is built once per session from `data/*.md`.
