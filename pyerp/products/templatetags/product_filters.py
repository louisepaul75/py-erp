"""
Custom template filters for the products app.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.

    Usage in template:
    {{ my_dict|get_item:key_variable }}
    """
    if not dictionary:
        return None

    return dictionary.get(key)


@register.filter
def get_primary_image(product):
    """
    Get the primary image for a product.

    Usage in template:
    {{ product|get_primary_image }}
    """
    image = None
    if hasattr(product, "images"):
        # Safely try to find the best image based on the priority:
        # 1. Produktfoto that is front=True
        # 2. Any Produktfoto
        # 3. Any front=True image
        # 4. Any is_primary=True image
        # 5. First image
        try:
            # First priority: Produktfoto that is front=True
            image = product.images.filter(
                image_type__iexact="Produktfoto", is_front=True
            ).first()
            
            if not image:
                # Second priority: Any Produktfoto
                image = product.images.filter(image_type__iexact="Produktfoto").first()
            
            if not image:
                # Third priority: Any front=True image
                image = product.images.filter(is_front=True).first()
            
            if not image:
                # Fourth priority: Any image marked as primary
                image = product.images.filter(is_primary=True).first()
            
            if not image:
                # Last resort: first image
                image = product.images.first()
        except Exception:
            pass
    
    return image
