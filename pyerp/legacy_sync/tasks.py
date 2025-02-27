"""
Celery tasks for the legacy_sync app.
"""

import logging
from celery import shared_task

from pyerp.legacy_sync.sync_tasks import (
    sync_products, sync_customers, sync_orders, sync_inventory, sync_entity
)

# Configure logging
logger = logging.getLogger(__name__)


@shared_task(
    name='legacy_sync.sync_entity',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_entity_task(self, entity_type, new_only=True):
    """
    Celery task to synchronize entities from the legacy system.

    Args:
        entity_type: Type of entity to synchronize (e.g., 'product', 'customer')
        new_only: If True, only fetch and sync entities that have been modified since the last sync.
    """
    logger.info(f"Starting {entity_type} synchronization task (new_only={new_only})")
    try:
        stats = sync_entity(entity_type, new_only=new_only)
        logger.info(f"{entity_type.capitalize()} synchronization task completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error during {entity_type} synchronization task: {e}")
        self.retry(exc=e)


@shared_task(
    name='legacy_sync.sync_products',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_products_task(self, new_only=True):
    """
    Celery task to synchronize products from the legacy system.

    Args:
        new_only: If True, only fetch and sync products that have been modified since the last sync.
    """
    logger.info(f"Starting product synchronization task (new_only={new_only})")
    try:
        stats = sync_products(new_only=new_only)
        logger.info(f"Product synchronization task completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error during product synchronization task: {e}")
        self.retry(exc=e)


@shared_task(
    name='legacy_sync.sync_customers',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_customers_task(self, new_only=True):
    """
    Celery task to synchronize customers from the legacy system.

    Args:
        new_only: If True, only fetch and sync customers that have been modified since the last sync.
    """
    logger.info(f"Starting customer synchronization task (new_only={new_only})")
    try:
        stats = sync_customers(new_only=new_only)
        logger.info(f"Customer synchronization task completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error during customer synchronization task: {e}")
        self.retry(exc=e)


@shared_task(
    name='legacy_sync.sync_orders',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_orders_task(self, new_only=True):
    """
    Celery task to synchronize orders from the legacy system.

    Args:
        new_only: If True, only fetch and sync orders that have been modified since the last sync.
    """
    logger.info(f"Starting order synchronization task (new_only={new_only})")
    try:
        stats = sync_orders(new_only=new_only)
        logger.info(f"Order synchronization task completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error during order synchronization task: {e}")
        self.retry(exc=e)


@shared_task(
    name='legacy_sync.sync_inventory',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_inventory_task(self, new_only=True):
    """
    Celery task to synchronize inventory from the legacy system.

    Args:
        new_only: If True, only fetch and sync inventory that have been modified since the last sync.
    """
    logger.info(f"Starting inventory synchronization task (new_only={new_only})")
    try:
        stats = sync_inventory(new_only=new_only)
        logger.info(f"Inventory synchronization task completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error during inventory synchronization task: {e}")
        self.retry(exc=e)


@shared_task(
    name='legacy_sync.sync_all',
    bind=True,
)
def sync_all_task(self, new_only=True):
    """
    Celery task to synchronize all entity types from the legacy system.

    Args:
        new_only: If True, only fetch and sync entities that have been modified since the last sync.
    """
    logger.info(f"Starting full synchronization task (new_only={new_only})")
    
    # Call each sync task individually
    sync_products_task.delay(new_only=new_only)
    sync_customers_task.delay(new_only=new_only)
    sync_orders_task.delay(new_only=new_only)
    sync_inventory_task.delay(new_only=new_only)
    
    logger.info("Full synchronization task dispatched")
    return {"status": "dispatched"} 