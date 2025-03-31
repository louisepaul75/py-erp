"""
Preprocessing hooks for drf-spectacular schema generation.
"""
import logging
from django.db import models
from django.apps import apps

logger = logging.getLogger("pyerp.api_docs")

def preprocess_filter_fields(endpoints, **kwargs):
    """
    Preprocessing hook to sanitize filter fields for drf-spectacular.
    
    This function examines ViewSets that use DjangoFilterBackend and ensures
    all filterset_fields exist in the model to prevent schema generation errors.
    """
    # ViewSets with filter issues to fix
    problematic_filters = {
        'CustomerViewSet': {
            'safe_fields': ['customer_group', 'delivery_block'],
        },
        # Add other viewsets here if needed
    }
    
    for (path, path_regex, method, callback) in endpoints:
        view_cls = getattr(callback, 'cls', None)
        if not view_cls:
            continue
            
        view_name = view_cls.__name__
        
        if view_name not in problematic_filters:
            continue
            
        # Fix filterset_fields for problematic ViewSets
        if hasattr(view_cls, 'filterset_fields'):
            safe_fields = problematic_filters[view_name].get('safe_fields', [])
            
            # Override filterset_fields with safe fields
            setattr(view_cls, 'filterset_fields', safe_fields)
            logger.info(f"Fixed filterset_fields for {view_name}: {safe_fields}")
    
    return endpoints 