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