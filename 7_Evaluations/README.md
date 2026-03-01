# Evaluations: Measuring What You've Built

This module introduces systematic evaluation for the RAG pipelines and agent from modules 4–6. It replaces "looks right to me" with a repeatable, automatable signal you can run before and after any change.

## The Core Idea

Every module so far builds something and eyeballs whether it works. That's fine for learning. It breaks down when you have 50 test cases, when you change a prompt and need to know if anything regressed, or when you're comparing two chunking strategies.

**Evaluations replace intuition with a repeatable signal.**

## What's New Here vs the Agent Module

| | Agents (module 6) | Evaluations (this module) |
|---|---|---|
| How you know it works | Run it, read the output | Scored against a golden dataset |
| Failure visibility | Final answer only | Retrieval, generation, and routing measured separately |
| Regression detection | Manual re-check | Run the eval suite before/after any change |
| Comparison | Subjective | Objective scores across strategies |

---

## Layout

```
7_Evaluations/
├── README.md
├── data/
│   ├── AI_Agent_Insure.md        # same document as modules 4–6
│   └── golden_dataset.json       # ground truth — edit this file directly
└── notebooks/
    ├── .env.example
    ├── requirements.txt
    ├── 1_Golden_Dataset.ipynb    # introduces golden datasets and failure modes
    ├── 2_Retrieval_Eval.ipynb    # precision@k, recall@k, MRR
    ├── 3_Generation_Eval.ipynb   # semantic similarity + LLM-as-judge
    └── 4_Agent_Eval.ipynb        # tool routing accuracy + end-to-end quality
```

---

## What's in Each File

### `notebooks/1_Golden_Dataset.ipynb` — Ground truth

**The foundation.** Everything else depends on this.

1. Introduces the four failure modes: bad retrieval, bad generation, bad grounding, bad routing
2. Builds the RAG index (same sentence-chunking + ChromaDB pattern as modules 4–6)
3. Prints every chunk with its ID so you can identify `relevant_chunk_ids` for each question
4. Loads `data/golden_dataset.json` and inspects it by category
5. Explains what makes a good golden dataset (coverage, verified answers, realistic questions)

**Key concept:** The golden dataset is created by hand — questions and expected answers are written and verified by you against the source document, then stored in `data/golden_dataset.json`. Edit that file directly to add questions, fill in `relevant_chunk_ids`, or correct an answer. If you ask the model to generate its own test cases, you're measuring self-consistency, not correctness.

---

### `notebooks/2_Retrieval_Eval.ipynb` — Retrieval layer

**Evaluate retrieval in isolation, before the LLM ever sees the context.**

Metrics:
- **Precision@k** — of the top-k chunks returned, what fraction are actually relevant?
- **Recall@k** — of all relevant chunks, what fraction did we retrieve?
- **MRR (Mean Reciprocal Rank)** — how high up is the first relevant chunk?

1. Load the golden dataset and build the index
2. Implement and explain each metric
3. Run eval at k=5 across all retrieval cases
4. Compare sentence chunking vs. token-window chunking on the same queries

**Key concept:** Retrieval evaluation requires no LLM — it's set intersection math. You can swap the LLM out entirely and still know if retrieval improved.

---

### `notebooks/3_Generation_Eval.ipynb` — Generation layer

**Evaluate the generated answer — two ways.**

**Method 1: Semantic similarity (reference-based)**
- Embed both the model's answer and the expected answer
- Compute cosine similarity
- No LLM needed for scoring — fast and cheap
- Best for: regression testing (did this prompt change break anything?)

**Method 2: LLM-as-judge (reference-free)**
- Send question + retrieved context + answer to a second LLM call
- Ask it to score **faithfulness** (is the answer grounded in the context?) and **relevance** (does it answer the question?) on a 1–5 scale
- Uses structured output (JSON mode) so scores are always machine-readable
- Best for: production monitoring, understanding *why* something regressed

Also covers the four LLM-as-judge failure modes: sycophancy, position bias, verbosity bias, self-consistency.

---

### `notebooks/4_Agent_Eval.ipynb` — Agent layer

**Evaluate the full agent from Module 6 across three dimensions.**

1. **Tool routing accuracy** — did the agent call the right tools? Measured as F1 over the tool sets (expected vs. actual)
2. **End-to-end answer quality** — is the final answer correct? Measured with semantic similarity
3. **Failure diagnosis** — when routing and E2E disagree, that tells you *where* the failure is

| Routing | E2E | Diagnosis |
|---|---|---|
| ✓ | ✓ | Pass |
| ✓ | ✗ | Generation failure — fix the prompt or generation step |
| ✗ | ✓ | Routing miss, got lucky — fix routing before harder cases expose it |
| ✗ | ✗ | Fix routing first, then re-evaluate generation |

**Key concept:** End-to-end alone can mask routing problems. Measuring each layer separately tells you where to fix things.

---

## Prerequisites

**Watch first:** Before working through this module, watch [Build An AI Agent from Scratch](https://youtu.be/t0V9MMQXzrw) (Module 6 — Agents). Notebook 4 evaluates the agent built there, and the retrieval and generation patterns from modules 4–5 are assumed knowledge throughout.

- Python 3.12+
- OpenAI API key
- `uv` for environment management
- Module 6 (`6_Agents/`) must be present — the agent eval imports `tools/` from it

---

## Setup — Notebooks

```bash
cd 7_Evaluations/notebooks
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Register the venv as a Jupyter kernel:

```bash
python -m ipykernel install --user --name evals-notebooks --display-name "Evaluations (notebooks)"
```

Add your API key:

```bash
cp .env.example .env
# then edit .env and replace the placeholder with your key
```

```bash
uv run jupyter lab
```

When a notebook opens, select **Evaluations (notebooks)** from the kernel selector in the top-right.

Before running the notebooks, fill in `relevant_chunk_ids` in `data/golden_dataset.json`:
1. Run `1_Golden_Dataset.ipynb` — prints every chunk with its ID; use the output to identify which chunk IDs belong to each question, then edit `data/golden_dataset.json` directly
2. Run `2_Retrieval_Eval.ipynb` — requires `relevant_chunk_ids` to be filled in
3. Run `3_Generation_Eval.ipynb`
4. Run `4_Agent_Eval.ipynb`

---

## Cost

All notebooks use `gpt-4o-mini` and `text-embedding-3-small`. The LLM-as-judge eval makes one extra API call per golden dataset entry. Running all four notebooks against a 10-question golden dataset is in the **low cents** range.

---

## How This Connects to the Rest of the Series

```
4_RAG       → RAG pipeline (the system being evaluated)
5_RAG_App   → RAG packaged as an app
6_Agents    → Agent loop with tool routing
7_Evals     → Measure all of the above; catch regressions before they ship
```

The `AI_Agent_Insure.md` document, sentence-chunking, ChromaDB, and the agent tools all carry over directly. The new concepts are: golden datasets, retrieval metrics, LLM-as-judge, and the diagnostic pattern of measuring each layer separately.
