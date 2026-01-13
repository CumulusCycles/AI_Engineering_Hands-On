"""
FastAPI application for the Outdoor Adventure Gear Catalog Search.
"""
import os
import json
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .embeddings import encode, tokenize
from .captioning import generate_caption
from .search import search_products, get_product_count, get_product_count_by_category
from .admin import create_product

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files
_current_dir = os.path.dirname(os.path.abspath(__file__))
_static_dir = os.path.join(_current_dir, "static")
os.makedirs(_static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# Pydantic models (v1 syntax)
class ProductCreate(BaseModel):
    name: str
    description: str
    category: str
    price: Optional[float] = None
    features: Optional[List[str]] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class TokenizeRequest(BaseModel):
    text: str


class EmbeddingRequest(BaseModel):
    text: str


class SimilarityRequest(BaseModel):
    texts: List[str]


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    count = get_product_count()
    return {
        "status": "healthy",
        "product_count": count
    }


# Admin endpoints
@app.get("/admin/stats")
async def get_stats():
    """Get product statistics."""
    total = get_product_count()
    by_category = get_product_count_by_category()
    return {
        "total": total,
        "by_category": by_category
    }


@app.post("/admin/seed")
async def seed_database():
    """Seed the database with sample products."""
    data_file = os.path.join(_current_dir, "data", "seed_products.json")
    
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Seed data file not found")
    
    with open(data_file, 'r') as f:
        products = json.load(f)
    
    created = 0
    errors = 0
    
    for product_data in products:
        try:
            create_product(
                name=product_data['name'],
                description=product_data['description'],
                category=product_data['category'],
                price=product_data.get('price'),
                features=product_data.get('features', [])
            )
            created += 1
        except Exception as e:
            errors += 1
            print(f"Error creating {product_data.get('name', 'unknown')}: {e}")
    
    return {
        "success": True,
        "message": f"Successfully seeded {created} products",
        "created": created,
        "errors": errors
    }


@app.post("/admin/products")
async def create_product_endpoint(product: ProductCreate):
    """Create a new product."""
    try:
        result = create_product(
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            features=product.features
        )
        return {
            "success": True,
            "product": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Search endpoints
@app.post("/search")
async def search_by_text(request: SearchRequest):
    """Search products by text query."""
    try:
        # Generate embedding from query
        query_embedding = encode(request.query)
        
        # Search products
        results = search_products(query_embedding, top_k=request.top_k)
        
        return {
            "query_caption": request.query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/image")
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = Form(5)
):
    """Search products by image upload."""
    # Validate file type
    content_type = file.content_type
    if content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        # Also check file extension as fallback
        filename = file.filename or ""
        if not (filename.lower().endswith('.jpg') or 
                filename.lower().endswith('.jpeg') or 
                filename.lower().endswith('.png')):
            raise HTTPException(
                status_code=400,
                detail="File must be JPG or PNG"
            )
    
    # Read file content
    contents = await file.read()
    
    # Validate file size (max 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Convert to PIL Image
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(contents))
        
        # Generate caption using BLIP
        caption = generate_caption(image)
        
        # Generate embedding from caption
        query_embedding = encode(caption)
        
        # Search products
        results = search_products(query_embedding, top_k=top_k)
        
        return {
            "query_caption": caption,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Debug endpoints
@app.post("/debug/tokenize")
async def debug_tokenize(request: TokenizeRequest):
    """Tokenize text for educational purposes."""
    try:
        result = tokenize(request.text)
        return {
            "original_text": request.text,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/embedding")
async def debug_embedding(request: EmbeddingRequest):
    """Generate embedding for educational purposes."""
    try:
        embedding = encode(request.text)
        embedding_array = np.array(embedding)
        
        # Calculate statistics
        stats = {
            "min": float(np.min(embedding_array)),
            "max": float(np.max(embedding_array)),
            "mean": float(np.mean(embedding_array)),
            "std": float(np.std(embedding_array))
        }
        
        # Get first 10 dimensions
        first_n = embedding[:10]
        
        return {
            "text": request.text,
            "embedding": embedding,
            "dimension": len(embedding),
            "first_n_dimensions": first_n,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/similarity")
async def debug_similarity(request: SimilarityRequest):
    """Calculate similarity matrix for multiple texts."""
    try:
        if len(request.texts) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 texts required"
            )
        
        # Generate embeddings for all texts
        embeddings = [encode(text) for text in request.texts]
        embeddings_array = np.array(embeddings)
        
        # Calculate cosine similarity matrix
        # Normalize embeddings
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        normalized = embeddings_array / (norms + 1e-8)
        
        # Compute similarity matrix (dot product of normalized vectors)
        similarity_matrix = np.dot(normalized, normalized.T)
        similarity_matrix = similarity_matrix.tolist()
        
        # Create pairwise similarities
        pairwise = []
        for i in range(len(request.texts)):
            for j in range(i + 1, len(request.texts)):
                pairwise.append({
                    "text1": request.texts[i],
                    "text2": request.texts[j],
                    "similarity": round(float(similarity_matrix[i][j]), 2)
                })
        
        return {
            "similarity_matrix": similarity_matrix,
            "texts": request.texts,
            "pairwise_similarities": pairwise
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
