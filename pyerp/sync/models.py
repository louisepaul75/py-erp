"""Models for tracking synchronization operations and state."""

from django.db import models
from django.utils import timezone
from pyerp.utils.json_utils import json_serialize
import json


class SyncSource(models.Model):
    """Represents a data source for synchronization."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SyncTarget(models.Model):
    """Represents a data target for synchronization."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SyncMapping(models.Model):
    """Defines mapping between source and target entities."""

    source = models.ForeignKey(SyncSource, on_delete=models.CASCADE)
    target = models.ForeignKey(SyncTarget, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=100)
    mapping_config = models.JSONField()
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("source", "target", "entity_type")

    def __str__(self):
        return f"{self.source} → {self.target} ({self.entity_type})"


class SyncState(models.Model):
    """Tracks the state of synchronization for incremental syncs."""

    mapping = models.ForeignKey(SyncMapping, on_delete=models.CASCADE)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    last_successful_sync_time = models.DateTimeField(null=True, blank=True)
    last_sync_id = models.CharField(max_length=100, blank=True)
    last_successful_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Sync state for {self.mapping}"

    def update_sync_started(self):
        """Mark a sync operation as started."""
        self.last_sync_time = timezone.now()
        self.save()

    def update_sync_completed(self, success=True):
        """Mark a sync operation as completed."""
        if success:
            self.last_successful_sync_time = self.last_sync_time
            self.last_successful_id = self.last_sync_id
        self.save()


class SyncLog(models.Model):
    """Logs synchronization operations (using the legacy structure)."""

    id = models.BigAutoField(primary_key=True)  # Explicitly define the PK

    # Fields matching legacy_sync_synclog / audit_synclog structure
    entity_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default='unknown')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.BigIntegerField(default=0)
    records_created = models.BigIntegerField(default=0)   # New field
    records_updated = models.BigIntegerField(default=0)   # New field
    records_failed = models.BigIntegerField(default=0)    # Changed to BigIntegerField
    error_message = models.TextField(blank=True)

    # Removed fields: mapping, is_full_sync, sync_params, trace, records_succeeded
    # Removed STATUS_CHOICES if they differ significantly from legacy data

    class Meta:
        # db_table = 'audit_synclog' # Removed to use default table name 'sync_synclog'
        pass # Add pass if Meta class becomes empty

    def __str__(self):
        # Updated str representation
        return f"{self.entity_type or 'Sync'} - {self.started_at} - {self.status}"

    # Removed methods: mark_completed, mark_failed as they used old fields
    # Removed save override related to sync_params
