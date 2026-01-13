"""
Similarity search using ChromaDB.
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

# Get the directory where this file is located
_current_dir = os.path.dirname(os.path.abspath(__file__))
_persist_directory = os.path.join(_current_dir, ".chroma")

# Initialize ChromaDB client
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


def add_product(embedding: List[float], metadata: Dict[str, Any], product_id: str):
    """
    Add a product to ChromaDB.
    
    Args:
        embedding: 384-dimensional embedding vector
        metadata: Product metadata dictionary
        product_id: Unique product identifier
    """
    collection = _get_collection()
    collection.add(
        embeddings=[embedding],
        metadatas=[metadata],
        ids=[product_id]
    )


def search_products(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for similar products using cosine similarity.
    
    Args:
        query_embedding: 384-dimensional query embedding vector
        top_k: Number of results to return
        
    Returns:
        List of product dictionaries with metadata and similarity scores
    """
    collection = _get_collection()
    
    # Check if collection is empty
    count = collection.count()
    if count == 0:
        return []
    
    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Convert results to list of dicts with scores
    products = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i, product_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if 'distances' in results else 0.0
            
            # Convert distance to similarity score (1 - distance)
            score = round(1 - distance, 2)
            
            # Convert metadata fields
            product = {
                "id": product_id,
                "name": metadata.get("name", ""),
                "description": metadata.get("description", ""),
                "category": metadata.get("category", ""),
                "image_path": metadata.get("image_path", ""),
                "score": score
            }
            
            # Convert price from string to float (or None)
            price_str = metadata.get("price", "")
            if price_str and price_str.strip():
                try:
                    product["price"] = float(price_str)
                except ValueError:
                    product["price"] = None
            else:
                product["price"] = None
            
            # Convert features from comma-separated string to array
            features_str = metadata.get("features", "")
            if features_str and features_str.strip():
                product["features"] = [f.strip() for f in features_str.split(",")]
            else:
                product["features"] = []
            
            products.append(product)
    
    return products


def get_product_count() -> int:
    """
    Get the total number of products in the database.
    
    Returns:
        Total product count
    """
    collection = _get_collection()
    return collection.count()


def get_product_count_by_category() -> Dict[str, int]:
    """
    Get product count grouped by category.
    
    Returns:
        Dictionary mapping category names to counts
    """
    collection = _get_collection()
    count = collection.count()
    
    if count == 0:
        return {}
    
    # Get all products
    results = collection.get()
    
    # Count by category
    category_counts = {}
    if results['metadatas']:
        for metadata in results['metadatas']:
            category = metadata.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
    
    return category_counts
