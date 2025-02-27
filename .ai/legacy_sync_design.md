# Legacy ERP Sync Module - Technical Design

## Overview
The Legacy ERP Sync module is responsible for extracting data from the 4D-based legacy ERP system and importing it into the new Django-based ERP system. This module enables a one-way synchronization path that will support the incremental development and deployment of the new system while maintaining data consistency.

## Goals
1. Create a reliable connection to the legacy 4D ERP system
2. Extract data from legacy system tables with proper error handling
3. Transform legacy data to fit the new system's schema
4. Support both full and incremental synchronization
5. Provide monitoring and logging of sync operations
6. Enable scheduling of automatic sync jobs
7. Build validation tools to verify data integrity

## Components

### 1. Legacy API Client (`legacy_sync.api`)

#### `client.py`
```python
class Legacy4DClient:
    """Client for connecting to the 4D legacy ERP API."""
    
    def __init__(self, host, port, username, password, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = None
        
    def connect(self):
        """Establish connection to the 4D ERP API."""
        # Implementation depends on 4D API specifics
        
    def disconnect(self):
        """Close the connection to the 4D ERP API."""
        # Implementation depends on 4D API specifics
        
    def query_table(self, table_name, filters=None, fields=None, limit=None, offset=None):
        """Query data from a specific table in the legacy ERP.
        
        Args:
            table_name (str): Name of the table to query
            filters (dict, optional): Filtering conditions
            fields (list, optional): Specific fields to retrieve
            limit (int, optional): Maximum number of records to return
            offset (int, optional): Offset for pagination
            
        Returns:
            list: List of dictionaries containing the retrieved records
        """
        # Implementation depends on 4D API specifics
        
    def get_record(self, table_name, record_id, fields=None):
        """Retrieve a specific record by ID.
        
        Args:
            table_name (str): Name of the table
            record_id: Primary key value of the record
            fields (list, optional): Specific fields to retrieve
            
        Returns:
            dict: Dictionary containing the record data
        """
        # Implementation depends on 4D API specifics
```

#### `endpoints.py`
```python
"""
Definitions of legacy ERP endpoints and table structures.
This module will contain constants and mappings for the legacy system.
"""

# Table names in the legacy system
LEGACY_TABLES = {
    'PRODUCTS': 'Products',
    'CUSTOMERS': 'Customers',
    'ORDERS': 'Orders',
    'INVOICES': 'Invoices',
    'INVENTORY': 'Inventory',
    'BOM': 'BillOfMaterials',
    # Add other tables as needed
}

# Field mappings for legacy tables
LEGACY_FIELDS = {
    'PRODUCTS': {
        'id': 'ProductID',
        'name': 'ProductName',
        'description': 'Description',
        'sku': 'SKU',
        'category': 'Category',
        'price': 'Price',
        'cost': 'Cost',
        'tax_rate': 'TaxRate',
        # Add other fields as needed
    },
    # Add field mappings for other tables as needed
}
```

### 2. Data Synchronization Models (`legacy_sync.models`)

```python
from django.db import models
from django.utils import timezone

class SyncLog(models.Model):
    """Log of synchronization operations."""
    
    SYNC_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('PARTIALLY_COMPLETED', 'Partially Completed'),
    ]
    
    table_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='PENDING')
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Sync {self.table_name} - {self.status} ({self.created_at})"
    
    def mark_as_running(self):
        self.status = 'RUNNING'
        self.start_time = timezone.now()
        self.save()
        
    def mark_as_completed(self, records_processed, records_created, records_updated, records_failed):
        self.status = 'COMPLETED' if records_failed == 0 else 'PARTIALLY_COMPLETED'
        self.records_processed = records_processed
        self.records_created = records_created
        self.records_updated = records_updated
        self.records_failed = records_failed
        self.end_time = timezone.now()
        self.save()
        
    def mark_as_failed(self, error_message):
        self.status = 'FAILED'
        self.error_message = error_message
        self.end_time = timezone.now()
        self.save()


class SyncError(models.Model):
    """Detailed error records for sync operations."""
    
    sync_log = models.ForeignKey(SyncLog, on_delete=models.CASCADE, related_name='errors')
    record_id = models.CharField(max_length=100)
    error_message = models.TextField()
    record_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Error in {self.sync_log.table_name} - Record {self.record_id}"
```

### 3. Data Mappers (`legacy_sync.services.mappers`)

```python
class BaseMapper:
    """Base class for mapping legacy data to new system models."""
    
    def __init__(self, legacy_record):
        self.legacy_record = legacy_record
        self.errors = []
        
    def map(self):
        """Map the legacy record to the format for the new system.
        
        Returns:
            dict: Data for the new system
        """
        raise NotImplementedError("Subclasses must implement map method")
        
    def validate(self, mapped_data):
        """Validate the mapped data before saving.
        
        Args:
            mapped_data (dict): The mapped data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate method")
```

Product mapper example:
```python
from .base import BaseMapper
from products.models import Product, Category

class ProductMapper(BaseMapper):
    """Maps legacy product data to the new Product model."""
    
    def map(self):
        """Map legacy product fields to new product fields."""
        legacy_data = self.legacy_record
        
        # Get or create category
        category = None
        if 'Category' in legacy_data and legacy_data['Category']:
            category, _ = Category.objects.get_or_create(
                name=legacy_data['Category'],
                defaults={'description': f"Imported from legacy: {legacy_data['Category']}"}
            )
        
        # Map to new product fields
        mapped_data = {
            'legacy_id': legacy_data.get('ProductID'),
            'name': legacy_data.get('ProductName', ''),
            'description': legacy_data.get('Description', ''),
            'sku': legacy_data.get('SKU', ''),
            'category': category,
            'list_price': legacy_data.get('Price', 0.0),
            'cost_price': legacy_data.get('Cost', 0.0),
            'tax_rate': legacy_data.get('TaxRate', 0.0),
            'is_active': True,  # Default to active
            'is_purchased': bool(legacy_data.get('IsPurchased', False)),
            'is_manufactured': bool(legacy_data.get('IsManufactured', False)),
        }
        
        return mapped_data
    
    def validate(self, mapped_data):
        """Validate the mapped product data."""
        # Basic validation
        if not mapped_data.get('name'):
            self.errors.append("Product name is required")
            return False
            
        if not mapped_data.get('sku'):
            self.errors.append("SKU is required")
            return False
            
        # Check for duplicate SKU
        if Product.objects.filter(sku=mapped_data['sku']).exclude(
            legacy_id=mapped_data.get('legacy_id')
        ).exists():
            self.errors.append(f"Duplicate SKU: {mapped_data['sku']}")
            return False
            
        return True
```

### 4. Sync Services (`legacy_sync.services`)

```python
import logging
from django.db import transaction
from django.utils import timezone

from ..api.client import Legacy4DClient
from ..api.endpoints import LEGACY_TABLES
from ..models import SyncLog, SyncError
from .mappers import ProductMapper, CustomerMapper  # Import other mappers as needed

logger = logging.getLogger(__name__)

class SyncService:
    """Base service for synchronizing data from legacy ERP."""
    
    def __init__(self, api_client=None):
        self.api_client = api_client or Legacy4DClient(
            host=settings.LEGACY_API_HOST,
            port=settings.LEGACY_API_PORT,
            username=settings.LEGACY_API_USERNAME,
            password=settings.LEGACY_API_PASSWORD,
        )
        
    def sync_table(self, table_name, model_class, mapper_class, batch_size=100, filters=None):
        """Synchronize data from a legacy table to a Django model.
        
        Args:
            table_name (str): Name of the legacy table
            model_class: Django model class for the new system
            mapper_class: Mapper class for transforming the data
            batch_size (int): Number of records to process in each batch
            filters (dict, optional): Filters to apply to the legacy data query
            
        Returns:
            SyncLog: Log of the synchronization operation
        """
        # Create sync log
        sync_log = SyncLog.objects.create(table_name=table_name)
        sync_log.mark_as_running()
        
        try:
            # Connect to legacy API
            self.api_client.connect()
            
            # Get total record count for progress tracking
            offset = 0
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            
            # Process records in batches
            while True:
                # Get batch of records from legacy system
                legacy_records = self.api_client.query_table(
                    table_name=table_name,
                    filters=filters,
                    limit=batch_size,
                    offset=offset
                )
                
                if not legacy_records:
                    break
                    
                # Process batch
                for legacy_record in legacy_records:
                    try:
                        with transaction.atomic():
                            # Map legacy record to new format
                            mapper = mapper_class(legacy_record)
                            mapped_data = mapper.map()
                            
                            # Validate mapped data
                            if not mapper.validate(mapped_data):
                                raise ValueError(f"Validation failed: {', '.join(mapper.errors)}")
                                
                            # Get or create record in new system
                            legacy_id = str(legacy_record.get('id') or legacy_record.get('ID'))
                            obj, created = model_class.objects.update_or_create(
                                legacy_id=legacy_id,
                                defaults=mapped_data
                            )
                            
                            if created:
                                records_created += 1
                            else:
                                records_updated += 1
                                
                    except Exception as e:
                        records_failed += 1
                        logger.exception(f"Error syncing {table_name} record: {str(e)}")
                        
                        # Log the error
                        SyncError.objects.create(
                            sync_log=sync_log,
                            record_id=legacy_id,
                            error_message=str(e),
                            record_data=legacy_record
                        )
                        
                    finally:
                        records_processed += 1
                        
                # Update offset for next batch
                offset += len(legacy_records)
                
                # Update sync log with progress
                sync_log.records_processed = records_processed
                sync_log.records_created = records_created
                sync_log.records_updated = records_updated
                sync_log.records_failed = records_failed
                sync_log.save()
                
            # Mark sync as completed
            sync_log.mark_as_completed(
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed
            )
            
        except Exception as e:
            logger.exception(f"Error syncing {table_name}: {str(e)}")
            sync_log.mark_as_failed(str(e))
            
        finally:
            # Disconnect from legacy API
            self.api_client.disconnect()
            
        return sync_log
```

### 5. Management Commands (`legacy_sync.management.commands`)

```python
from django.core.management.base import BaseCommand
from django.conf import settings

from products.models import Product
from ...api.client import Legacy4DClient
from ...api.endpoints import LEGACY_TABLES
from ...services import SyncService
from ...services.mappers import ProductMapper

class Command(BaseCommand):
    help = 'Sync products from legacy ERP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform a full sync of all records',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting product synchronization...'))
        
        # Create API client
        client = Legacy4DClient(
            host=settings.LEGACY_API_HOST,
            port=settings.LEGACY_API_PORT,
            username=settings.LEGACY_API_USERNAME,
            password=settings.LEGACY_API_PASSWORD,
        )
        
        # Create sync service
        sync_service = SyncService(api_client=client)
        
        # Determine filters
        filters = None
        if not options['full']:
            # For incremental sync, get products updated since last sync
            # Logic to determine latest sync time would go here
            pass
            
        # Perform sync
        sync_log = sync_service.sync_table(
            table_name=LEGACY_TABLES['PRODUCTS'],
            model_class=Product,
            mapper_class=ProductMapper,
            filters=filters
        )
        
        # Output results
        self.stdout.write(self.style.SUCCESS(
            f'Product sync completed: '
            f'{sync_log.records_created} created, '
            f'{sync_log.records_updated} updated, '
            f'{sync_log.records_failed} failed'
        ))
        
        if sync_log.records_failed > 0:
            self.stdout.write(self.style.WARNING(
                f'There were {sync_log.records_failed} errors during sync. '
                f'Check the admin interface for details.'
            ))
```

### 6. Admin Interface (`legacy_sync.admin`)

```python
from django.contrib import admin
from .models import SyncLog, SyncError

class SyncErrorInline(admin.TabularInline):
    model = SyncError
    extra = 0
    readonly_fields = ['record_id', 'error_message', 'created_at']
    fields = readonly_fields
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['table_name', 'status', 'records_processed', 'records_created', 
                   'records_updated', 'records_failed', 'start_time', 'end_time']
    list_filter = ['status', 'table_name']
    search_fields = ['table_name']
    readonly_fields = ['table_name', 'status', 'records_processed', 'records_created',
                      'records_updated', 'records_failed', 'start_time', 'end_time',
                      'error_message', 'created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['table_name', 'status', 'error_message']
        }),
        ('Statistics', {
            'fields': ['records_processed', 'records_created', 'records_updated', 'records_failed']
        }),
        ('Timing', {
            'fields': ['start_time', 'end_time', 'created_at', 'updated_at']
        }),
    ]
    inlines = [SyncErrorInline]
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
```

### 7. Celery Tasks (`legacy_sync.tasks`)

```python
from celery import shared_task
from django.conf import settings

from products.models import Product
from .api.client import Legacy4DClient
from .api.endpoints import LEGACY_TABLES
from .services import SyncService
from .services.mappers import ProductMapper

@shared_task
def sync_products(full_sync=False):
    """Synchronize products from legacy ERP."""
    # Create API client
    client = Legacy4DClient(
        host=settings.LEGACY_API_HOST,
        port=settings.LEGACY_API_PORT,
        username=settings.LEGACY_API_USERNAME,
        password=settings.LEGACY_API_PASSWORD,
    )
    
    # Create sync service
    sync_service = SyncService(api_client=client)
    
    # Determine filters
    filters = None
    if not full_sync:
        # For incremental sync, get products updated since last sync
        # Logic to determine latest sync time would go here
        pass
        
    # Perform sync
    sync_log = sync_service.sync_table(
        table_name=LEGACY_TABLES['PRODUCTS'],
        model_class=Product,
        mapper_class=ProductMapper,
        filters=filters
    )
    
    return {
        'table': sync_log.table_name,
        'status': sync_log.status,
        'created': sync_log.records_created,
        'updated': sync_log.records_updated,
        'failed': sync_log.records_failed,
    }
```

## API Configuration
The Legacy ERP Sync module requires proper configuration to connect to the 4D legacy system. Add these settings to your Django settings:

```python
# Legacy ERP API settings
LEGACY_API_HOST = os.environ.get('LEGACY_API_HOST', 'localhost')
LEGACY_API_PORT = int(os.environ.get('LEGACY_API_PORT', '8080'))
LEGACY_API_USERNAME = os.environ.get('LEGACY_API_USERNAME', '')
LEGACY_API_PASSWORD = os.environ.get('LEGACY_API_PASSWORD', '')
LEGACY_API_TIMEOUT = int(os.environ.get('LEGACY_API_TIMEOUT', '30'))

# Sync settings
LEGACY_SYNC_BATCH_SIZE = int(os.environ.get('LEGACY_SYNC_BATCH_SIZE', '100'))
```

## Testing Strategy

### Unit Tests
1. Test API client connection and query methods
2. Test data mappers for proper transformations
3. Test validation logic in mappers
4. Test sync service with mocked API client

### Integration Tests
1. Test end-to-end sync with test data
2. Test error handling and recovery
3. Test admin interface functionality

## Implementation Plan

1. Set up project structure with Django configuration
2. Implement core models for tracking sync operations
3. Create API client for connecting to legacy 4D system
4. Implement mapper classes for data transformation
5. Build sync service for orchestrating the synchronization
6. Add management commands for manual sync operations
7. Create admin interface for monitoring and control
8. Implement Celery tasks for scheduled sync jobs 