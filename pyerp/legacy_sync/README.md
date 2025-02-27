# Legacy ERP Synchronization

This Django app provides functionality for synchronizing data between the legacy 4D-based ERP system and the new Django-based ERP system.

## Overview

The legacy_sync app is designed to handle the migration and ongoing synchronization of data from the legacy 4D-based ERP system to the new Django-based ERP system. It provides a flexible and configurable approach to mapping data between the two systems, even when their data structures differ significantly.

## Features

- Configurable entity mapping between legacy and new systems
- Field-level transformations for data conversion
- Synchronization logging and error tracking
- Management command for manual synchronization
- Celery tasks for scheduled synchronization
- Admin interface for managing mappings and transformations

## Setup

1. Ensure the WSZ_api package is available at the path specified in `api_client.py`
2. Run migrations to create the necessary database tables:
   ```
   python manage.py migrate legacy_sync
   ```
3. Configure entity mappings in the admin interface

## Usage

### Configuring Entity Mappings

Before synchronizing data, you need to configure entity mappings in the admin interface:

1. Go to Admin > Legacy ERP Synchronization > Entity Mapping Configurations
2. Create a new mapping for each entity type you want to synchronize
3. Specify the legacy table name, new model path, and field mappings

Example field mapping JSON:

```json
{
  "name": {
    "new_field": "name",
    "required": true
  },
  "description": {
    "new_field": "description",
    "required": false
  },
  "price": {
    "new_field": "unit_price",
    "transform": "to_float",
    "required": true
  },
  "active": {
    "new_field": "is_active",
    "transform": "to_boolean",
    "required": false
  }
}
```

### Creating Custom Transformations

You can create custom transformation functions for complex data conversions:

1. Go to Admin > Legacy ERP Synchronization > Transformation Functions
2. Create a new transformation function with a unique name
3. Write Python code that sets a `result` variable based on the input `value`

Example transformation function:

```python
# Convert a legacy status code to a new status string
if value == 1:
    result = "active"
elif value == 2:
    result = "inactive"
elif value == 3:
    result = "pending"
else:
    result = "unknown"
```

### Running Synchronization

#### Using the Management Command

You can run synchronization manually using the management command:

```bash
# List available entity types
python manage.py sync_legacy_data --list

# Sync a specific entity type
python manage.py sync_legacy_data --entity product

# Sync only new or modified records
python manage.py sync_legacy_data --entity product --new-only

# Sync all entity types
python manage.py sync_legacy_data

# Force synchronization even if there are errors
python manage.py sync_legacy_data --force
```

#### Using Celery Tasks

You can schedule synchronization using Celery tasks:

```python
from pyerp.legacy_sync.tasks import sync_products_task, sync_all_task

# Sync products
sync_products_task.delay(new_only=True)

# Sync all entity types
sync_all_task.delay(new_only=True)
```

## Models

### SyncLog

Logs synchronization operations and their results.

### EntityMapping

Maps entities between the legacy and new systems.

### EntityMappingConfig

Configures how entities and their fields are mapped between systems.

### TransformationFunction

Defines custom transformation functions for data conversion.

## API Client

The `api_client.py` module provides a wrapper around the WSZ_api package for interacting with the legacy system. It handles authentication, data fetching, and error handling.

## Sync Tasks

The `sync_tasks.py` module provides functions for synchronizing different types of entities between the systems. It uses the entity mapping configurations to transform data from the legacy format to the new format.

## Management Command

The `sync_legacy_data` management command provides a command-line interface for running synchronization operations.

## Celery Tasks

The `tasks.py` module provides Celery tasks for scheduled synchronization operations.

## Admin Interface

The admin interface provides a user-friendly way to manage entity mappings, transformation functions, and view synchronization logs. 