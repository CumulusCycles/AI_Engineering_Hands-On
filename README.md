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
