"""
Test database migrations for pyERP.

This module contains tests to ensure that database migrations work correctly
and maintain data integrity during schema changes.
"""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db
def test_migrations_are_in_sync():
    """Test that all migrations are in sync with models."""
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    assert not plan, "There are pending migrations that need to be applied"


@pytest.mark.django_db
def test_migrations_can_be_applied():
    """Test that all migrations can be applied without errors."""
    executor = MigrationExecutor(connection)
    # Get all app labels from the migration graph
    app_labels = {node[0] for node in executor.loader.graph.nodes}

    # Try to apply migrations for each app
    for app_label in app_labels:
        try:
            executor.migrate([app_label])
        except Exception as e:
            pytest.fail(f"Failed to apply migrations for {app_label}: {str(e)}")
