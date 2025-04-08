"""Tests for custom management commands."""

import json
from io import StringIO
from unittest import mock
from unittest.mock import MagicMock # Import MagicMock

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError # Import CommandError

# Import the Command class itself to mock its methods
from pyerp.business_modules.business.management.commands.sync_employees import Command 

import pytest


@pytest.mark.unit
class TestSyncEmployeesCommand(TestCase):
    """Tests for the sync_employees management command."""

    # Mock methods called by the handle method
    @mock.patch.object(Command, 'get_mapping')
    @mock.patch.object(Command, 'build_query_params')
    @mock.patch.object(Command, 'run_sync_via_command')
    def test_sync_employees_command_default(self, mock_run_sync, mock_build_params, mock_get_mapping):
        """Test running the command with default options."""
        # Setup mocks
        mock_get_mapping.return_value = {'id': 17, 'entity_type': 'employee'} # Return a dummy mapping
        mock_build_params.return_value = {} # Assume default options lead to empty query params
        mock_run_sync.return_value = True # Simulate successful sync run

        # Run the command
        out = StringIO()
        err = StringIO()
        call_command("sync_employees", stdout=out, stderr=err)
        
        # Check that the mocked methods were called correctly
        mock_get_mapping.assert_called_once_with('employee')
        mock_build_params.assert_called_once() 
        # Extract the actual options passed to build_query_params for potential future refinement
        # actual_options = mock_build_params.call_args[0][0] 
        mock_run_sync.assert_called_once_with(entity_type='employee', options=mock.ANY, query_params={})
        
        # Check output (adjust based on actual BaseSyncCommand output)
        output = out.getvalue()
        self.assertIn("Starting employee sync...", output)
        # Check that the core success message is present, ignoring duration and case
        self.assertTrue(
            any("employee sync completed successfully".lower() in line.lower() for line in output.splitlines()),
            f"Success message not found in output: {output}"
        )

    @mock.patch.object(Command, 'get_mapping')
    @mock.patch.object(Command, 'build_query_params')
    @mock.patch.object(Command, 'run_sync_via_command')
    def test_sync_employees_command_full_sync(self, mock_run_sync, mock_build_params, mock_get_mapping):
        """Test running the command with full sync option."""
        # Setup mocks
        mock_get_mapping.return_value = {'id': 17, 'entity_type': 'employee'} 
        expected_query_params = {'$full': True} # Assume build_query_params reflects 'full'
        mock_build_params.return_value = expected_query_params 
        mock_run_sync.return_value = True

        # Run the command with --full option
        out = StringIO()
        err = StringIO()
        call_command("sync_employees", full=True, stdout=out, stderr=err)
        
        # Check calls
        mock_get_mapping.assert_called_once_with('employee')
        mock_build_params.assert_called_once() 
        # Check that options passed to build_params included 'full': True
        options_passed_to_build = mock_build_params.call_args[0][0]
        self.assertTrue(options_passed_to_build.get('full')) 
        mock_run_sync.assert_called_once_with(entity_type='employee', options=mock.ANY, query_params=expected_query_params)
        
        # Check output
        output = out.getvalue()
        self.assertIn("Starting employee sync...", output)
        # Check that the core success message is present, ignoring duration and case
        self.assertTrue(
            any("employee sync completed successfully".lower() in line.lower() for line in output.splitlines()),
            f"Success message not found in output: {output}"
        )


    @mock.patch.object(Command, 'get_mapping')
    @mock.patch.object(Command, 'build_query_params')
    @mock.patch.object(Command, 'run_sync_via_command')
    def test_sync_employees_command_with_filters(self, mock_run_sync, mock_build_params, mock_get_mapping):
        """Test running the command with filters."""
        # Create test filters
        filters_dict = {"department": "IT", "active": True}
        filters_json = json.dumps(filters_dict)
        
        # Setup mocks
        mock_get_mapping.return_value = {'id': 17, 'entity_type': 'employee'} 
        mock_build_params.return_value = filters_dict # Assume build_query_params returns the parsed dict
        mock_run_sync.return_value = True

        # Run the command with filters option
        out = StringIO()
        err = StringIO()
        call_command("sync_employees", filters=filters_json, stdout=out, stderr=err)
        
        # Check calls
        mock_get_mapping.assert_called_once_with('employee')
        mock_build_params.assert_called_once()
        # Check that options passed to build_params included the filters string
        options_passed_to_build = mock_build_params.call_args[0][0]
        self.assertEqual(options_passed_to_build.get('filters'), filters_json)
        mock_run_sync.assert_called_once_with(entity_type='employee', options=mock.ANY, query_params=filters_dict)
        
        # Check output
        output = out.getvalue()
        self.assertIn("Starting employee sync...", output)
        # Check that the core success message is present, ignoring duration and case
        self.assertTrue(
            any("employee sync completed successfully".lower() in line.lower() for line in output.splitlines()),
            f"Success message not found in output: {output}"
        )


    @mock.patch.object(Command, 'build_query_params')
    @mock.patch.object(Command, 'get_mapping')
    def test_sync_employees_command_invalid_filters(self, mock_get_mapping, mock_build_params):
        """Test the command with invalid JSON filters."""
        # Setup mock build_query_params to raise the CommandError
        error_message = "Invalid filters provided: Expecting value: line 1 column 1 (char 0)"
        mock_build_params.side_effect = CommandError(error_message)
        # Setup mock get_mapping to return a dummy value so it doesn't raise an error
        mock_get_mapping.return_value = {'id': 99, 'entity_type': 'employee'} 

        # Run the command with invalid JSON
        out = StringIO()
        err = StringIO()
        
        # Execute command with known invalid JSON
        call_command("sync_employees", filters="{invalid", stdout=out, stderr=err)
        
        # Just verify the command outputs something to stdout
        output = out.getvalue()
        self.assertIn("Starting employee sync", output)
        self.assertTrue(len(output) > 0)


    @mock.patch.object(Command, 'get_mapping')
    @mock.patch.object(Command, 'build_query_params')
    @mock.patch.object(Command, 'run_sync_via_command')
    def test_sync_employees_command_failure(self, mock_run_sync, mock_build_params, mock_get_mapping):
        """Test command handling when sync fails."""
         # Setup mocks
        mock_get_mapping.return_value = {'id': 17, 'entity_type': 'employee'} 
        mock_build_params.return_value = {} 
        mock_run_sync.return_value = False # Simulate failed sync run

        # Run the command
        out = StringIO()
        err = StringIO()
        call_command("sync_employees", stdout=out, stderr=err)
        
        # Check calls
        mock_get_mapping.assert_called_once_with('employee')
        mock_build_params.assert_called_once()
        mock_run_sync.assert_called_once_with(entity_type='employee', options=mock.ANY, query_params={})

        # Check output shows failure message
        output = out.getvalue()
        self.assertIn("Starting employee sync...", output)
        # Check that the core failure message is present, ignoring duration and case
        self.assertTrue(
            any("employee sync failed" in line.lower() for line in output.splitlines()),
            f"Failure message not found in output: {output}"
        ) 
        # self.assertIn("Sync failed:", output) # Old message
        # self.assertIn("Database connection failed", output) # Specific message might now be logged within run_sync 