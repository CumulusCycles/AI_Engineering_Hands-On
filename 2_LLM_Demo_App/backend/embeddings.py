"""
Text embedding generation using sentence-transformers.
"""
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Global model instance for lazy loading
_model = None


def _get_model():
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model


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


def tokenize(text: str, return_tokens: bool = True, return_ids: bool = True) -> Dict[str, Any]:
    """
    Tokenize text using the same tokenizer as the embedding model.
    Demonstrates the tokenization step that happens before embedding generation.
    
    Args:
        text: Input text string
        return_tokens: Whether to return token strings
        return_ids: Whether to return token IDs
        
    Returns:
        Dictionary containing:
        - tokens: List of token strings (without special tokens)
        - tokens_with_special: List of token strings (with special tokens)
        - token_ids: List of token IDs (with special tokens)
        - token_ids_no_special: List of token IDs (without special tokens)
        - token_count: Total token count (with special tokens)
        - token_count_no_special: Token count (without special tokens)
        - word_count: Word count (split by spaces)
        - character_count: Character count
        - token_mapping: List of dicts with token, token_id, and position
    """
    model = _get_model()
    tokenizer = model.tokenizer
    
    # Tokenize the text
    encoded = tokenizer(text, return_tensors="pt", add_special_tokens=True)
    input_ids = encoded['input_ids'][0].tolist()
    
    # Get special token IDs
    special_token_ids = set()
    if hasattr(tokenizer, 'cls_token_id') and tokenizer.cls_token_id is not None:
        special_token_ids.add(tokenizer.cls_token_id)
    if hasattr(tokenizer, 'sep_token_id') and tokenizer.sep_token_id is not None:
        special_token_ids.add(tokenizer.sep_token_id)
    if hasattr(tokenizer, 'pad_token_id') and tokenizer.pad_token_id is not None:
        special_token_ids.add(tokenizer.pad_token_id)
    # Common special token IDs (101 = [CLS], 102 = [SEP] for many models)
    special_token_ids.add(101)
    special_token_ids.add(102)
    special_token_ids.add(0)  # Often padding
    
    # Get tokens with special tokens
    tokens_with_special = []
    for token_id in input_ids:
        token_str = tokenizer.decode([token_id], skip_special_tokens=False)
        # Check if it's a special token
        if token_id in special_token_ids:
            # Try to get the actual special token string
            if token_id == 101 or (hasattr(tokenizer, 'cls_token_id') and token_id == tokenizer.cls_token_id):
                tokens_with_special.append('[CLS]')
            elif token_id == 102 or (hasattr(tokenizer, 'sep_token_id') and token_id == tokenizer.sep_token_id):
                tokens_with_special.append('[SEP]')
            else:
                tokens_with_special.append(token_str)
        else:
            tokens_with_special.append(token_str)
    
    # Get tokens without special tokens
    tokens = []
    for token_id in input_ids:
        if token_id not in special_token_ids:
            token_str = tokenizer.decode([token_id], skip_special_tokens=True).strip()
            if token_str:  # Only add non-empty tokens
                tokens.append(token_str)
    
    token_ids_no_special = [tid for tid in input_ids if tid not in special_token_ids]
    
    # Build token mapping
    token_mapping = []
    position = 0
    for i, token_id in enumerate(input_ids):
        if token_id not in special_token_ids:
            token_str = tokenizer.decode([token_id], skip_special_tokens=True).strip()
            if token_str:  # Only add non-empty tokens
                token_mapping.append({
                    "token": token_str,
                    "token_id": token_id,
                    "position": position
                })
                position += 1
    
    # Calculate statistics
    word_count = len(text.split())
    character_count = len(text)
    token_count = len(input_ids)
    token_count_no_special = len(token_ids_no_special)
    
    result = {
        "token_count": token_count,
        "token_count_no_special": token_count_no_special,
        "word_count": word_count,
        "character_count": character_count,
    }
    
    if return_tokens:
        result["tokens"] = tokens
        result["tokens_with_special"] = tokens_with_special
    
    if return_ids:
        result["token_ids"] = input_ids
        result["token_ids_no_special"] = token_ids_no_special
    
    result["token_mapping"] = token_mapping
    
    return result
