"""
FastAPI application for the LLM Pipeline Demo.
"""
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

try:
    from .embeddings import tokenize, encode, get_embedding_stats
    from .search import get_product_count, seed_products, search_products, get_all_embeddings
except ImportError:
    from embeddings import tokenize, encode, get_embedding_stats
    from search import get_product_count, seed_products, search_products, get_all_embeddings

app = FastAPI(title="LLM Pipeline Demo")

# Request models
class TextRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

# Route 1: Health Check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "product_count": get_product_count()
    }

# Route 2: Seed Database
@app.post("/seed")
async def seed():
    """Seed the vector store with products."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "seed_products.json")
    
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Seed data file not found")
    
    with open(data_file, 'r') as f:
        products = json.load(f)
    
    result = seed_products(products)
    
    return {
        "success": True,
        "message": f"Seeded {result['created']} products",
        **result
    }

# Route 3: Tokenize
@app.post("/tokenize")
async def tokenize_text(request: TextRequest):
    """Tokenize the input text."""
    try:
        result = tokenize(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route 4: Generate Embedding
@app.post("/embedding")
async def generate_embedding(request: TextRequest):
    """Generate embedding for the input text."""
    try:
        embedding = encode(request.text)
        stats = get_embedding_stats(embedding)
        
        return {
            "text": request.text,
            "embedding": embedding,
            "first_10": embedding[:10],
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route 5: Search
@app.post("/search")
async def search(request: SearchRequest):
    """Search for similar products."""
    try:
        results = search_products(request.query, request.top_k)
        return {
            "query": request.query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route 6: Get all embeddings (for visualization)
@app.get("/embeddings")
async def get_embeddings():
    """Get all embeddings for visualization."""
    try:
        return get_all_embeddings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
