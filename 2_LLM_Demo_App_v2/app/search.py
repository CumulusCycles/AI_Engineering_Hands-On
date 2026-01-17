"""
Vector store operations using ChromaDB.
"""
import os
from typing import List, Dict, Any
import chromadb

try:
    from .embeddings import encode
except ImportError:
    from embeddings import encode

# ChromaDB setup
_current_dir = os.path.dirname(os.path.abspath(__file__))
_persist_directory = os.path.join(_current_dir, ".chroma")

_client = None
_collection = None

def _get_collection():
    """Get or create the ChromaDB collection."""
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(path=_persist_directory)
    if _collection is None:
        _collection = _client.get_or_create_collection(name="products")
    return _collection

def get_product_count() -> int:
    """Get total number of products in the vector store."""
    collection = _get_collection()
    return collection.count()

def seed_products(products: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Seed the vector store with products.
    
    Args:
        products: List of product dictionaries
        
    Returns:
        Dictionary with created and error counts
    """
    collection = _get_collection()
    created = 0
    errors = 0

    for i, product in enumerate(products):
        try:
            product_id = f"product_{i}"
            
            # Generate embedding from description
            embedding = encode(product["description"])
            
            # Store metadata (no images)
            metadata = {
                "name": product["name"],
                "description": product["description"],
                "category": product["category"],
                "price": str(product.get("price", "")),
                "features": ",".join(product.get("features", []))
            }
            
            collection.add(
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[product_id]
            )
            created += 1
        except Exception as e:
            print(f"Error adding product: {e}")
            errors += 1
    
    return {"created": created, "errors": errors}

def search_products(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search for products similar to the query.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        
    Returns:
        List of products with similarity scores
    """
    collection = _get_collection()
    
    if collection.count() == 0:
        return []

    # Generate query embedding
    query_embedding = encode(query)

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Format results
    products = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i, product_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if 'distances' in results else 0.0
            score = round(1 - distance, 4)
            
            products.append({
                "id": product_id,
                "name": metadata.get("name", ""),
                "description": metadata.get("description", ""),
                "category": metadata.get("category", ""),
                "price": float(metadata["price"]) if metadata.get("price") else None,
                "features": metadata.get("features", "").split(",") if metadata.get("features") else [],
                "score": score
            })
    
    return products

def get_all_embeddings() -> Dict[str, Any]:
    """
    Get all products and their embeddings for visualization.
    
    Returns:
        Dictionary with names and embeddings
    """
    collection = _get_collection()

    if collection.count() == 0:
        return {"names": [], "embeddings": [], "categories": []}
    
    results = collection.get(include=["embeddings", "metadatas"])

    names = [m["name"] for m in results["metadatas"]]
    # Convert numpy arrays to lists for JSON serialization
    embeddings = [list(e) if hasattr(e, 'tolist') else list(e) for e in results["embeddings"]]
    categories = [m["category"] for m in results["metadatas"]]

    return {
        "names": names,
        "embeddings": embeddings,
        "categories": categories
    }
