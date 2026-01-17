"""
Text tokenization and embedding generation using sentence-transformers.
"""
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Global model instance (lazy loaded)
_model = None

def _get_model() -> SentenceTransformer:
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model

def tokenize(text: str) -> Dict[str, Any]:
    """
    Tokenize text and return token information.
    
    Args:
        text: Input text string
        
    Returns:
        Dictionary with tokens, token IDs, and counts
    """
    model = _get_model()
    tokenizer = model.tokenizer

    # Tokenize the text
    encoded = tokenizer(text, add_special_tokens=True)
    input_ids = encoded['input_ids']

    # Get tokens
    tokens_with_special = tokenizer.convert_ids_to_tokens(input_ids)
    tokens = [t for t in tokens_with_special if t not in ['[CLS]', '[SEP]', '[PAD]']]

    # Build token mapping
    token_mapping = []
    for i, token_id in enumerate(input_ids):
        token_str = tokenizer.convert_ids_to_tokens([token_id])[0]
        if token_str not in ['[CLS]', '[SEP]', '[PAD]']:
            token_mapping.append({
                "token": token_str,
                "token_id": token_id,
                "position": len(token_mapping)
            })

    return {
        "original_text": text,
        "tokens": tokens,
        "token_ids": [t["token_id"] for t in token_mapping],
        "token_count": len(tokens),
        "token_mapping": token_mapping
    }

def encode(text: str) -> List[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.
    
    Args:
        text: Input text string
        
    Returns:
        384-dimensional vector as a list of floats
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def get_embedding_stats(embedding: List[float]) -> Dict[str, Any]:
    """
    Calculate statistics for an embedding vector.
    
    Args:
        embedding: Embedding vector
        
    Returns:
        Dictionary with min, max, mean, std
    """
    import numpy as np
    arr = np.array(embedding)
    return {
        "dimension": len(embedding),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr))
    }
