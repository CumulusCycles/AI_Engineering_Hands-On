# Notebooks

Step-by-step walkthroughs of function calling, the agent loop, and RAG as a tool.

## Setup

From this folder:

```bash
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Register the venv as a Jupyter kernel so it appears in the kernel selector:

```bash
python -m ipykernel install --user --name agents-notebooks --display-name "Agents (notebooks)"
```

Add your API key:

```bash
cp .env.example .env
# edit .env and replace the placeholder with your key
```

## Launch

```bash
source .venv/bin/activate
jupyter lab
```

When a notebook opens, select **Agents (notebooks)** from the kernel selector in the top-right.

## Run Order

| Notebook | What it covers |
|---|---|
| `1_Function_Calling.ipynb` | Manual tool call walkthrough — every step explicit |
| `2_Agent_Loop.ipynb` | Automated `while` loop, multi-step reasoning |
| `3_Agent_App.ipynb` | RAG as a tool, four-tool agent |
