"""
agent_app.py — Streamlit agent app for the Agents module.

Same question interface as the RAG app (module 5), but the backend is now an
agent loop instead of a single RAG call.  The key UI addition is an expandable
"Agent trace" panel that shows every tool call the agent made — so you can see
the reasoning, not just the final answer.

Run from 6_Agents/app:
    streamlit run agent_app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# Add the 6_Agents root to sys.path so the shared tools package is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools import TOOL_SCHEMAS, TOOL_FUNCTIONS

load_dotenv()

MODEL           = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K           = 5
DATA_PATH       = Path(__file__).resolve().parent.parent / "data" / "AI_Agent_Insure.md"

SYSTEM_PROMPT = (
    "You are a helpful assistant for AI Agent Insure, a specialty insurer for "
    "AI systems, autonomous agents, and ML infrastructure. "
    "Use search_docs to look up detailed information from the company document. "
    "Use the other tools for structured lookups (product details, pricing, eligibility). "
    "Call as many tools as you need — do not guess when a tool can give you the answer."
)


# ---------------------------------------------------------------------------
# Build the RAG index once per session.
# @st.cache_resource prevents Streamlit from rebuilding the index on every
# user interaction — same pattern as the RAG app in module 5.
# ---------------------------------------------------------------------------
@st.cache_resource
def build_rag_index():
    """Load the company document, chunk it, embed it, and store in ChromaDB."""
    openai_client = OpenAI()

    doc = DATA_PATH.read_text(encoding="utf-8").strip()
    # Sentence chunking: split on periods, strip whitespace, re-add period.
    raw = [s.strip() for s in doc.replace("\n", " ").split(".") if s.strip()]
    chunks = [c + "." for c in raw]

    resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=chunks)
    embeddings = [r.embedding for r in resp.data]

    chroma = chromadb.EphemeralClient()
    coll = chroma.create_collection("agent_rag")
    coll.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks
    )
    return coll, openai_client, chunks


# ---------------------------------------------------------------------------
# search_docs tool — the RAG pipeline wrapped as an agent tool.
# This function is defined here (not in tools.py) because it needs access to
# the cached ChromaDB collection and OpenAI client.
# ---------------------------------------------------------------------------
def make_search_docs(coll, openai_client):
    """
    Factory that returns a search_docs function bound to the cached index and
    client.  We use a factory so the function can close over the cached objects
    without needing global state.
    """
    def search_docs(query: str) -> str:
        q_emb = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
        q_vec = q_emb.data[0].embedding
        results = coll.query(query_embeddings=[q_vec], n_results=TOP_K)
        retrieved = results["documents"][0]
        if not retrieved:
            return "No relevant content found in the document for that query."
        return "\n---\n".join(retrieved)
    return search_docs


SEARCH_DOCS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": (
            "Search the AI Agent Insure company document for detailed information. "
            "Use this for questions about company background, mission, operational model, "
            "claims process, strategic positioning, or anything not covered by the "
            "other structured tools."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to run against the company document."
                }
            },
            "required": ["query"]
        }
    }
}


# ---------------------------------------------------------------------------
# Agent loop — same logic as Notebook 2, returns both the answer and a trace
# list so the UI can display what the agent did.
# ---------------------------------------------------------------------------
def run_agent(user_question: str, all_schemas, all_functions, openai_client,
              max_iterations: int = 10):
    """
    Run the agent loop and return (final_answer, trace).

    trace is a list of dicts describing each tool call:
        {"tool": str, "args": dict, "result": str}
    This lets the Streamlit UI show the agent's reasoning in the trace panel.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_question}
    ]
    trace = []

    for _ in range(max_iterations):
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=all_schemas,
            tool_choice="auto",
            temperature=0
        )
        choice = response.choices[0]
        messages.append(choice.message)

        if choice.finish_reason == "stop":
            return choice.message.content, trace

        if choice.finish_reason == "tool_calls":
            for tc in choice.message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                result  = all_functions[fn_name](**fn_args)

                # Record the call in the trace for the UI.
                trace.append({"tool": fn_name, "args": fn_args, "result": result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

    return f"[Agent stopped after {max_iterations} iterations without a final answer]", trace


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="AI Agent Insure — Agent", page_icon="🤖")
    st.title("AI Agent Insure — Agent Assistant")
    st.caption(
        "Powered by an agent loop with 4 tools: product info, pricing, eligibility, and document search."
    )

    # Build the RAG index (cached — only runs once per session).
    try:
        coll, openai_client, chunks = build_rag_index()
    except FileNotFoundError:
        st.error(f"Data file not found: {DATA_PATH}")
        return

    # Wire up the full tool set: structured tools + RAG search.
    search_docs_fn = make_search_docs(coll, openai_client)
    all_schemas    = TOOL_SCHEMAS + [SEARCH_DOCS_SCHEMA]
    all_functions  = {**TOOL_FUNCTIONS, "search_docs": search_docs_fn}

    st.sidebar.metric("Chunks indexed", len(chunks))
    st.sidebar.markdown("**Available tools:**")
    for s in all_schemas:
        st.sidebar.markdown(f"- `{s['function']['name']}`")

    question = st.text_input(
        "Ask a question",
        placeholder="e.g. What would Agentic AI Liability Insurance cost for a startup?"
    )
    if not question.strip():
        return

    if st.button("Ask"):
        with st.spinner("Agent is thinking..."):
            answer, trace = run_agent(
                question, all_schemas, all_functions, openai_client
            )

        st.subheader("Answer")
        st.markdown(answer)

        # Show the agent trace so users can see which tools were called and why.
        # This is the key difference from the RAG app — the reasoning is visible.
        if trace:
            with st.expander(f"Agent trace ({len(trace)} tool call{'s' if len(trace) != 1 else ''})"):
                for i, step in enumerate(trace, 1):
                    st.markdown(f"**Step {i}: `{step['tool']}`**")
                    st.json(step["args"])
                    st.markdown("**Result:**")
                    # Truncate long RAG results in the UI — the full result was
                    # still sent to the model.
                    result_preview = step["result"]
                    if len(result_preview) > 600:
                        result_preview = result_preview[:600] + "\n\n*(truncated for display)*"
                    st.text(result_preview)
                    if i < len(trace):
                        st.divider()
        else:
            st.caption("No tools were called — the model answered from its system prompt.")


if __name__ == "__main__":
    main()
