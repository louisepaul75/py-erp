from rest_framework import serializers
from django.utils import timezone
from .models import SyncWorkflow, SyncJob

class SyncWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for SyncWorkflow model."""
    last_job_status = serializers.SerializerMethodField()
    last_run_time = serializers.SerializerMethodField()

    class Meta:
        model = SyncWorkflow
        fields = [
            'id', 'name', 'slug', 'description',
            'command_template',
            'parameters',
            'environment_variables',
            'last_job_status', 'last_run_time'
        ]
        read_only_fields = ['last_job_status', 'last_run_time']

    def get_last_job(self, obj):
        # Efficiently get the most recent job for this workflow
        return SyncJob.objects.filter(workflow=obj).order_by('-created_at').first()

    def get_last_job_status(self, obj):
        last_job = self.get_last_job(obj)
        return last_job.status if last_job else None

    def get_last_run_time(self, obj):
        last_job = self.get_last_job(obj)
        # Return completed_at if available, otherwise created_at
        if last_job:
            return last_job.completed_at or last_job.created_at
        return None

class SyncJobSerializer(serializers.ModelSerializer):
    """Serializer for SyncJob model."""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)

    class Meta:
        model = SyncJob
        fields = [
            'id', 'workflow', 'workflow_name', 'task_id', 'status',
            'parameters', 'created_at', 'started_at', 'completed_at', 'log_output'
        ]
        read_only_fields = [
            'id', 'workflow_name', 'task_id', 'status', 'created_at',
            'started_at', 'completed_at', 'log_output'
        ]

class TriggerSyncJobSerializer(serializers.Serializer):
    """Serializer for triggering a new sync job."""
    # Allow passing optional parameters, default to workflow defaults later
    parameters = serializers.JSONField(required=False, default=dict)

    def validate_parameters(self, value):
        # Basic validation: ensure it's a dictionary
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a JSON object (dictionary).")
        # TODO: Add more specific validation based on workflow.parameter_schema later
        return value 