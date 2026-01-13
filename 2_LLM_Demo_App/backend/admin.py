"""
Product creation and image generation.
"""
import os
import uuid
from typing import Dict, Any, Optional, List
from PIL import Image, ImageDraw, ImageFont

from .embeddings import encode
from .search import add_product

# Category colors
CATEGORY_COLORS = {
    "Tent": "#4A90E2",
    "Backpack": "#50C878",
    "Sleeping Bag": "#FF6B6B",
    "Cooking": "#FFA500"
}
DEFAULT_COLOR = "#808080"


def create_product(
    name: str,
    description: str,
    category: str,
    price: Optional[float] = None,
    features: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new product with generated image and embedding.
    
    Args:
        name: Product name
        description: Product description
        category: Product category (Tent, Backpack, Sleeping Bag, Cooking)
        price: Optional product price
        features: Optional list of feature strings
        
    Returns:
        Product dictionary with id, name, description, category, price, features, image_path
    """
    # Generate UUID for product ID
    product_id = str(uuid.uuid4())
    
    # Get category color
    color = CATEGORY_COLORS.get(category, DEFAULT_COLOR)
    
    # Create image directory if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(current_dir, "static", "products")
    os.makedirs(image_dir, exist_ok=True)
    
    # Generate placeholder image (800x600)
    image = Image.new('RGB', (800, 600), color=color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a bold font, fallback to default if not available
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (800 - text_width) // 2
    y = (600 - text_height) // 2
    
    # Draw white text
    draw.text((x, y), name, fill='white', font=font)
    
    # Save image
    image_path = os.path.join(image_dir, f"{product_id}.jpg")
    image.save(image_path, "JPEG")
    
    # Generate embedding from description
    embedding = encode(description)
    
    # Prepare metadata for ChromaDB
    metadata = {
        "name": name,
        "description": description,
        "category": category,
        "price": str(price) if price is not None else "",
        "features": ",".join(features) if features else "",
        "image_path": f"static/products/{product_id}.jpg"
    }
    
    # Store in ChromaDB
    add_product(embedding, metadata, product_id)
    
    # Return product dict
    return {
        "id": product_id,
        "name": name,
        "description": description,
        "category": category,
        "price": price,
        "features": features if features else [],
        "image_path": f"static/products/{product_id}.jpg"
    }
