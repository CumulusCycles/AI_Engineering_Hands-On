"""
Database seeding script to load sample products from seed_products.json.
Run this from the backend directory: python seed.py
Or run as a module from project root: python -m backend.seed
"""

import json
import os
import sys

# Handle imports - work whether run directly or as module
if __name__ == "__main__":
    # When run directly, add parent to path and import as package
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    _parent_dir = os.path.dirname(_backend_dir)
    if _parent_dir not in sys.path:
        sys.path.insert(0, _parent_dir)
    from backend.admin import create_product
else:
    # Use relative import when run as module
    from .admin import create_product

# Get the directory where this file is located
_current_dir = os.path.dirname(os.path.abspath(__file__))
_data_file = os.path.join(_current_dir, "data", "seed_products.json")


def seed_database():
    """Load and create products from seed_products.json."""
    if not os.path.exists(_data_file):
        print(f"Error: {_data_file} not found")
        return 0, 1
    
    with open(_data_file, 'r') as f:
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
            print(f"Created: {product_data['name']}")
        except Exception as e:
            errors += 1
            print(f"Error creating {product_data.get('name', 'unknown')}: {e}")
    
    print(f"\nSeeding complete: {created} created, {errors} errors")
    return created, errors


if __name__ == "__main__":
    seed_database()
