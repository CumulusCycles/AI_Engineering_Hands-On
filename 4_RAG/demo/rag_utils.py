"""
Shared utilities for RAG demos. Use from 4_RAG or 4_RAG/demo with 4_RAG as cwd.
"""
from pathlib import Path

# Resolve data path from 4_RAG or 4_RAG/demo
_DATA_FILE = "AI_Agent_Insure.md"
def _data_path() -> Path:
    for base in [Path("data"), Path("demo/data"), Path("../data")]:
        p = base / _DATA_FILE
        if p.exists():
            return p
    return Path("data") / _DATA_FILE  # default for error message


def load_document(path: Path | None = None) -> str:
    """Load the sample document. Uses path if given, else resolves data/AI_Agent_Insure.md."""
    p = path or _data_path()
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {p}. Run from 4_RAG with data/ present.")
    return p.read_text(encoding="utf-8").strip()


def chunk_by_sentences(doc: str) -> list[str]:
    """Split document into sentence-based chunks (period as separator)."""
    chunks = [s.strip() for s in doc.replace("\n", " ").split(".") if s.strip()]
    return [c + "." for c in chunks]


def chunk_by_tokens(doc: str, max_tokens: int = 80, overlap_tokens: int = 20) -> list[str]:
    """Split document into fixed-size token chunks with overlap. Requires tiktoken."""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(doc)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens).strip())
        start = end - overlap_tokens if end < len(tokens) else len(tokens)
    return [c for c in chunks if c]


def embed(texts: list[str], client=None, model: str = "text-embedding-3-small") -> list[list[float]]:
    """Embed texts with OpenAI. Requires OPENAI_API_KEY and openai package."""
    if client is None:
        from openai import OpenAI
        client = OpenAI()
    resp = client.embeddings.create(model=model, input=texts)
    return [r.embedding for r in resp.data]


def build_index(chunks: list[str], collection_name: str = "rag", client=None, embed_fn=None):
    """
    Build a ChromaDB index from chunks. Returns (chroma_client, collection).
    embed_fn(texts) -> list[list[float]]; if None, uses embed() with OpenAI.
    """
    import chromadb
    if embed_fn is None:
        from dotenv import load_dotenv
        load_dotenv()
        embed_fn = lambda texts: embed(texts, client=client)
    chroma_client = chromadb.EphemeralClient()
    coll = chroma_client.create_collection(collection_name, metadata={"description": "RAG demo"})
    ids = [str(i) for i in range(len(chunks))]
    coll.add(ids=ids, embeddings=embed_fn(chunks), documents=chunks)
    return chroma_client, coll
