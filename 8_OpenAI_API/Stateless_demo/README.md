# Stateless_demo

Two small scripts that call a **local Ollama** model through the OpenAI-compatible API (`http://localhost:11434/v1`). Same two-turn demo in both; the difference is whether prior messages are sent again.

## Prerequisites

- Ollama running: `ollama serve`
- Model available (default in the scripts): `ollama pull llama3.2:3b`

## Setup

```bash
pip install openai
```

## Scripts

| Script | Behavior |
|--------|----------|
| `stateless_demo.py` | Two separate requests. The second request only contains `What's my name?` — no earlier turns — so the model usually **cannot** know your name. |
| `stateful_demo.py` | Same user lines, but the second request includes the **full** `messages` list (earlier user + assistant + new user), so the model **can** answer. |

## Run

**Stateless**

```bash
python stateless_demo.py
```

**Stateful**

```bash
python stateful_demo.py
```

To use another Ollama model, change the `MODEL` constant at the top of each script (and `ollama pull` that tag).
