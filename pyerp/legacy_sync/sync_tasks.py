"""
Data synchronization tasks for the legacy_sync app.

This module provides functions for synchronizing data between the legacy 4D-based ERP  # noqa: E501
and the new Django-based ERP system.
"""

import logging
import importlib
from typing import Dict, List, Optional, Any, Union  # noqa: F401
import pandas as pd  # noqa: F401
from django.db import transaction
from django.utils import timezone
from django.apps import apps  # noqa: F401
from datetime import datetime

from pyerp.legacy_sync.api_client import api_client
from pyerp.legacy_sync.models import SyncLog, SyncStatus, EntityMapping, EntityMappingConfig  # noqa: E501

 # Configure logging
logger = logging.getLogger(__name__)


def get_model_class(model_path):
    """
    Get a model class from its full path.

    Args:
        model_path: Full path to the model class (e.g., 'pyerp.products.models.Product')  # noqa: E501

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


def map_variant_product_fields(variant_product, legacy_data):
    """
    Map fields from legacy Artikel_Variante data to the VariantProduct model.

    Args:
        variant_product: The VariantProduct instance to update
        legacy_data: Dictionary containing legacy data from Artikel_Variante

    Returns:
        The updated VariantProduct instance
    """
    variant_product.is_verkaufsartikel = legacy_data.get('Verkaufsartikel', False)  # noqa: E501

 # Handle date fields
    release_date = legacy_data.get('Release_Date')
    if release_date:
        if isinstance(release_date, (int, float)):
            variant_product.release_date = datetime.fromtimestamp(release_date / 1000)  # noqa: E501
        else:
            variant_product.release_date = release_date

    auslaufdatum = legacy_data.get('Auslaufdatum')
    if auslaufdatum:
        if isinstance(auslaufdatum, (int, float)):
            variant_product.auslaufdatum = datetime.fromtimestamp(auslaufdatum / 1000)  # noqa: E501
        else:
            variant_product.auslaufdatum = auslaufdatum

 # Handle pricing fields from the Preise collection
    preise = legacy_data.get('Preise', {}).get('Coll', [])
    for preis in preise:
        art = preis.get('Art')
        if art == 'Laden':  # Retail price
            variant_product.retail_price = preis.get('Preis')
            variant_product.retail_unit = preis.get('VE')
        elif art == 'Handel':  # Wholesale price
            variant_product.wholesale_price = preis.get('Preis')
            variant_product.wholesale_unit = preis.get('VE')

 # Extract additional data for physical attributes from Properties if available  # noqa: E501
    properties = legacy_data.get('Properties', {})
    if isinstance(properties, dict) and 'results' in properties:
        props = properties.get('results', [])
        for prop in props:
            prop_name = prop.get('name', '').lower()
            prop_value = prop.get('value')

            if prop_name == 'farbe' or prop_name == 'color':
                variant_product.color = prop_value
            elif prop_name == 'größe' or prop_name == 'size' or prop_name == 'groesse':  # noqa: E501
                variant_product.size = prop_value
            elif prop_name == 'material':
                variant_product.material = prop_value
            elif prop_name in ('gewicht', 'weight'):
                try:
                    variant_product.weight_grams = float(prop_value)
                except (ValueError, TypeError):
                    pass
            elif prop_name in ('länge', 'length', 'laenge'):
                try:
                    variant_product.length_mm = float(prop_value)
                except (ValueError, TypeError):
                    pass
            elif prop_name in ('breite', 'width'):
                try:
                    variant_product.width_mm = float(prop_value)
                except (ValueError, TypeError):
                    pass
            elif prop_name in ('höhe', 'height', 'hoehe'):
                try:
                    variant_product.height_mm = float(prop_value)
                except (ValueError, TypeError):
                    pass

    return variant_product


def sync_entity(entity_type: str, new_only: bool = True) -> Dict[str, Any]:
    """
    Generic function to synchronize entities from the legacy system to the new system.  # noqa: E501

    Args:
        entity_type: Type of entity to synchronize (e.g., 'product', 'customer')  # noqa: E501
        new_only: If True, only fetch and sync entities that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    logger.info(f"Starting {entity_type} synchronization (new_only={new_only})")  # noqa: E501

 # Get the mapping configuration
    try:
        mapping_config = EntityMappingConfig.objects.get(entity_type=entity_type, is_active=True)  # noqa: E501
    except EntityMappingConfig.DoesNotExist:
        logger.error(f"No active mapping configuration found for {entity_type}")  # noqa: E501
        raise ValueError(f"No active mapping configuration found for {entity_type}")  # noqa: E501

 # Create a sync log entry
    sync_log = SyncLog.objects.create(
        entity_type=entity_type,  # noqa: E128
        status=SyncStatus.IN_PROGRESS,  # noqa: F841
        started_at=timezone.now()  # noqa: F841
    )

    stats = {
        'total_fetched': 0,  # noqa: E128
        'created': 0,
        'updated': 0,
        'errors': 0,
    }

    try:
        model_class = get_model_class(mapping_config.new_model)

 # Fetch entities from the legacy system
        legacy_table = mapping_config.legacy_table
        entities_df = api_client.fetch_table(
            table_name=legacy_table,  # noqa: F841
            new_data_only=new_only  # noqa: F841
        )

        stats['total_fetched'] = len(entities_df)
        logger.info(f"Fetched {stats['total_fetched']} {entity_type} records from legacy system")  # noqa: E501

 # Process each entity
        for _, row in entities_df.iterrows():
            try:
                with transaction.atomic():
                    legacy_data = row.to_dict()
                    legacy_id = str(legacy_data.get('id'))

                    if not legacy_id:
                        logger.warning(f"Skipping {entity_type} record with no ID")  # noqa: E501
                        continue

 # Transform the legacy data using the mapping configuration
                    new_data = mapping_config.transform_legacy_data(legacy_data)  # noqa: E501

 # Add the legacy ID to the new data
                    new_data['legacy_id'] = legacy_id

 # Apply additional custom mapping for variant products
                    if entity_type == 'variant_product':
                        try:
                            if not EntityMapping.objects.filter(entity_type=entity_type, legacy_id=legacy_id).exists():  # noqa: E501
                                entity = model_class.objects.create(**new_data)
                                map_variant_product_fields(entity, legacy_data)
                                EntityMapping.objects.create(
                                    entity_type=entity_type,  # noqa: E128
                                    legacy_id=legacy_id,
                                    new_id=str(entity.id)  # noqa: F841
                                )
                                stats['created'] += 1
                                logger.debug(f"Created {entity_type} {legacy_id} -> {entity.id}")  # noqa: E501
                                continue  # Skip the regular create/update flow
                            else:
                                mapping = EntityMapping.objects.get(entity_type=entity_type, legacy_id=legacy_id)  # noqa: E501
                                entity = model_class.objects.get(id=mapping.new_id)  # noqa: E501
                                for field, value in new_data.items():
                                    setattr(entity, field, value)
                                map_variant_product_fields(entity, legacy_data)
                                entity.save()
                                stats['updated'] += 1
                                logger.debug(f"Updated {entity_type} {legacy_id} -> {entity.id}")  # noqa: E501
                                continue  # Skip the regular create/update flow
                        except Exception as e:
                            logger.error(f"Error in custom mapping for {entity_type} {legacy_id}: {e}")  # noqa: E501
                            stats['errors'] += 1
                            continue

 # Regular create/update flow for other entity types
 # Check if we already have a mapping for this entity
                    try:
                        mapping = EntityMapping.objects.get(
                            entity_type=entity_type,  # noqa: E128
                            legacy_id=legacy_id
                        )
                        entity = model_class.objects.get(id=mapping.new_id)
                        for field, value in new_data.items():
                            setattr(entity, field, value)
                        entity.save()
                        stats['updated'] += 1
                        logger.debug(f"Updated {entity_type} {legacy_id} -> {entity.id}")  # noqa: E501
                    except EntityMapping.DoesNotExist:
                        entity = model_class.objects.create(**new_data)
                        EntityMapping.objects.create(
                            entity_type=entity_type,  # noqa: E128
                            legacy_id=legacy_id,
                            new_id=str(entity.id)  # noqa: F841
                        )
                        stats['created'] += 1
                        logger.debug(f"Created {entity_type} {legacy_id} -> {entity.id}")  # noqa: E501
                    except model_class.DoesNotExist:
                        entity = model_class.objects.create(**new_data)
                        mapping.new_id = str(entity.id)
                        mapping.save()
                        stats['created'] += 1
                        logger.debug(f"Recreated {entity_type} {legacy_id} -> {entity.id}")  # noqa: E501

            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing {entity_type} {legacy_data.get('id', 'unknown')}: {e}")  # noqa: E501

 # Update the sync log
        sync_log.status = SyncStatus.COMPLETED
        sync_log.completed_at = timezone.now()
        sync_log.records_processed = stats['total_fetched']
        sync_log.records_created = stats['created']
        sync_log.records_updated = stats['updated']
        sync_log.records_failed = stats['errors']
        sync_log.save()

        logger.info(f"{entity_type.capitalize()} synchronization completed: {stats}")  # noqa: E501
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
        new_only: If True, only fetch and sync products that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('product', new_only)


def sync_customers(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize customers from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync customers that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('customer', new_only)


 # Add more specific sync functions as needed


def sync_orders(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize orders from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync orders that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('order', new_only)


def sync_variant_products(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize product variants from the legacy system to the new system.

    This function uses the custom map_variant_product_fields mapping function to handle  # noqa: E501
    complex data transformations for product variants, including pricing, physical attributes,  # noqa: E501
    and date fields.

    Args:
        new_only: If True, only fetch and sync product variants that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('variant_product', new_only)


def sync_inventory(new_only: bool = True) -> Dict[str, Any]:
    """
    Synchronize inventory from the legacy system to the new system.

    Args:
        new_only: If True, only fetch and sync inventory that have been modified since the last sync.  # noqa: E501

    Returns:
        A dictionary with sync statistics.
    """
    return sync_entity('inventory', new_only)
