"""Admin configuration for sync app."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    SyncSource, SyncTarget, SyncMapping, SyncState, SyncLog, SyncLogDetail
)


@admin.register(SyncSource)
class SyncSourceAdmin(admin.ModelAdmin):
    """Admin interface for sync sources."""
    
    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')
    list_filter = ('active',)


@admin.register(SyncTarget)
class SyncTargetAdmin(admin.ModelAdmin):
    """Admin interface for sync targets."""
    
    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')
    list_filter = ('active',)


class SyncStateInline(admin.TabularInline):
    """Inline admin for sync states."""
    
    model = SyncState
    readonly_fields = (
        'last_sync_time', 'last_successful_sync_time', 
        'last_sync_id', 'last_successful_id'
    )
    extra = 0


@admin.register(SyncMapping)
class SyncMappingAdmin(admin.ModelAdmin):
    """Admin interface for sync mappings."""
    
    list_display = (
        'id', 'entity_type', 'source', 'target', 'active', 'last_sync_status'
    )
    list_filter = ('active', 'entity_type', 'source', 'target')
    search_fields = ('entity_type',)
    inlines = [SyncStateInline]
    
    def last_sync_status(self, obj):
        """Display the status of the last sync attempt."""
        try:
            last_log = SyncLog.objects.filter(mapping=obj).latest('start_time')
            status = last_log.status
            
            if status == 'completed':
                return format_html(
                    '<span style="color: green;">{}</span>', status
                )
            elif status == 'partial':
                return format_html(
                    '<span style="color: orange;">{}</span>', status
                )
            elif status == 'failed':
                return format_html(
                    '<span style="color: red;">{}</span>', status
                )
            else:
                return status
        except SyncLog.DoesNotExist:
            return "Never run"
    
    last_sync_status.short_description = "Last Sync"


class SyncLogDetailInline(admin.TabularInline):
    """Inline admin for sync log details."""
    
    model = SyncLogDetail
    readonly_fields = (
        'record_id', 'status', 'timestamp', 'error_message'
    )
    fields = readonly_fields
    extra = 0
    max_num = 20
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    """Admin interface for sync logs."""
    
    list_display = (
        'id', 'mapping', 'status', 'start_time', 'end_time', 
        'records_processed', 'records_succeeded', 'records_failed', 
        'is_full_sync'
    )
    list_filter = ('status', 'is_full_sync', 'mapping__entity_type')
    search_fields = ('mapping__entity_type',)
    readonly_fields = (
        'mapping', 'status', 'start_time', 'end_time', 
        'records_processed', 'records_succeeded', 'records_failed',
        'is_full_sync', 'sync_params', 'error_message', 'trace'
    )
    date_hierarchy = 'start_time'
    inlines = [SyncLogDetailInline]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SyncState)
class SyncStateAdmin(admin.ModelAdmin):
    """Admin interface for sync states."""
    
    list_display = (
        'mapping', 'last_sync_time', 'last_successful_sync_time'
    )
    list_filter = ('mapping__entity_type',)
    readonly_fields = (
        'mapping', 'last_sync_time', 'last_successful_sync_time',
        'last_sync_id', 'last_successful_id'
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 