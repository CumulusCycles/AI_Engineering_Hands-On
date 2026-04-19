<table style="border: none; border-collapse: collapse;">
  <tr>
    <td style="border: none; padding: 0;">
      <img src="img/logo_transparent_sm.png" alt="Logo" width="200">
    </td>
    <td style="border: none; padding: 0;">
      <h1>AI Engineering Hands-On</h1>
      Repo for the AI Engineering Hands-On <a href="https://www.youtube.com/playlist?list=PLRBkbp6t5gM151rUSi6Z8T8n6UCppEEMH">Playlist</a>.
    </td>
  </tr>
</table>

## Table of Contents

- [Overview](#overview)
- [Companion Videos](#companion-videos)
- [Dev Environment Config](#dev-environment-config)
- [1 — Large Language Models](#1--large-language-models)
- [2 — LLM Demo Apps](#2--llm-demo-apps)
- [3 — Prompt Engineering](#3--prompt-engineering)
- [4 — RAG](#4--rag)
- [5 — RAG App](#5--rag-app)
- [6 — Agents](#6--agents)
- [7 — Evaluations](#7--evaluations)
- [8 — OpenAI API](#8--openai-api)
- [9 — AI Workflows](#9--ai-workflows)
- [10 — AI Workflow App](#10--ai-workflow-app)

## Overview

| Module | Description |
|--------|-------------|
| [0_Dev_Env_Config](0_Dev_Env_Config/) | Dev environment setup: uv, venv, OpenAI & Ollama demos. |
| [1_LLMs](1_LLMs/) | What LLMs are, how they work; notebooks on pipeline, OpenAI API, Ollama. |
| [2_LLM_Demo_App](2_LLM_Demo_App/) | Full-stack semantic search app (FastAPI + React): text/image search, ChromaDB, pipeline demo. |
| [2_LLM_Demo_App_v2](2_LLM_Demo_App_v2/) | Same idea with decoupled backend (FastAPI) and frontend (Streamlit) over HTTP. |
| [3_Prompt_Engineering](3_Prompt_Engineering/) | Prompt engineering as runtime configuration: foundations, structure, structured outputs, advanced techniques. |
| [4_RAG](4_RAG/) | RAG: why + pipeline, then concrete examples (Q&A, citations, chunking, evaluation). |
| [5_RAG_App](5_RAG_App/) | Streamlit app: Q&A over `data/*.md` (sentence chunking, top-8 retrieval). |
| [6_Agents](6_Agents/) | Function calling, agent loops, RAG as a tool, and a Streamlit agent app with visible reasoning traces. |
| [7_Evaluations](7_Evaluations/) | Golden datasets, retrieval metrics (precision@k, MRR), LLM-as-judge, and agent routing eval. |
| [8_OpenAI_API](8_OpenAI_API/) | OpenAI Responses API demos: structured outputs with Pydantic, and stateless vs stateful conversation with a local Ollama model. |
| [9_AI_Workflows](9_AI_Workflows/) | **Video Content Generator** CLI (chapter folder + `src/` package): narration pipeline with Pydantic, modular layers, API retries, multi-draft guardrail correction, and safe output folders. |
| [10_AI_Workflow_App](10_AI_Workflow_App/) | **ScriptSprout** — full-stack web app (FastAPI + React): same narration workflow ideas as chapter 9, with persistence, HITL in the UI, semantic search, and admin tooling. Docs: [10_AI_Workflow_App/README.md](10_AI_Workflow_App/README.md) (runnable app in [`ScriptSprout/`](10_AI_Workflow_App/ScriptSprout/)). |

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## Companion Videos

- [Intro](https://youtu.be/HaXveXkSwlQ)
- [Dev Environment Config](https://youtu.be/36sbUO2LaOk)
- [LLMs](https://youtu.be/seFjZz08KSw)

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## Dev Environment Config
Links to resources discussed in the [Dev Environment Config](https://youtu.be/36sbUO2LaOk) video.

### Links
- [Homebrew](https://brew.sh/)
- [Python](https://www.python.org/downloads/)
- [Cursor](https://cursor.com/home?from=agents)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Ollama](https://ollama.com/)
- [llama3.2](https://ollama.com/library/llama3.2)
- [Postman](https://www.postman.com/downloads/)
- [OpenAI](https://openai.com/index/openai-api/)

### Commands
Commands executed in Terminal in the [Dev Environment Config](https://youtu.be/36sbUO2LaOk) video.

#### uv
```bash
uv --version
uv run --python 3.12 python --version
uv python install 3.12

ls -al
uv venv --python python3.12
source .venv/bin/activate

uv pip list
uv pip install jupyterlab
uv pip list
uv run --with jupyter jupyterlab

deactivate
```

#### Ollama
```bash
ollama list
pgrep ollama

ollama pull llama3.2:3b
ollama run llama3.2:3b
Who are you?
/bye

pgrep ollama

ollama serve
pgrep ollam

pkill ollama
pgrep ollama
```

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 1 — Large Language Models

[**1_LLMs/**](1_LLMs/) — What LLMs are and how they work; hands-on with APIs.

- **Notebooks:** LLM pipeline (tokenization, embeddings, attention), OpenAI Chat Completions, Ollama + OpenAI-compatible API.
- **Docs:** LLM overview, frontier vs open-source, Chat Completions API.
- See [1_LLMs/README.md](1_LLMs/README.md) and [1_LLMs/demo/README.md](1_LLMs/demo/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 2 — LLM Demo Apps

Two app variants that demonstrate semantic search and the LLM pipeline.

- **[2_LLM_Demo_App/](2_LLM_Demo_App/)** — Outdoor gear catalog: FastAPI backend, React frontend, text + image search, ChromaDB, pipeline demo. Run `./deploy.sh` then seed; frontend :3000, backend :8000.
- **[2_LLM_Demo_App_v2/](2_LLM_Demo_App_v2/)** — Same concepts with a decoupled architecture: FastAPI backend and Streamlit frontend communicate over HTTP for easier deployment and scaling.

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 3 — Prompt Engineering

[**3_Prompt_Engineering/**](3_Prompt_Engineering/) — Controlling LLM behavior through prompt design.

- **Notebooks:** Foundations (roles, behavior spec), structure & constraints, structured outputs (JSON, Pydantic), advanced techniques (few-shot, chain-of-thought, chaining).
- Requires OpenAI API key (e.g. `gpt-4o-mini`). See [3_Prompt_Engineering/README.md](3_Prompt_Engineering/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 4 — RAG

[**4_RAG/**](4_RAG/) — Retrieval-Augmented Generation: retrieve context, then generate with an LLM.

- **Notebooks:** Why RAG + minimal pipeline; then RAG examples (product Q&A, citations, different questions, chunking, evaluation). Shared `demo/rag_utils.py`; data in `data/`.
- Run Jupyter from `4_RAG/`; notebooks use OpenAI. See [4_RAG/README.md](4_RAG/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 5 — RAG App

[**5_RAG_App/**](5_RAG_App/) — A single-scope Streamlit app: ask questions over all markdown files in `data/`. Sentence chunking, top-8 retrieval, answer + sources. No notebooks; run `streamlit run app.py` from `5_RAG_App/`. See [5_RAG_App/README.md](5_RAG_App/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 6 — Agents

[**6_Agents/**](6_Agents/) — AI agents: the LLM decides what to do, not just what to say.

- **Notebooks:** Manual function calling walkthrough, automated agent loop (`run_agent()`), RAG as a tool alongside structured lookups.
- **App:** Streamlit agent app with an expandable trace panel showing every tool call, argument, and result.
- Shared `tools/` package (tool schemas + implementations) used by both notebooks and app. Requires OpenAI API key. See [6_Agents/README.md](6_Agents/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 7 — Evaluations

[**7_Evaluations/**](7_Evaluations/) — Systematic evaluation for the RAG pipelines and agent from modules 4–6.

- **Notebooks:** Golden dataset construction, retrieval eval (precision@k, recall@k, MRR), generation eval (semantic similarity + LLM-as-judge), agent eval (tool routing accuracy + end-to-end quality).
- **App:** Streamlit eval harness — select an eval type, run it against the golden dataset, get a scored results dashboard with per-case pass/fail.
- Reuses the `AI_Agent_Insure.md` document, ChromaDB index, and agent tools from modules 4–6. See [7_Evaluations/README.md](7_Evaluations/README.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 8 — OpenAI API

[**8_OpenAI_API/**](8_OpenAI_API/) — Focused demos of the OpenAI Responses API and conversation state.

- **[demo/](8_OpenAI_API/demo/)** — Structured output with `responses.parse`: prompts for a story, returns a `StoryResponse` Pydantic model (`title` + `story`). Demonstrates typed structured outputs from the Responses API.
- **[Stateless_demo/](8_OpenAI_API/Stateless_demo/)** — Two scripts using a local Ollama model via the OpenAI-compatible API (`http://localhost:11434/v1`). `stateless_demo.py` sends each turn independently (no memory); `stateful_demo.py` sends the full message history each turn. Side-by-side illustration of why conversation context matters.

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 9 — AI Workflows

[**9_AI_Workflows/**](9_AI_Workflows/) — A **Video Content Generator** CLI: synopsis, title, description, full story, guardrails check, and DALL·E 3 thumbnail using the OpenAI API. The project lives in **[`9_AI_Workflows/`](9_AI_Workflows/)** (run **`uv`** there); the Python package is under **`src/`** with Pydantic models, modular boundaries (`api`, `workflow`, `output_bundle`, `story`, etc.), **retries** on transient API errors, **multi-draft** story correction when guardrails fail, and **collision-safe** output folders. See [9_AI_Workflows/README.md](9_AI_Workflows/README.md) and [9_AI_Workflows/MODEL_USAGE_GUIDE.md](9_AI_Workflows/MODEL_USAGE_GUIDE.md).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>

## 10 — AI Workflow App

[**10_AI_Workflow_App/**](10_AI_Workflow_App/) — **ScriptSprout** in [`ScriptSprout/`](10_AI_Workflow_App/ScriptSprout/): the chapter 9 narration pipeline as a multi-user product (Vite + React, FastAPI, SQLite, ChromaDB, OpenAI). See [10_AI_Workflow_App/README.md](10_AI_Workflow_App/README.md), [10_AI_Workflow_App/ARCHITECTURE.md](10_AI_Workflow_App/ARCHITECTURE.md), and [10_AI_Workflow_App/architecture.html](10_AI_Workflow_App/architecture.html).

<p align="right"><a href="#table-of-contents" style="font-size: 0.85em;">↑ toc</a></p>
