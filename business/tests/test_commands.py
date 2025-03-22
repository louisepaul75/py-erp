"""Tests for custom management commands."""

import json
from io import StringIO
from unittest import mock

from django.test import TestCase
from django.core.management import call_command

import pytest


@pytest.mark.unit
class TestSyncEmployeesCommand(TestCase):
    """Tests for the sync_employees management command."""

    @mock.patch("business.management.commands.sync_employees.sync_employees")
    def test_sync_employees_command_default(self, mock_sync_employees):
        """Test running the command with default options."""
        # Set up mock return value
        mock_sync_employees.return_value = {
            "status": "success",
            "records_processed": 10,
            "records_succeeded": 9,
            "records_failed": 1,
        }

        # Run the command
        out = StringIO()
        call_command("sync_employees", stdout=out)
        
        # Check that the sync_employees function was called with defaults
        mock_sync_employees.assert_called_once_with(full_sync=False, filters=None)
        
        # Check output
        output = out.getvalue()
        self.assertIn("Starting employee sync", output)
        self.assertIn("Running incremental sync", output)
        self.assertIn("Sync completed", output)
        self.assertIn("10 total, 9 success, 1 failed", output)

    @mock.patch("business.management.commands.sync_employees.sync_employees")
    def test_sync_employees_command_full_sync(self, mock_sync_employees):
        """Test running the command with full sync option."""
        # Set up mock return value
        mock_sync_employees.return_value = {
            "status": "success",
            "records_processed": 100,
            "records_succeeded": 95,
            "records_failed": 5,
        }

        # Run the command with --full option
        out = StringIO()
        call_command("sync_employees", full=True, stdout=out)
        
        # Check that the sync_employees function was called with full_sync=True
        mock_sync_employees.assert_called_once_with(full_sync=True, filters=None)
        
        # Check output
        output = out.getvalue()
        self.assertIn("Starting employee sync", output)
        self.assertIn("Running full sync", output)
        self.assertIn("Sync completed", output)
        self.assertIn("100 total, 95 success, 5 failed", output)

    @mock.patch("business.management.commands.sync_employees.sync_employees")
    def test_sync_employees_command_with_filters(self, mock_sync_employees):
        """Test running the command with filters."""
        # Set up mock return value
        mock_sync_employees.return_value = {
            "status": "success",
            "records_processed": 5,
            "records_succeeded": 5,
            "records_failed": 0,
        }

        # Create test filters
        filters = {"department": "IT", "active": True}
        
        # Run the command with filters option
        out = StringIO()
        call_command("sync_employees", filters=json.dumps(filters), stdout=out)
        
        # Check that the sync_employees function was called with filters
        mock_sync_employees.assert_called_once_with(full_sync=False, filters=filters)
        
        # Check output
        output = out.getvalue()
        self.assertIn("Starting employee sync", output)
        self.assertIn(f"with filters: {filters}", output)
        self.assertIn("Sync completed", output)
        self.assertIn("5 total, 5 success, 0 failed", output)

    @mock.patch("business.management.commands.sync_employees.sync_employees")
    def test_sync_employees_command_invalid_filters(self, mock_sync_employees):
        """Test the command with invalid JSON filters."""
        # Run the command with invalid JSON
        out = StringIO()
        call_command("sync_employees", filters="not-valid-json", stdout=out)
        
        # Check that sync_employees was never called
        mock_sync_employees.assert_not_called()
        
        # Check output shows error
        output = out.getvalue()
        self.assertIn("Invalid JSON format for filters", output)

    @mock.patch("business.management.commands.sync_employees.sync_employees")
    def test_sync_employees_command_failure(self, mock_sync_employees):
        """Test command handling when sync fails."""
        # Set up mock to return error
        mock_sync_employees.return_value = {
            "status": "error",
            "message": "Database connection failed",
        }

        # Run the command
        out = StringIO()
        call_command("sync_employees", stdout=out)
        
        # Check output shows error
        output = out.getvalue()
        self.assertIn("Sync failed:", output)
        self.assertIn("Database connection failed", output) 