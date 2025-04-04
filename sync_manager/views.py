from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SyncWorkflow, SyncJob
from .serializers import (SyncWorkflowSerializer, SyncJobSerializer, 
                        TriggerSyncJobSerializer)
from .tasks import run_sync_workflow_task

class SyncWorkflowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows viewing Sync Workflows.
    Provides an action to trigger a workflow.
    """
    queryset = SyncWorkflow.objects.all()
    serializer_class = SyncWorkflowSerializer
    permission_classes = [] # TODO: Add appropriate permissions (e.g., IsAdminUser)
    lookup_field = 'slug' # Use slug for lookups

    @action(detail=True, methods=['post'], serializer_class=TriggerSyncJobSerializer)
    def trigger(self, request, slug=None):
        """Triggers a new SyncJob for this workflow."""
        workflow = self.get_object() # Gets workflow based on slug
        
        trigger_serializer = TriggerSyncJobSerializer(data=request.data)
        trigger_serializer.is_valid(raise_exception=True)
        
        # Combine default parameters with provided ones (provided override defaults)
        job_parameters = workflow.default_parameters.copy()
        job_parameters.update(trigger_serializer.validated_data.get('parameters', {}))
        
        # Create the SyncJob record
        job = SyncJob.objects.create(
            workflow=workflow,
            status=SyncJob.Status.PENDING,
            parameters=job_parameters
        )
        
        # Queue the Celery task asynchronously
        run_sync_workflow_task.delay(job.id)
        
        # Return the created job details
        job_serializer = SyncJobSerializer(job)
        return Response(job_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='recent-jobs')
    def recent_jobs(self, request, slug=None):
        """Returns the most recent jobs for this workflow."""
        workflow = self.get_object()
        recent_jobs = SyncJob.objects.filter(workflow=workflow).order_by('-created_at')[:10] # Limit to 10
        serializer = SyncJobSerializer(recent_jobs, many=True)
        return Response(serializer.data)

class SyncJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows viewing Sync Job history and status.
    """
    queryset = SyncJob.objects.select_related('workflow').order_by('-created_at')
    serializer_class = SyncJobSerializer
    permission_classes = [] # TODO: Add appropriate permissions

    # Optional: Add filtering capabilities if needed later (e.g., by status, workflow)
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['status', 'workflow__slug']
