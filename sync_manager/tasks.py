import subprocess
import sys
import shlex # Import shlex for safe command splitting
from datetime import timezone

# Create a mock shared_task decorator for tests
import os
# Check if we're in test mode
if os.environ.get("SKIP_CELERY_IMPORT") == "1":
    # Mock shared_task decorator for tests
    def shared_task(*args, **kwargs):
        """Mock shared_task decorator for testing."""
        def decorator(func):
            # Just return the function unchanged for tests
            return func
        # Handle both @shared_task and @shared_task() syntax
        return decorator if args and callable(args[0]) else decorator
else:
    # Normal import for production
    from celery import shared_task

from django.core.management import call_command # More robust way? Maybe subprocess is better for isolation/env vars
from django.utils import timezone as django_timezone

from .models import SyncJob, SyncWorkflow

# Helper function to build the command arguments
def build_command_args(workflow: SyncWorkflow, parameters: dict) -> list[str]:
    # Split the template safely using shlex
    try:
        base_args = shlex.split(workflow.command_template)
    except ValueError:
        # Handle potential splitting errors, e.g., unbalanced quotes
        print(f"Error splitting command template: {workflow.command_template}")
        base_args = [] # Or raise an error / return default?
    
    args = base_args
    
    # Commented out entity_type logic as it was removed from model
    # if workflow.entity_type:
    #     args.extend(['--entity-type', workflow.entity_type])
        
    # Add boolean flags based on parameters
    if parameters.get('debug'):
        args.append('--debug')
    if parameters.get('force_update'):
        args.append('--force-update')
        
    # TODO: Add handling for other parameter types (dates, limits) when implemented
    
    return args

@shared_task(bind=True, ignore_result=True) # ignore_result=True as we store results in SyncJob model
def run_sync_workflow_task(self, sync_job_id: int):
    """
    Celery task to execute a synchronization workflow management command.
    """
    try:
        job = SyncJob.objects.select_related('workflow').get(pk=sync_job_id)
    except SyncJob.DoesNotExist:
        # Log error - job doesn't exist, can't run
        # Consider using Celery's logging mechanisms
        print(f"Error: SyncJob with ID {sync_job_id} not found.")
        return # Nothing more to do

    workflow = job.workflow
    job.task_id = self.request.id # Store the Celery task ID
    job.status = SyncJob.Status.STARTED
    job.started_at = django_timezone.now()
    job.log_output = f"Task {self.request.id} started for workflow '{workflow.name}'...\n"
    job.save()

    exit_code = -1
    output_log = ""

    try:
        full_command = build_command_args(workflow, job.parameters)
        
        # Removed construction with python manage.py - command_template should contain it
        # manage_py_path = './manage.py' 
        # full_command = [sys.executable, manage_py_path] + command_args
        
        if not full_command: # Check if command splitting failed
            raise ValueError("Could not build command from template.")

        job.log_output += f"Executing command: {' '.join(full_command)}\n\n"
        job.save()

        # Execute the command using subprocess
        process = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=False, # Don't raise exception on non-zero exit code
            cwd='.',     # Ensure it runs from the project root
            # Consider environment variables if needed, e.g., for customer/employee sync
            # env=os.environ.copy() 
        )

        exit_code = process.returncode
        output_log = f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}"

        if exit_code == 0:
            job.status = SyncJob.Status.SUCCESS
            job.log_output += f"\nCommand executed successfully.\n"
        else:
            job.status = SyncJob.Status.FAILURE
            job.log_output += f"\nCommand failed with exit code {exit_code}.\n"
            
        job.log_output += "\n--- Full Output --- \n" + output_log

    except Exception as e:
        job.status = SyncJob.Status.FAILURE
        job.log_output += f"\nTask failed with exception: {e}\n{output_log}"
        # Potentially re-raise or handle specific exceptions
        
    finally:
        job.completed_at = django_timezone.now()
        job.save()
        print(f"SyncJob {job.id} finished with status: {job.status}") 