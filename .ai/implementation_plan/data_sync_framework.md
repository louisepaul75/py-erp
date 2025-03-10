# Data Synchronization Framework Implementation Plan

## Overview

This document outlines the technical implementation plan for creating a scalable data synchronization framework to replace the current individual scripts for product import (`update_parent_products.py` and `update_variant_products.py`). The framework will enable synchronizing multiple data entities from the legacy 4D system to the new pyERP system, supporting both one-time imports and regular incremental updates.

## Current Architecture Analysis

The current approach uses individual scripts with the following characteristics:
- Separate scripts for parent products and variant products
- Direct use of SimpleAPIClient for data extraction
- Hard-coded field mappings within each script
- Manual execution of scripts
- Limited error handling and recovery
- No built-in scheduling or monitoring
- Full table processing rather than incremental updates

## Target Architecture

### 1. Modular ETL Components

#### Base Classes and Interfaces

```python
# Pseudocode for base classes

class BaseExtractor:
    """Base class for extracting data from source systems."""
    
    def __init__(self, config):
        self.config = config
        
    def connect(self):
        """Establish connection to data source."""
        raise NotImplementedError
        
    def extract(self, query_params=None):
        """Extract data based on query parameters."""
        raise NotImplementedError
        
    def close(self):
        """Close connection to data source."""
        raise NotImplementedError


class BaseTransformer:
    """Base class for transforming data between systems."""
    
    def __init__(self, config):
        self.config = config
        self.field_mappings = config.get('field_mappings', {})
        
    def transform(self, source_data):
        """Transform source data to target format."""
        raise NotImplementedError
        
    def validate(self, transformed_data):
        """Validate transformed data."""
        raise NotImplementedError


class BaseLoader:
    """Base class for loading data into target systems."""
    
    def __init__(self, config):
        self.config = config
        self.model = self._get_model()
        
    def _get_model(self):
        """Get Django model based on configuration."""
        raise NotImplementedError
        
    def load(self, transformed_data, update_existing=True):
        """Load transformed data into target system."""
        raise NotImplementedError
        
    def handle_conflicts(self, existing_record, new_data):
        """Handle conflicts between existing and new data."""
        raise NotImplementedError
```

#### Implementation Classes

```python
# Pseudocode for implementation classes

class APIExtractor(BaseExtractor):
    """Extractor for API data sources."""
    
    def connect(self):
        """Connect to API with authentication."""
        self.client = SimpleAPIClient(
            environment=self.config.get('environment', 'live'),
            client_id=self.config.get('client_id'),
            client_secret=self.config.get('client_secret')
        )
        
    def extract(self, query_params=None):
        """Extract data from API."""
        table_name = self.config.get('table_name')
        if not table_name:
            raise ValueError("Table name must be specified in config")
            
        filters = self.config.get('filters', {})
        if query_params:
            filters.update(query_params)
            
        return self.client.get_table_data(table_name, filters)


class ProductTransformer(BaseTransformer):
    """Transformer for product data."""
    
    def transform(self, source_data):
        """Transform product data."""
        transformed_records = []
        
        for record in source_data:
            transformed = {}
            # Apply field mappings
            for source_field, target_field in self.field_mappings.items():
                if source_field in record:
                    transformed[target_field] = record[source_field]
                    
            # Apply custom transformations
            for transformer_func in self.config.get('custom_transformers', []):
                transformed = transformer_func(transformed, record)
                
            transformed_records.append(transformed)
            
        return transformed_records
        
    def validate(self, transformed_data):
        """Validate transformed product data."""
        # Apply validation rules from config
        validation_errors = []
        
        for record in transformed_data:
            record_errors = {}
            for rule in self.config.get('validation_rules', []):
                field = rule.get('field')
                validator = rule.get('validator')
                
                if field in record and not validator(record[field]):
                    record_errors[field] = rule.get('error_message', 'Validation failed')
                    
            if record_errors:
                validation_errors.append({
                    'record': record,
                    'errors': record_errors
                })
                
        return validation_errors


class DjangoModelLoader(BaseLoader):
    """Loader for Django models."""
    
    def _get_model(self):
        """Get Django model from app and model name."""
        from django.apps import apps
        
        app_name = self.config.get('app_name')
        model_name = self.config.get('model_name')
        
        if not app_name or not model_name:
            raise ValueError("app_name and model_name must be specified in config")
            
        return apps.get_model(app_name, model_name)
        
    def load(self, transformed_data, update_existing=True):
        """Load transformed data into Django model."""
        from django.db import transaction
        
        results = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        unique_field = self.config.get('unique_field', 'id')
        
        with transaction.atomic():
            for record in transformed_data:
                try:
                    if unique_field not in record:
                        raise ValueError(f"Record missing unique field: {unique_field}")
                        
                    unique_value = record[unique_field]
                    existing = self.model.objects.filter(**{unique_field: unique_value}).first()
                    
                    if existing and update_existing:
                        # Update existing record
                        for field, value in record.items():
                            setattr(existing, field, value)
                        existing.save()
                        results['updated'] += 1
                    elif existing:
                        # Skip existing record
                        results['skipped'] += 1
                    else:
                        # Create new record
                        self.model.objects.create(**record)
                        results['created'] += 1
                except Exception as e:
                    results['errors'] += 1
                    logger.error(f"Error loading record: {e}")
                    
        return results
```

### 2. Configuration Structure

```yaml
# Example configuration for parent product sync
name: parent_product_sync
description: Synchronize parent products from legacy system

source:
  type: api
  extractor: APIExtractor
  config:
    environment: live
    table_name: Artikel_Familie
    filters:
      active: true

transformation:
  transformer: ProductTransformer
  field_mappings:
    Art_Nr: sku
    Art_Nr: base_sku
    Familie_ID: legacy_id
    Bezeichnung: name
    Bezeichnung_EN: name_en
    Beschreibung: description
    Beschreibung_EN: description_en
    Gewicht: weight
  custom_transformers:
    - transform_dimensions
    - transform_boolean_flags
  validation_rules:
    - field: sku
      validator: validate_sku_format
      error_message: Invalid SKU format
    - field: name
      validator: validate_not_empty
      error_message: Name cannot be empty

target:
  loader: DjangoModelLoader
  config:
    app_name: pyerp.products
    model_name: ParentProduct
    unique_field: sku
    conflict_strategy: newest_wins

scheduling:
  frequency: daily
  time: '02:00'
  dependencies:
    - category_sync

incremental:
  enabled: true
  timestamp_field: last_modified
  full_sync_fallback: true
```

### 3. Execution Framework

```python
# Pseudocode for sync task executor

class SyncTask:
    """A task for synchronizing data between systems."""
    
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        with open(config_path) as f:
            return yaml.safe_load(f)
            
    def _setup_logger(self):
        """Set up logger for this task."""
        logger_name = f"sync_task.{self.config.get('name', 'unnamed')}"
        logger = logging.getLogger(logger_name)
        # Configure logger
        return logger
        
    def _create_component(self, component_type, config):
        """Create a component (extractor, transformer, loader) from config."""
        component_class_name = config.get(f'{component_type}')
        component_module = importlib.import_module(f'pyerp.sync.{component_type}s')
        component_class = getattr(component_module, component_class_name)
        return component_class(config.get('config', {}))
        
    def execute(self, incremental=True):
        """Execute the sync task."""
        self.logger.info(f"Starting sync task: {self.config.get('name')}")
        
        start_time = time.time()
        stats = {
            'extracted': 0,
            'transformed': 0,
            'loaded': 0,
            'errors': 0
        }
        
        try:
            # Create components
            extractor = self._create_component('extractor', self.config.get('source', {}))
            transformer = self._create_component('transformer', self.config.get('transformation', {}))
            loader = self._create_component('loader', self.config.get('target', {}))
            
            # Set up query params for incremental sync
            query_params = None
            if incremental and self.config.get('incremental', {}).get('enabled', False):
                timestamp_field = self.config.get('incremental', {}).get('timestamp_field')
                last_sync = self._get_last_successful_sync()
                if last_sync and timestamp_field:
                    query_params = {timestamp_field: {'$gt': last_sync}}
            
            # Extract
            extractor.connect()
            source_data = extractor.extract(query_params)
            stats['extracted'] = len(source_data)
            self.logger.info(f"Extracted {stats['extracted']} records")
            
            # Transform
            transformed_data = transformer.transform(source_data)
            validation_errors = transformer.validate(transformed_data)
            
            if validation_errors:
                self.logger.warning(f"Found {len(validation_errors)} validation errors")
                stats['errors'] += len(validation_errors)
                
            valid_data = [record for i, record in enumerate(transformed_data) 
                         if i not in [e['record'] for e in validation_errors]]
            stats['transformed'] = len(valid_data)
            self.logger.info(f"Transformed {stats['transformed']} valid records")
            
            # Load
            update_existing = self.config.get('target', {}).get('config', {}).get('update_existing', True)
            load_results = loader.load(valid_data, update_existing)
            stats.update(load_results)
            
            # Record successful sync
            self._record_successful_sync()
            
            self.logger.info(f"Sync task completed successfully in {time.time() - start_time:.2f} seconds")
            self.logger.info(f"Stats: {stats}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Sync task failed: {e}")
            stats['errors'] += 1
            return stats
            
    def _get_last_successful_sync(self):
        """Get timestamp of last successful sync."""
        # Implementation depends on how you track sync history
        pass
        
    def _record_successful_sync(self):
        """Record a successful sync."""
        # Implementation depends on how you track sync history
        pass


# Celery task for scheduled execution
@shared_task
def execute_sync_task(config_path):
    """Execute a sync task with the given configuration."""
    task = SyncTask(config_path)
    return task.execute()


# Django management command
class Command(BaseCommand):
    help = 'Execute a data synchronization task'
    
    def add_arguments(self, parser):
        parser.add_argument('config', help='Path to configuration file')
        parser.add_argument('--full', action='store_true', help='Perform full sync instead of incremental')
        
    def handle(self, *args, **options):
        config_path = options['config']
        incremental = not options['full']
        
        task = SyncTask(config_path)
        stats = task.execute(incremental=incremental)
        
        self.stdout.write(self.style.SUCCESS(f"Sync completed: {stats}"))
```

### 4. Scheduling Infrastructure

```python
# Celery configuration
app = Celery('pyerp')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Schedule configuration for Celery Beat
app.conf.beat_schedule = {
    'sync-parent-products': {
        'task': 'pyerp.sync.tasks.execute_sync_task',
        'schedule': crontab(hour=2, minute=0),  # Run at 2:00 AM
        'args': ['/path/to/parent_product_sync.yaml'],
    },
    'sync-variant-products': {
        'task': 'pyerp.sync.tasks.execute_sync_task',
        'schedule': crontab(hour=3, minute=0),  # Run at 3:00 AM
        'args': ['/path/to/variant_product_sync.yaml'],
    },
    # Additional sync tasks...
}

# Airflow DAG for complex workflows
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'pyerp',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'product_sync_workflow',
    default_args=default_args,
    description='Synchronize product data from legacy system',
    schedule_interval=timedelta(days=1),
)

def run_sync_task(config_path, **context):
    from pyerp.sync.tasks import execute_sync_task
    return execute_sync_task(config_path)

# Tasks with dependencies
t1 = PythonOperator(
    task_id='sync_categories',
    python_callable=run_sync_task,
    op_kwargs={'config_path': '/path/to/category_sync.yaml'},
    dag=dag,
)

t2 = PythonOperator(
    task_id='sync_parent_products',
    python_callable=run_sync_task,
    op_kwargs={'config_path': '/path/to/parent_product_sync.yaml'},
    dag=dag,
)

t3 = PythonOperator(
    task_id='sync_variant_products',
    python_callable=run_sync_task,
    op_kwargs={'config_path': '/path/to/variant_product_sync.yaml'},
    dag=dag,
)

# Define task dependencies
t1 >> t2 >> t3
```

### 5. Monitoring and Reporting

```python
# Model for tracking sync history
class SyncHistory(models.Model):
    """Track history of sync tasks."""
    
    task_name = models.CharField(max_length=100)
    config_path = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='running'
    )
    stats = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.task_name} - {self.started_at}"
        
    def duration(self):
        """Calculate task duration."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# Admin interface for monitoring
@admin.register(SyncHistory)
class SyncHistoryAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'started_at', 'completed_at', 'status', 'duration_display']
    list_filter = ['task_name', 'status', 'started_at']
    search_fields = ['task_name', 'error_message']
    readonly_fields = ['task_name', 'config_path', 'started_at', 'completed_at', 
                      'status', 'stats', 'error_message', 'duration_display']
                      
    def duration_display(self, obj):
        duration = obj.duration()
        if duration is not None:
            return f"{duration:.2f} seconds"
        return "-"
    duration_display.short_description = "Duration"


# API endpoint for monitoring
class SyncHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SyncHistory.objects.all()
    serializer_class = SyncHistorySerializer
    filter_backends = [filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task_name', 'status']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
```

## Migration Plan

### Phase 1: Framework Foundation (4 weeks)

#### Week 1-2: Base Architecture
1. Create package structure for the sync framework
2. Implement base classes for Extractor, Transformer, and Loader
3. Develop configuration schema and parsing
4. Set up logging and metrics collection

#### Week 3-4: Initial Implementation
1. Create API/SimpleAPIClient extractor implementation
2. Implement basic transformers with field mapping
3. Develop Django model loader with transaction support
4. Convert existing parent_product script to use the framework

### Phase 2: Scheduling & Orchestration (3 weeks)

#### Week 5-6: Scheduling Infrastructure
1. Set up Celery integration
2. Implement task scheduling via Celery Beat
3. Create management commands for manual execution
4. Develop task dependencies and workflow management

#### Week 7: Advanced Orchestration
1. Set up Airflow for complex workflows (if needed)
2. Implement conditional execution based on task success/failure
3. Create job monitoring and alerting

### Phase 3: Resilience & Monitoring (3 weeks)

#### Week 8-9: Monitoring & Reporting
1. Implement SyncHistory model for tracking tasks
2. Create admin interface for monitoring
3. Develop dashboard for visualization
4. Set up alerting for failed tasks

#### Week 10: Error Handling & Recovery
1. Enhance error handling with detailed context
2. Implement retry logic with backoff
3. Create error classification and reporting
4. Develop manual recovery procedures

### Phase 4: Incremental Updates (2 weeks)

#### Week 11: Change Detection
1. Implement timestamp-based delta sync
2. Create checksum/hash comparison for change detection
3. Develop tracking for last successful sync

#### Week 12: Conflict Resolution
1. Implement conflict detection
2. Create configurable resolution strategies
3. Add manual override capability
4. Test with real-world scenarios

## Rollout Strategy

1. **Development Phase**
   - Implement framework in development environment
   - Convert existing scripts one at a time
   - Test with sample data

2. **Testing Phase**
   - Deploy to staging environment
   - Run parallel with existing scripts
   - Compare results for accuracy

3. **Production Rollout**
   - Deploy framework to production
   - Migrate one entity type at a time
   - Monitor closely for issues
   - Keep existing scripts as fallback

4. **Full Adoption**
   - Migrate all entity types to new framework
   - Implement scheduled execution
   - Retire legacy scripts
   - Continuous monitoring and improvement

## Resources Required

- 1 Senior Developer (4-6 weeks full-time)
- 1 Junior Developer (12 weeks full-time)
- Access to staging environment
- Access to legacy system APIs
- Time for stakeholder reviews

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complexity of framework slows development | Schedule delays | Start with minimal viable framework, add features incrementally |
| Compatibility issues with legacy APIs | Data integrity issues | Thorough testing with sample data, fallback to original scripts |
| Performance issues with large datasets | System overload | Implement batch processing, optimize queries, schedule during off-hours |
| Dependency on external systems (Celery, Airflow) | Increased maintenance | Start with simple scheduling (cron), add complexity as needed |
| Data inconsistencies during transition | Business impact | Run parallel systems, verify data integrity before full cutover |

## Success Metrics

1. **Efficiency Improvements**
   - Reduction in manual intervention for data synchronization
   - Decrease in sync execution time

2. **Data Quality**
   - Reduction in data inconsistencies
   - Improved error detection and reporting

3. **Maintenance Metrics**
   - Reduction in code duplication
   - Ease of adding new entity types

4. **Operational Metrics**
   - Percentage of successful automated syncs
   - Mean time to detect and resolve sync issues 