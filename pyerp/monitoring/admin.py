"""
Admin configuration for the monitoring app.
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib import messages

from pyerp.monitoring.models import HealthCheckResult
from pyerp.monitoring.services import run_all_health_checks


@admin.register(HealthCheckResult)
class HealthCheckResultAdmin(admin.ModelAdmin):
    """Admin interface for health check results."""
    
    list_display = ('component', 'status', 'timestamp', 'response_time_display')
    list_filter = ('component', 'status', 'timestamp')
    search_fields = ('component', 'details')
    readonly_fields = ('component', 'status', 'timestamp', 'details', 'response_time')
    fieldsets = (
        (None, {
            'fields': ('component', 'status', 'timestamp', 'response_time')
        }),
        (_('Details'), {
            'fields': ('details',)
        }),
    )
    
    def response_time_display(self, obj):
        """Format response time for display."""
        if obj.response_time is None:
            return "-"
        return f"{obj.response_time:.2f} ms"
    response_time_display.short_description = _('Response Time')
    
    def has_add_permission(self, request):
        """Prevent manual creation of health check results."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification of health check results."""
        return False


class SystemStatusAdmin(admin.ModelAdmin):
    """
    Admin interface for system status dashboard.
    This is a proxy admin that doesn't actually manage a model,
    but provides a custom view for the system status dashboard.
    """
    
    model = HealthCheckResult  # Use HealthCheckResult model for permissions
    
    def get_urls(self):
        """Add custom URLs for the status dashboard."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='monitoring_dashboard'),
            path('refresh/', self.admin_site.admin_view(self.refresh_health_checks), name='refresh_health_checks'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Render the system status dashboard."""
        # Get the latest health check results for each component
        components = [
            HealthCheckResult.COMPONENT_DATABASE,
            HealthCheckResult.COMPONENT_LEGACY_ERP,
            HealthCheckResult.COMPONENT_PICTURES_API,
        ]
        
        latest_results = {}
        for component in components:
            result = HealthCheckResult.get_latest_result(component)
            latest_results[component] = result
        
        # Get history data for charts (last 20 entries for each component)
        history_data = {}
        for component in components:
            history = HealthCheckResult.objects.filter(
                component=component
            ).order_by('-timestamp')[:20]
            
            # Reverse to get chronological order for charts
            history_data[component] = list(reversed(history))
        
        context = {
            'title': _('System Status Dashboard'),
            'latest_results': latest_results,
            'history_data': history_data,
            'refresh_url': reverse('admin:refresh_health_checks'),
            **self.admin_site.each_context(request),
        }
        
        return TemplateResponse(
            request,
            'admin/monitoring/dashboard.html',
            context
        )
    
    def refresh_health_checks(self, request):
        """Run health checks and return the results as JSON."""
        try:
            results = run_all_health_checks()
            return JsonResponse({
                'success': True,
                'results': results
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Register the system status admin
try:
    admin.site.register(HealthCheckResult, HealthCheckResultAdmin)
except admin.sites.AlreadyRegistered:
    # Model is already registered, skip registration
    pass

# Create an instance of the custom admin view
system_status_admin = SystemStatusAdmin(HealthCheckResult, admin.site)

# The register_view method doesn't exist in the standard AdminSite
# Commenting out this code as it appears to be a custom extension
"""
# Add the custom admin view to the admin index
admin.site.register_view(
    'monitoring/dashboard/',
    system_status_admin.dashboard_view,
    'System Status Dashboard'
)
""" 