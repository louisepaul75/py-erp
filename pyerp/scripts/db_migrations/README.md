# Database Migration Utilities

This directory contains utility scripts for managing database migrations in the pyERP system.

## Scripts

### check_variant_table.py

Checks the structure of the variant product table to ensure it has all required fields and constraints.

Usage:
```bash
python -m pyerp.scripts.db_migrations.check_variant_table
```

### fix_migration_state.py

Fixes the migration state by marking pending migrations as applied, resolving conflicts between different migration paths.

Usage:
```bash
python -m pyerp.scripts.db_migrations.fix_migration_state
```

### fix_migrations.py

General utility for fixing migration issues in the pyERP system.

Usage:
```bash
python -m pyerp.scripts.db_migrations.fix_migrations
```

### fix_variant_foreign_key.py

Adds missing foreign key constraints to the variant product table.

Usage:
```bash
python -m pyerp.scripts.db_migrations.fix_variant_foreign_key
```

### fix_variant_table.py

Fixes the variant product table by ensuring it has all necessary fields and constraints.

Usage:
```bash
python -m pyerp.scripts.db_migrations.fix_variant_table
```

## Common Issues

- **Migration conflicts**: When multiple migration paths try to create the same table or modify the same fields, conflicts can occur. Use `fix_migration_state.py` to resolve these conflicts.
- **Missing foreign key constraints**: If foreign key constraints are missing, use `fix_variant_foreign_key.py` to add them.
- **Table structure issues**: If the table structure is incorrect, use `check_variant_table.py` to diagnose the issues and `fix_variant_table.py` to fix them.
