"""Celery tasks for scheduled synchronization operations."""

from typing import Dict, List, Optional
import os
import yaml

from django.conf import settings
from django.db import transaction
from django.utils import timezone

try:
    from celery import shared_task
except ImportError:
    # Create dummy decorator for testing
    def shared_task(func):
        return func

from celery.schedules import crontab
from pyerp.utils.logging import get_logger, log_data_sync_event

from .models import SyncMapping, SyncSource, SyncTarget
from .pipeline import PipelineFactory

logger = get_logger(__name__)


def _load_sales_record_yaml() -> Dict:
    """Load sales record sync configuration from YAML file."""
    config_path = os.path.join(
        os.path.dirname(__file__), "config", "sales_record_sync.yaml"
    )
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load sales record sync config: {e}")
        return {}


def get_sales_record_mappings():
    """Get sales record mappings from YAML configuration.
    
    Returns:
        Tuple containing (sales_record_mapping, sales_record_item_mapping)
    """
    config = _load_sales_record_yaml()
    mappings = config.get("mappings", [])
    
    # Extract the sales record and item mappings
    sales_record_mapping = None
    sales_record_item_mapping = None
    
    for mapping in mappings:
        if mapping.get("entity_type") == "sales_record":
            sales_record_mapping = mapping
        elif mapping.get("entity_type") == "sales_record_item":
            sales_record_item_mapping = mapping
    
    return sales_record_mapping, sales_record_item_mapping


def create_sales_record_mappings():
    """Create sales record mappings from YAML configuration.
    
    Returns:
        Tuple containing (sales_record_mapping, sales_record_item_mapping)
    """
    config = _load_sales_record_yaml()
    mappings = config.get("mappings", [])
    
    # Create the mappings in database (TODO: Implement this)
    
    # Extract the sales record and item mappings
    sales_record_mapping = None
    sales_record_item_mapping = None
    
    for mapping in mappings:
        if mapping.get("entity_type") == "sales_record":
            sales_record_mapping = mapping
        elif mapping.get("entity_type") == "sales_record_item":
            sales_record_item_mapping = mapping
    
    return sales_record_mapping, sales_record_item_mapping


@shared_task(
    bind=True,
    name="sync.run_entity_sync",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def run_entity_sync(
    self,
    mapping_id: int,
    incremental: bool = True,
    batch_size: int = 100,
    query_params: Optional[Dict] = None,
) -> Dict:
    """Run sync for a specific entity mapping.

    Args:
        mapping_id: ID of the SyncMapping to process
        incremental: If True, only sync records modified since last sync
        batch_size: Number of records to process in each batch
        query_params: Optional additional query parameters

    Returns:
        Dict with sync results
    """
    try:
        mapping = SyncMapping.objects.get(id=mapping_id, active=True)

        # Create pipeline and run sync
        pipeline = PipelineFactory.create_pipeline(mapping)
        sync_log = pipeline.run(
            incremental=incremental, batch_size=batch_size, query_params=query_params
        )

        result = {
            "status": sync_log.status,
            "records_processed": sync_log.records_processed,
            "records_succeeded": sync_log.records_succeeded,
            "records_failed": sync_log.records_failed,
            "sync_log_id": sync_log.id,
        }

        log_data_sync_event(
            source=mapping.source.name,
            destination=mapping.target.name,
            record_count=sync_log.records_processed,
            status=sync_log.status,
            details={
                "entity_type": mapping.entity_type,
                "incremental": incremental,
                "sync_log_id": sync_log.id,
                **result,
            },
        )

        return result

    except SyncMapping.DoesNotExist:
        error_msg = f"Sync mapping with ID {mapping_id} not found or not active"
        log_data_sync_event(
            source="unknown",
            destination="unknown",
            record_count=0,
            status="failed",
            details={"mapping_id": mapping_id, "error": error_msg},
        )
        return {"status": "failed", "error": error_msg}
    except Exception as e:
        error_msg = f"Error in run_entity_sync task: {str(e)}"
        log_data_sync_event(
            source=getattr(mapping, "source.name", "unknown"),
            destination=getattr(mapping, "target.name", "unknown"),
            record_count=0,
            status="failed",
            details={"mapping_id": mapping_id, "error": error_msg},
        )
        raise  # This will trigger retry mechanism


@shared_task(
    name="sync.run_all_mappings",
    max_retries=1,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def run_all_mappings(
    incremental: bool = True, source_name: Optional[str] = None
) -> List[Dict]:
    """Run sync for all active mappings, optionally filtered by source.

    Args:
        incremental: If True, only sync records modified since last sync
        source_name: Optional source name to filter mappings

    Returns:
        List of dicts with sync results
    """
    # Get all active mappings
    mappings = SyncMapping.objects.filter(active=True)

    # Filter by source if specified
    if source_name:
        mappings = mappings.filter(source__name=source_name)

    # Launch a task for each mapping
    results = []
    for mapping in mappings:
        task_result = run_entity_sync.delay(mapping.id, incremental=incremental)
        results.append(
            {
                "mapping_id": mapping.id,
                "entity_type": mapping.entity_type,
                "task_id": task_result.id,
            }
        )

    log_data_sync_event(
        source=source_name or "all",
        destination="all",
        record_count=len(mappings),
        status="scheduled",
        details={"incremental": incremental, "task_count": len(mappings)},
    )

    return results


@shared_task(name="sync.run_incremental_sync")
def run_incremental_sync() -> List[Dict]:
    """Run incremental sync for all active mappings.

    This task is intended to be scheduled to run every 5 minutes.

    Returns:
        List of dicts with sync results
    """
    log_data_sync_event(
        source="all",
        destination="all",
        record_count=0,
        status="starting_incremental",
        details={"schedule": "5min"},
    )
    return run_all_mappings(incremental=True)


@shared_task(name="sync.run_full_sync")
def run_full_sync() -> List[Dict]:
    """Run full sync for all active mappings.

    This task is intended to be scheduled to run nightly.

    Returns:
        List of dicts with sync results
    """
    log_data_sync_event(
        source="all",
        destination="all",
        record_count=0,
        status="starting_full",
        details={"schedule": "nightly"},
    )
    return run_all_mappings(incremental=False)


# Add periodic task registration for Celery Beat
# This will be picked up by Celery Beat scheduler
run_incremental_sync.periodic_task = {
    "name": "sync.scheduled_incremental_sync",
    "schedule": 300.0,  # Every 5 minutes
    "options": {"expires": 290.0},  # Expire if not executed within 290 seconds
}

run_full_sync.periodic_task = {
    "name": "sync.scheduled_full_sync",
    "schedule": {"cron": {"hour": 2, "minute": 0}},  # Run at 2:00 AM
    "options": {"expires": 3600.0},  # Expire if not executed within 1 hour
}


@shared_task(name="sync.run_sales_record_sync")
def run_sales_record_sync(
    incremental: bool = True, batch_size: int = 100
) -> List[Dict]:
    """
    Run sync for sales records and their line items.

    Args:
        incremental: If True, only sync records modified since last sync
        batch_size: Number of records to process in each batch

    Returns:
        List of dicts with sync results
    """
    logger.info(
        f"Starting {'incremental' if incremental else 'full'} sales record sync"
    )
    log_data_sync_event(
        source="legacy_erp",
        destination="pyerp",
        record_count=0,
        status="started",
        details={
            "sync_type": "sales_records",
            "incremental": incremental,
            "batch_size": batch_size,
        },
    )

    results = []

    # Get or create mappings
    sales_record_mapping, sales_record_item_mapping = get_sales_record_mappings()

    if not sales_record_mapping or not sales_record_item_mapping:
        logger.info("Sales record mappings not found. Creating...")
        sales_record_mapping, sales_record_item_mapping = create_sales_record_mappings()

    # Sync sales records
    if sales_record_mapping:
        logger.info(
            f"Running sales record sync (mapping ID: {sales_record_mapping.id})"
        )
        record_result = run_entity_sync(
            mapping_id=sales_record_mapping.id,
            incremental=incremental,
            batch_size=batch_size,
        )
        results.append(record_result)

    # Sync line items
    if sales_record_item_mapping:
        logger.info(
            f"Running sales record line item sync (mapping ID: {sales_record_item_mapping.id})"
        )
        item_result = run_entity_sync(
            mapping_id=sales_record_item_mapping.id,
            incremental=incremental,
            batch_size=batch_size,
        )
        results.append(item_result)

    # Calculate total records processed
    total_records = sum(result.get("records_processed", 0) for result in results)

    log_data_sync_event(
        source="legacy_erp",
        destination="pyerp",
        record_count=total_records,
        status="completed",
        details={
            "sync_type": "sales_records",
            "incremental": incremental,
            "results": results,
        },
    )

    return results


@shared_task(name="sync.run_incremental_sales_record_sync")
def run_incremental_sales_record_sync() -> List[Dict]:
    """
    Run incremental sync for sales records (scheduled task).

    Returns:
        List of dicts with sync results
    """
    logger.info("Starting scheduled incremental sales record sync")
    log_data_sync_event(
        source="legacy_erp",
        destination="pyerp",
        record_count=0,
        status="scheduled",
        details={
            "sync_type": "sales_records",
            "incremental": True,
            "schedule": "15min",
        },
    )
    return run_sales_record_sync(incremental=True, batch_size=100)


# Configure as a periodic task
run_incremental_sales_record_sync.periodic_task = {
    "name": "sync.incremental_sales_record_sync",
    "schedule": crontab(minute="*/15"),  # Run every 15 minutes
    "options": {"expires": 900.0},  # Expire if not executed within 15 minutes
}


@shared_task(name="sync.run_full_sales_record_sync")
def run_full_sales_record_sync() -> List[Dict]:
    """
    Run full sync for sales records (scheduled task).

    Returns:
        List of dicts with sync results
    """
    logger.info("Starting scheduled full sales record sync")
    log_data_sync_event(
        source="legacy_erp",
        destination="pyerp",
        record_count=0,
        status="scheduled",
        details={
            "sync_type": "sales_records",
            "incremental": False,
            "schedule": "daily",
        },
    )
    return run_sales_record_sync(incremental=False, batch_size=100)


# Configure as a periodic task
run_full_sales_record_sync.periodic_task = {
    "name": "sync.full_sales_record_sync",
    "schedule": crontab(hour=3, minute=0),  # Run at 3:00 AM
    "options": {"expires": 3600.0},  # Expire if not executed within 1 hour
}


def _load_production_yaml() -> Dict:
    """Load production sync configuration from YAML file."""
    config_path = os.path.join(
        os.path.dirname(__file__), "config", "production_sync.yaml"
    )
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load production sync config: {e}")
        return {}


def get_production_mappings():
    """Get production order mappings from YAML configuration.
    
    Returns:
        Tuple containing (production_order_mapping, production_order_item_mapping)
    """
    config = _load_production_yaml()
    mappings = config.get("mappings", [])
    
    # Extract the production order and item mappings
    production_order_mapping = None
    production_order_item_mapping = None
    
    for mapping in mappings:
        if mapping.get("entity_type") == "production_order":
            production_order_mapping = mapping
        elif mapping.get("entity_type") == "production_order_item":
            production_order_item_mapping = mapping
    
    return production_order_mapping, production_order_item_mapping


def create_production_mappings():
    """Create or update production related sync mappings in the database.
    
    Returns:
        Tuple containing (production_order_mapping_id, production_order_item_mapping_id)
    """
    try:
        production_order_config, production_order_item_config = get_production_mappings()
        
        if not production_order_config or not production_order_item_config:
            logger.error("Production mapping configuration incomplete")
            return None, None
        
        # Create or update production order mapping
        production_order_mapping, _ = SyncMapping.objects.update_or_create(
            source__name=production_order_config["source"],
            target__name=production_order_config["target"],
            entity_type=production_order_config["entity_type"],
            defaults={"mapping_config": production_order_config["mapping_config"]},
        )
        
        # Create or update production order item mapping
        production_order_item_mapping, _ = SyncMapping.objects.update_or_create(
            source__name=production_order_item_config["source"],
            target__name=production_order_item_config["target"],
            entity_type=production_order_item_config["entity_type"],
            defaults={"mapping_config": production_order_item_config["mapping_config"]},
        )
        
        return production_order_mapping.id, production_order_item_mapping.id
    except Exception as e:
        logger.error(f"Failed to create production mappings: {e}")
        return None, None


@shared_task(name="sync.run_production_sync")
def run_production_sync(
    incremental: bool = True, batch_size: int = 100, query_params: Optional[Dict] = None
) -> List[Dict]:
    """Run synchronization for production data.
    
    This task synchronizes both production orders and production order items
    using the mappings defined in the production_sync.yaml configuration file.
    
    Args:
        incremental: If True, only sync new/updated records
        batch_size: Number of records to process in each batch
        query_params: Optional additional query parameters
    
    Returns:
        List of results from each sync operation
    """
    try:
        # Create or update mappings
        production_order_mapping_id, production_order_item_mapping_id = create_production_mappings()
        
        if not production_order_mapping_id or not production_order_item_mapping_id:
            logger.error("Unable to create production mappings")
            return [
                {"status": "error", "message": "Unable to create production mappings"}
            ]
        
        results = []
        
        # First, sync production orders
        logger.info("Starting production order sync")
        log_data_sync_event(
            source="legacy_erp",
            destination="pyerp",
            record_count=0,
            status="started",
            details={
                "entity_type": "production_order",
                "incremental": incremental,
                "batch_size": batch_size,
            },
        )
        
        production_order_result = run_entity_sync(
            mapping_id=production_order_mapping_id,
            incremental=incremental,
            batch_size=batch_size,
            query_params=query_params,
        )
        
        results.append(production_order_result)
        
        # Then, sync production order items
        logger.info("Starting production order item sync")
        log_data_sync_event(
            source="legacy_erp",
            destination="pyerp",
            record_count=0,
            status="started",
            details={
                "entity_type": "production_order_item",
                "incremental": incremental,
                "batch_size": batch_size,
            },
        )
        
        production_order_item_result = run_entity_sync(
            mapping_id=production_order_item_mapping_id,
            incremental=incremental,
            batch_size=batch_size,
            query_params=query_params,
        )
        
        results.append(production_order_item_result)
        
        return results
    except Exception as e:
        logger.error(f"Production sync failed: {e}")
        return [{"status": "error", "message": str(e)}]


@shared_task(name="sync.run_incremental_production_sync")
def run_incremental_production_sync(query_params: Optional[Dict] = None) -> List[Dict]:
    """Run incremental synchronization for production data.
    
    Synchronizes only new/updated records from the last successful sync.
    
    Args:
        query_params: Optional additional query parameters
    
    Returns:
        List of results from each sync operation
    """
    logger.info("Starting incremental production sync")
    return run_production_sync(incremental=True, query_params=query_params)


@shared_task(name="sync.run_full_production_sync")
def run_full_production_sync(query_params: Optional[Dict] = None) -> List[Dict]:
    """Run full synchronization for production data.
    
    Synchronizes all records regardless of when they were last updated.
    
    Args:
        query_params: Optional additional query parameters
    
    Returns:
        List of results from each sync operation
    """
    logger.info("Starting full production sync")
    return run_production_sync(incremental=False, query_params=query_params)


def _load_business_yaml() -> Dict:
    """Load business data sync configuration from YAML file."""
    config_path = os.path.join(
        os.path.dirname(__file__), "config", "business_sync.yaml"
    )
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load business sync config: {e}")
        return {}


def get_employee_mapping():
    """Get employee mapping from YAML configuration.
    
    Returns:
        Dict containing employee mapping configuration
    """
    config = _load_business_yaml()
    
    # Extract the employee mapping
    employee_mapping = config.get("employees", {})
    
    return employee_mapping


def create_employee_mapping():
    """Create employee mapping from YAML configuration.
    
    Returns:
        SyncMapping object for employee data
    """
    from .models import SyncSource, SyncTarget, SyncMapping
    
    # Load the configuration
    config = _load_business_yaml()
    employee_config = config.get("employees", {})
    
    if not employee_config:
        logger.error("Employee configuration not found in business_sync.yaml")
        return None
    
    # Get or create source
    source_config = employee_config.get("source", {}).get("config", {})
    source, _ = SyncSource.objects.get_or_create(
        name="legacy_erp",
        defaults={
            "description": "Legacy 4D ERP System",
            "config": source_config
        }
    )
    
    # Get or create target
    target, _ = SyncTarget.objects.get_or_create(
        name="django_models",
        defaults={
            "description": "Django ORM Models",
            "config": {"loader_class": "pyerp.sync.loaders.django_model.DjangoModelLoader"}
        }
    )
    
    # Create mapping
    mapping_config = {
        "transformer_class": employee_config.get("transformer", {}).get("class"),
        "field_mappings": employee_config.get("transformer", {}).get("config", {}).get("field_mappings", {}),
        "validation_rules": employee_config.get("transformer", {}).get("config", {}).get("validation_rules", []),
        "loader_config": employee_config.get("loader", {}).get("config", {})
    }
    
    mapping, created = SyncMapping.objects.get_or_create(
        source=source,
        target=target,
        entity_type="employee",
        defaults={
            "mapping_config": mapping_config,
            "active": True
        }
    )
    
    if created:
        logger.info("Created new employee mapping")
    else:
        # Update the mapping if it already exists
        mapping.mapping_config = mapping_config
        mapping.save()
        logger.info("Updated existing employee mapping")
    
    return mapping


@shared_task
def sync_employees(
    full_sync=False,
    filters=None,
):
    """Run the employee synchronization task.

    Args:
        full_sync (bool): If True, do a full sync instead of incremental.
        filters (dict): Optional filters to apply to the extraction.

    Returns:
        dict: Result status and details.
    """
    try:
        # Create config objects
        source_config = {
            "name": "legacy_erp",
            "extractor_class": "pyerp.sync.extractors.legacy_api.LegacyAPIExtractor",
            "config": {
                "environment": "test",
                "table_name": "Pers",
                "key_field": "__KEY"
            },
        }

        target_config = {
            "name": "django_models",
            "loader_class": "pyerp.sync.loaders.django_model.DjangoModelLoader",
            "config": {
                "app_label": "business",
                "model_name": "Employee",
            },
        }

        mapping_config = {
            "entity_type": "employee",
            "transformer_class": "pyerp.sync.transformers.employee.EmployeeTransformer",
            "field_mappings": {
                # Basic info
                "Pers_Nr": "employee_number",
                "Name": "last_name",
                "Vorname": "first_name",
                "eMail": "email",
                "AD_Name": "ad_username",
                
                # Contact details
                "Straße": "street", 
                "PLZ": "postal_code",
                "Ort": "city",
                "Telefon": "phone",
                "Telefon2": "mobile_phone",
                
                # Employment details
                "GebDatum": "birth_date",
                "Eintrittsdatum": "hire_date",
                "Austrittsdatum": "termination_date",
                "ausgeschieden": "is_terminated",
                "anwesend": "is_present",
                
                # Compensation and benefits
                "Geh_code": "salary_code",
                "Monatsgehalt": "monthly_salary",
                "Jahres_Gehalt": "annual_salary",
                "Arb_Std_Wo": "weekly_hours",
                "Arb_Std_Tag": "daily_hours",
                "Jahrs_Urlaub": "annual_vacation_days",
                
                # System fields for sync
                "__KEY": "legacy_id",
            },
        }

        # Get or create sync components from config
        source, created = SyncSource.objects.get_or_create(
            name=source_config["name"],
            defaults={
                "description": "Legacy 4D ERP System",
                "config": {
                    "extractor_class": source_config["extractor_class"],
                    "config": source_config["config"]
                },
                "active": True
            }
        )
        
        target, created = SyncTarget.objects.get_or_create(
            name=target_config["name"],
            defaults={
                "description": "Django ORM Models",
                "config": {
                    "loader_class": target_config["loader_class"],
                    "config": target_config["config"]
                },
                "active": True
            }
        )
        
        mapping, created = SyncMapping.objects.get_or_create(
            entity_type=mapping_config["entity_type"],
            source=source,
            target=target,
            defaults={
                "mapping_config": mapping_config,
            }
        )
        
        if not mapping:
            return {"status": "error", "message": "Failed to get or create mapping"}
        
        # Create and run the pipeline
        factory = PipelineFactory()
        pipeline = factory.create_pipeline(mapping)
        
        result = pipeline.run(
            incremental=not full_sync,  # Convert full_sync to incremental
            query_params=filters or {},  # Use query_params instead of filters
            batch_size=100
        )
        
        logger.info(
            "Employee sync completed: %d total, %d success, %d failed", 
            result.records_processed, 
            result.records_succeeded, 
            result.records_failed
        )
        
        return {
            "status": "success",
            "mapping_id": mapping.id,
            "sync_log_id": result.id,
            "records_processed": result.records_processed,
            "records_succeeded": result.records_succeeded,
            "records_failed": result.records_failed
        }
        
    except Exception as e:
        logger.exception("Error in employee sync task: %s", e)
        return {
            "status": "error",
            "message": str(e)
        }


@shared_task
def scheduled_employee_sync():
    """Scheduled task for incremental employee sync."""
    logger.info("Running scheduled incremental employee sync")
    return sync_employees(full_sync=False)


# Add periodic_task attribute for registration in AppConfig
scheduled_employee_sync.periodic_task = {
    "name": "sync-employees-every-5-min",
    "schedule": crontab(minute="*/5"),
    "options": {"expires": 60 * 4}  # Expires after 4 minutes
}


@shared_task
def nightly_full_employee_sync():
    """Nightly task for full employee sync."""
    logger.info("Running nightly full employee sync")
    return sync_employees(full_sync=True)


# Add periodic_task attribute for registration in AppConfig
nightly_full_employee_sync.periodic_task = {
    "name": "sync-employees-nightly",
    "schedule": crontab(hour=2, minute=15),  # Run at 2:15 AM
    "options": {"expires": 60 * 60 * 3}  # Expires after 3 hours
}
