# Sync System

A modular ETL-based system for synchronizing data between different systems (legacy ERP, webshop, POS, etc.) and the Django-based ERP.

## Architecture

The sync system follows an ETL (Extract, Transform, Load) architecture with these key components:

- **Extractors**: Pull data from source systems (e.g., legacy ERP API)
- **Transformers**: Convert data between formats
- **Loaders**: Load data into target systems (e.g., Django models)
- **Pipelines**: Orchestrate the ETL process
- **Tasks**: Schedule and execute sync operations

## Key Features

- Modular design for easy extension to new source/target systems
- Incremental sync using date-based filtering
- Batched processing for large datasets
- Comprehensive logging and error tracking
- Scheduled tasks (5-minute incremental sync, nightly full sync)

## Configuration

### Setting Up Sync Mappings

1. Create a `SyncSource` for each data source:
   - Legacy ERP
   - Webshop API
   - POS System
   - etc.

2. Create a `SyncTarget` for each data target:
   - Django models
   - External APIs
   - etc.

3. Create a `SyncMapping` for each entity type:
   - Map products from legacy ERP to Django models
   - Map customers from webshop to Django models
   - etc.

Example configuration:

```python
# Create a source
legacy_erp = SyncSource.objects.create(
    name='legacy_erp',
    description='Legacy 4D ERP System',
    config={
        'environment': 'production',
        'extractor_class': 'pyerp.sync.extractors.legacy_api.LegacyAPIExtractor',
        'page_size': 100
    }
)

# Create a target
django_models = SyncTarget.objects.create(
    name='django_models',
    description='Django ORM Models',
    config={
        'loader_class': 'pyerp.sync.loaders.django_model.DjangoModelLoader'
    }
)

# Create a mapping
product_mapping = SyncMapping.objects.create(
    source=legacy_erp,
    target=django_models,
    entity_type='product',
    mapping_config={
        'transformer_class': 'pyerp.sync.transformers.product.ProductTransformer',
        'model_path': 'pyerp.products.models.Product',
        'fields': {
            'product_id': {'target_field': 'legacy_id'},
            'name': {'target_field': 'name'},
            'description': {'target_field': 'description'},
            'price': {'target_field': 'base_price', 'transform': 'to_decimal'},
            # ...
        }
    }
)
```

## Usage

### Management Command

You can run sync operations using the management command:

```bash
# List available mappings
python manage.py run_sync --list

# Run incremental sync for a specific mapping
python manage.py run_sync --mapping=1

# Run full sync for all product mappings
python manage.py run_sync --entity-type=product --full

# Run incremental sync for all mappings from a specific source
python manage.py run_sync --source=legacy_erp

# Add filters
python manage.py run_sync --mapping=1 --filters='{"status": "active"}'

# Debug mode
python manage.py run_sync --mapping=1 --debug
```

### Scheduled Tasks

The system has two scheduled tasks:

1. **Incremental Sync (Every 5 minutes)**
   - Only syncs records modified since the last successful sync
   - Uses date-based filtering for efficiency

2. **Full Sync (Nightly at 2:00 AM)**
   - Syncs all records regardless of modification date
   - Ensures complete consistency between systems

## Extending the System

### Adding a New Source

1. Create a new extractor class in `extractors/`
2. Implement the required methods from `BaseExtractor`
3. Create a `SyncSource` with the appropriate configuration

### Adding a New Entity Type

1. Create a new transformer class in `transformers/`
2. Implement the required methods from `BaseTransformer`
3. Create a `SyncMapping` with the appropriate configuration

### Adding a New Target

1. Create a new loader class in `loaders/`
2. Implement the required methods from `BaseLoader`
3. Create a `SyncTarget` with the appropriate configuration

## Monitoring and Maintenance

- Check the Django admin for `SyncLog` entries
- Review the logs for error messages
- Monitor the `SyncState` records to ensure syncs are occurring regularly
- Use the management command with `--list` to see available mappings 

## Recent Updates (March 2025)

### Improved Legacy API Integration

- Fixed date filtering by updating the default field name from 'Modified' to 'modified_date'
- Enhanced error handling for API connections
- Improved pagination support for large datasets

### Data Model Enhancements

- Increased `record_id` field length in `SyncLogDetail` model from 100 to 255 characters
- Added support for longer IDs from legacy systems
- Applied database migrations for schema changes

### Robust Data Transformation

- Implemented enhanced JSON data cleaning functionality
- Added support for handling NaN values and infinities
- Improved handling of non-serializable data types (datetime objects, numpy types)

### Testing and Validation

- Created comprehensive test scripts for validating the ETL pipeline
- Added test cases for real legacy API connections
- Implemented test environments for simulating different sync scenarios

### Documentation Updates

- Enhanced code documentation with detailed docstrings
- Updated README with latest configuration options
- Created usage examples for common sync operations 