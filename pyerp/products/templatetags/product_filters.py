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
    if hasattr(product, 'images'):
        # Safely get the first primary image
        try:
            return product.images.filter(is_primary=True).first()
        except:
            return None
    return None 