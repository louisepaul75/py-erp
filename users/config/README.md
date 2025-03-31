# Permission Categorization in pyERP

This directory contains the configuration files for the permission categorization system. The most important file is `permissions_mapping.json`, which serves as the central configuration for mapping permissions to categories.

## Files

- `permissions_mapping.json` - Contains the mapping of all permissions to their categories and subcategories.

## When to Run the Synchronization

The permission synchronization should be run in the following scenarios:

1. **After System Installation**: Run a full synchronization to create the initial configuration
2. **After Adding New Apps/Models**: Any time new models (and their corresponding permissions) are added to the system
3. **After Database Migrations**: Especially migrations that affect permission-related models
4. **After Manual Edits** to the `permissions_mapping.json` file
5. **During CI/CD Pipelines**: To ensure consistency between environments

## What Gets Synchronized

The synchronization process handles:

1. **Database to JSON**: Exports all permissions from the Django database to the JSON configuration file
2. **Categorization**: Organizes permissions into logical categories and subcategories based on patterns
3. **JSON to Database**: Imports the category structure and permission assignments back to the database
4. **Diff Check**: Identifies permissions in the database that aren't yet in the JSON file

## Usage

The system uses a management command to synchronize permissions between the database and the JSON configuration file.

### Exporting Permissions

To export all current permissions from the database to the JSON file:

```bash
python manage.py sync_permissions --export-only
```
Use this when you want to update the JSON file with new permissions from the database, but don't want to modify the database.

### Automatic Categorization

To automatically categorize permissions based on predefined patterns:

```bash
python manage.py sync_permissions --categorize
```
Use this to organize permissions into logical categories and subcategories based on their app and model names.

### Importing Permissions

To import the permissions defined in the JSON file into the database:

```bash
python manage.py sync_permissions --import-only
```
Use this after manually editing the JSON file to apply your changes to the database.

### Complete Synchronization

For regular use (export, diff-check, and import):

```bash
python manage.py sync_permissions
```
This is the most common command that performs a full synchronization cycle.

## Structure of the JSON File

The JSON file has the following format:

```json
{
    "app_label.codename": {
        "id": 1,
        "name": "Permission Name",
        "codename": "codename",
        "content_type": "app_label.model",
        "category": "Warehouse",
        "subcategory": "Inventory",
        "order": 0
    },
    ...
}
```

## Hierarchical Categories

The permission system supports a hierarchical structure with main categories and subcategories:

### Main Categories
- Users & Access
- Warehouse
- Sales
- Purchasing
- Production
- Finance
- System
- Others

### Subcategories (examples)
- Warehouse > Inventory
- Warehouse > Product
- Sales > Orders
- Sales > Customers
- System > Configuration

## Categorizing Permissions

Initially, all permissions are assigned to the "Others" category. To divide permissions into specific categories and subcategories:

1. Open the JSON file in a text editor
2. For each permission, set the "category" field to the desired main category
3. Set the "subcategory" field to the desired subcategory (or leave empty for main category only)
4. Run `python manage.py sync_permissions --import-only` to apply the changes to the database

## Automatic Categorization

The system includes patterns to automatically categorize permissions based on their app and model names. The categorization rules are defined in the `sync_permissions.py` script.

## Automating the Process

For future full automation, you can:

1. **Add to Django's post-migrate signal**: Automatically run the sync after migrations
   ```python
   # In apps.py or a suitable module
   from django.db.models.signals import post_migrate
   
   def sync_permissions(sender, **kwargs):
       from django.core.management import call_command
       call_command('sync_permissions')
   
   post_migrate.connect(sync_permissions)
   ```

2. **Schedule as a periodic task**:
   - With Celery: Schedule the task to run daily/weekly
   - With cron: Add a crontab entry to run the sync regularly
   ```
   # Example crontab entry (runs daily at 2 AM)
   0 2 * * * cd /path/to/pyerp && python manage.py sync_permissions
   ```

3. **Add to CI/CD pipeline**: Include the sync command in deployment scripts to maintain consistency across environments

## Version Control

The JSON file should be under version control to track changes:

```bash
git add users/config/permissions_mapping.json
git commit -m "Update permission categories"
``` 