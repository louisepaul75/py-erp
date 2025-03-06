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
            # Safely try to find the best image based on the priority:
            # 4. Any is_primary=True image
        try:
        image = product.images.filter(image_type__iexact='Produktfoto', is_front=True).first()  # noqa: E501
        if image:
        return image

 # Second priority: Any Produktfoto
        image = product.images.filter(image_type__iexact='Produktfoto').first()  # noqa: E501
        if image:
        return image

 # Third priority: Any front=True image
        image = product.images.filter(is_front=True).first()
        if image:
        return image

 # Fourth priority: Any image marked as primary
        image = product.images.filter(is_primary=True).first()
        if image:
        return image

 # Last resort: first image
        return product.images.first()
        except:
        return None
    return None
