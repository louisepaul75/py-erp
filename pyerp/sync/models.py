"""Models for tracking synchronization operations and state."""

from django.db import models
from django.utils import timezone


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
        unique_together = ('source', 'target', 'entity_type')
    
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
    """Logs synchronization operations and results."""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed')
    ]
    
    mapping = models.ForeignKey(SyncMapping, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_succeeded = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    is_full_sync = models.BooleanField(default=False)
    sync_params = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    trace = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.mapping} - {self.start_time} - {self.status}"
    
    def mark_completed(self, records_succeeded, records_failed):
        """Mark a sync log as completed."""
        self.status = 'completed' if records_failed == 0 else 'partial'
        self.end_time = timezone.now()
        self.records_succeeded = records_succeeded
        self.records_failed = records_failed
        self.records_processed = records_succeeded + records_failed
        self.save()
    
    def mark_failed(self, error_message, trace=''):
        """Mark a sync log as failed."""
        self.status = 'failed'
        self.end_time = timezone.now()
        self.error_message = error_message
        self.trace = trace
        self.save()


class SyncLogDetail(models.Model):
    """Detailed log entries for individual record syncs."""
    
    sync_log = models.ForeignKey(SyncLog, on_delete=models.CASCADE, related_name='details')
    record_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)
    record_data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.record_id} - {self.status}" 