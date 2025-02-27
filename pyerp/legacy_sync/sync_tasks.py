"""
Data synchronization tasks for the legacy_sync app.

This module provides functions for synchronizing data between the legacy 4D-based ERP
and the new Django-based ERP system.
"""

import logging
import importlib
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from django.db import transaction
from django.utils import timezone
from django.apps import apps

from pyerp.legacy_sync.api_client import api_client
from pyerp.legacy_sync.models import SyncLog, SyncStatus, EntityMapping, EntityMappingConfig

# Configure logging
logger = logging.getLogger(__name__)


def get_model_class(model_path):
    """
    Get a model class from its full path.
    
    Args:
        model_path: Full path to the model class (e.g., 'pyerp.products.models.Product')
        
    Returns:
        The model class.
    """
    try:
        module_path, class_name = model_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Error importing model {model_path}: {e}")
        raise


def sync_entity(entity_type: str, new_only: bool = True) -> Dict[str, Any]:
    """
    Generic function to synchronize entities from the legacy system to the new system.
    
    Args:
        entity_type: Type of entity to synchronize (e.g., 'product', 'customer')
        new_only: If True, only fetch and sync entities that have been modified since the last sync.
        
    Returns:
        A dictionary with sync statistics.
    """
    logger.info(f"Starting {entity_type} synchronization (new_only={new_only})")
    
    # Get the mapping configuration
    try:
        mapping_config = EntityMappingConfig.objects.get(entity_type=entity_type, is_active=True)
    except EntityMappingConfig.DoesNotExist:
        logger.error(f"No active mapping configuration found for {entity_type}")
        raise ValueError(f"No active mapping configuration found for {entity_type}")
    
    # Create a sync log entry
    sync_log = SyncLog.objects.create(
        entity_type=entity_type,
        status=SyncStatus.IN_PROGRESS,
        started_at=timezone.now()
    )
    
    stats = {
        'total_fetched': 0,
        'created': 0,
        'updated': 0,
        'errors': 0,
    }
    
    try:
        # Get the model class
        model_class = get_model_class(mapping_config.new_model)
        
        # Fetch entities from the legacy system
        legacy_table = mapping_config.legacy_table
        entities_df = api_client.fetch_table(
            table_name=legacy_table,
            new_data_only=new_only
        )
        
        stats['total_fetched'] = len(entities_df)
        logger.info(f"Fetched {stats['total_fetched']} {entity_type} records from legacy system")
        
        # Process each entity
        for _, row in entities_df.iterrows():
            try:
                with transaction.atomic():
                    # Convert DataFrame row to dict
                    legacy_data = row.to_dict()
                    legacy_id = str(legacy_data.get('id'))
                    
                    if not legacy_id:
                        logger.warning(f"Skipping {entity_type} record with no ID")
                        continue
                    
                    # Transform legacy data to new format
                    new_data = mapping_config.transform_legacy_data(legacy_data)
                    
                    # Add legacy_id to the new data
                    new_data['legacy_id'] = legacy_id
                    
                    # Check if we already have a mapping for this entity
                    try:
                        mapping = EntityMapping.objects.get(
                            entity_type=entity_type,
                            legacy_id=legacy_id
                        )
                        # Update existing entity
                        entity = model_class.objects.get(id=mapping.new_id)
                        for field, value in new_data.items():
                            setattr(entity, field, value)
                        entity.save()
                        stats['updated'] += 1
                        logger.debug(f"Updated {entity_type} {legacy_id} -> {entity.id}")
                    except EntityMapping.DoesNotExist:
                        # Create new entity
                        entity = model_class.objects.create(**new_data)
                        # Create mapping
                        EntityMapping.objects.create(
                            entity_type=entity_type,
                            legacy_id=legacy_id,
                            new_id=str(entity.id)
                        )
                        stats['created'] += 1
                        logger.debug(f"Created {entity_type} {legacy_id} -> {entity.id}")
                    except model_class.DoesNotExist:
                        # Mapping exists but entity doesn't - recreate it
                        entity = model_class.objects.create(**new_data)
                        # Update mapping
                        mapping.new_id = str(entity.id)
                        mapping.save()
                        stats['created'] += 1
                        logger.debug(f"Recreated {entity_type} {legacy_id} -> {entity.id}")
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing {entity_type} {legacy_data.get('id', 'unknown')}: {e}")
        
        # Update the sync log
        sync_log.status = SyncStatus.COMPLETED
        sync_log.completed_at = timezone.now()
        sync_log.records_processed = stats['total_fetched']
        sync_log.records_created = stats['created']
        sync_log.records_updated = stats['updated']
        sync_log.records_failed = stats['errors']
        sync_log.save()
        
        logger.info(f"{entity_type.capitalize()} synchronization completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error during {entity_type} synchronization: {e}")
        
        # Update the sync log
        sync_log.status = SyncStatus.FAILED
        sync_log.completed_at = timezone.now()
        sync_log.error_message = str(e)
        sync_log.save()
        
        raise


def sync_products(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize products from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync products that have been modified since the last sync.

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('product', new_only)


def sync_customers(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize customers from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync customers that have been modified since the last sync.

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('customer', new_only)


# Add more specific sync functions as needed
def sync_orders(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize orders from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync orders that have been modified since the last sync.

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('order', new_only)


def sync_inventory(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize inventory from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync inventory that have been modified since the last sync.

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('inventory', new_only) 