"""
Image captioning using BLIP model.
"""
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Global model instances for lazy loading
_processor = None
_model = None


def _get_models():
    """Lazy load the BLIP processor and model."""
    global _processor, _model
    if _processor is None or _model is None:
        _processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
        _model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
    return _processor, _model


def generate_caption(image: Image.Image) -> str:
    """
    Generate a text caption for the given image using BLIP.
    
    Args:
        image: PIL Image object
        
    Returns:
        Generated caption string (max 50 tokens)
    """
    processor, model = _get_models()
    
    # Process the image
    inputs = processor(images=image, return_tensors="pt")
    
    # Generate caption with max_length=50
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_length=50)
    
    # Decode the generated caption
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    
    return caption
