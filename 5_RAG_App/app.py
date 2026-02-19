"""
RAG app: ask questions over data/*.md. Sentence chunking, top-8 retrieval, one index.
Run from 5_RAG_App: streamlit run app.py
"""
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
DATA_DIR = Path(__file__).resolve().parent / "data"
TOP_K = 8
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


def load_documents() -> str:
    """Load and concatenate all .md files in data/."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files in {DATA_DIR}")
    parts = []
    for p in md_files:
        parts.append(p.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts)


def chunk_by_sentences(doc: str) -> list[str]:
    chunks = [s.strip() for s in doc.replace("\n", " ").split(".") if s.strip()]
    return [c + "." for c in chunks]


# Build the ChromaDB index once per session; Streamlit won't re-run this on every interaction.
@st.cache_resource
def build_index():
    """Build ChromaDB index from data/*.md (cached per session)."""
    client_openai = OpenAI()
    doc = load_documents()
    chunks = chunk_by_sentences(doc)

    resp = client_openai.embeddings.create(model=EMBEDDING_MODEL, input=chunks)
    embeddings = [r.embedding for r in resp.data]
    ids = [str(i) for i in range(len(chunks))]

    chroma_client = chromadb.EphemeralClient()
    coll = chroma_client.create_collection("rag", metadata={"description": "RAG app"})
    coll.add(ids=ids, embeddings=embeddings, documents=chunks)
    return coll, client_openai, chunks


def answer_from_context(context: str, question: str, client: OpenAI) -> str:
    prompt = f"""Use only the following context to answer the question. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return r.choices[0].message.content


def main():
    st.set_page_config(page_title="RAG Q&A", page_icon="📄")
    st.title("RAG Q&A")
    st.caption(f"Questions over documents in `data/`. Sentence chunking, top-{TOP_K} retrieval.")

    try:
        coll, client_openai, all_chunks = build_index()
    except FileNotFoundError as e:
        st.error(str(e))
        return
    st.sidebar.metric("Chunks indexed", len(all_chunks))

    question = st.text_input("Ask a question", placeholder="e.g. What products does AI Agent Insure offer?")
    if not question.strip():
        return

    if st.button("Ask"):
        with st.spinner("Retrieving and generating..."):
            q_emb = client_openai.embeddings.create(model=EMBEDDING_MODEL, input=[question])
            q_vec = q_emb.data[0].embedding
            results = coll.query(query_embeddings=[q_vec], n_results=TOP_K)
            retrieved = results["documents"][0]
            retrieved_ids = results["ids"][0]
            context = "\n".join(retrieved)
            answer = answer_from_context(context, question, client_openai)

        st.subheader("Answer")
        st.markdown(answer)
        with st.expander("Sources (retrieved chunks)"):
            for i, (cid, doc) in enumerate(zip(retrieved_ids, retrieved)):
                st.markdown(f"**Chunk {cid}**")
                st.text(doc[:500] + ("..." if len(doc) > 500 else ""))
                st.divider()


if __name__ == "__main__":
    main()
