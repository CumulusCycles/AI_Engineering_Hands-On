# App

Streamlit agent app with a question input and an expandable trace panel showing every tool call the agent made.

## Setup

From this folder:

```bash
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Add your API key:

```bash
cp .env.example .env
# edit .env and replace the placeholder with your key
```

## Launch

```bash
source .venv/bin/activate
streamlit run agent_app.py
```

## Testing

Use these questions in order — each one exercises a different routing path:

| Question | Expected tool(s) |
|---|---|
| "What does Agentic AI Liability Insurance cover?" | `get_product_info` |
| "How much would Model & Data Security Insurance cost for a startup?" | `get_pricing_estimate` |
| "Can a healthcare company get coverage?" | `check_eligibility` |
| "How does AI Agent Insure handle claims and incident response?" | `search_docs` |
| "Explain AI Agent Insure's underwriting philosophy and tell me what Compliance & Regulatory Shield would cost for an enterprise." | `search_docs` + `get_pricing_estimate` |
| "What is AI Agent Insure?" | *(no tool — answered from system prompt)* |

Check the **Agent trace** expander below each answer — it should show the tool name, arguments, and result for every step. The last question should show "No tools were called."
