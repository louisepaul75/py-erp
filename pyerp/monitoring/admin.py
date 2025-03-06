"""
Admin configuration for the monitoring app.
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _  # noqa: F401
from django.urls import reverse
from django.contrib import messages  # noqa: F401

from pyerp.monitoring.models import HealthCheckResult
from pyerp.monitoring.services import run_all_health_checks, validate_database


class HealthCheckResultAdmin(admin.ModelAdmin):
    """Admin interface for health check results."""

    list_display = ('component', 'status', 'timestamp', 'response_time_display')  # noqa: E501
  # noqa: E501, F841
    list_filter = ('component', 'status', 'timestamp')  # noqa: F841
  # noqa: F841
    search_fields = ('component', 'details')  # noqa: F841
  # noqa: F841
    readonly_fields = ('component', 'status', 'timestamp', 'details', 'response_time')  # noqa: E501
  # noqa: E501, F841
    fieldsets = (  # noqa: F841
  # noqa: F841
        (None, {
            'fields': ('component', 'status', 'timestamp', 'response_time')  # noqa: E128
        }),
        (_('Details'), {
            'fields': ('details',)  # noqa: E128
        }),
    )

    def response_time_display(self, obj):


        """Format response time for display."""
        if obj.response_time is None:
            return "-"
        return f"{obj.response_time:.2f} ms"
    response_time_display.short_description = _('Response Time')
  # noqa: F841

    def has_add_permission(self, request):

        """Prevent manual creation of health check results."""
        return False

    def has_change_permission(self, request, obj=None):

        """Prevent modification of health check results."""
        return False

    def get_urls(self):

        """Add custom URLs for the status dashboard."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='system_status_dashboard'),  # noqa: E501
            path('refresh/', self.admin_site.admin_view(self.refresh_health_checks), name='refresh_health_checks'),  # noqa: E501
            path('validate-database/', self.admin_site.admin_view(self.validate_database), name='validate_database'),  # noqa: E501
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Render the system status dashboard."""
        # Get the latest health check results for each component
        components = [
            HealthCheckResult.COMPONENT_DATABASE,  # noqa: E128
            HealthCheckResult.COMPONENT_LEGACY_ERP,
            HealthCheckResult.COMPONENT_PICTURES_API,
            HealthCheckResult.COMPONENT_DATABASE_VALIDATION,
        ]

        latest_results = {}
        for component in components:
            result = HealthCheckResult.get_latest_result(component)
            latest_results[component] = result

        # Get history data for charts (last 20 entries for each component)
        history_data = {}
        for component in components:
            history = HealthCheckResult.objects.filter(
                component=component  # noqa: E128
            ).order_by('-timestamp')[:20]

            # Reverse to get chronological order for charts
            history_data[component] = list(reversed(history))

        context = {
            'title': _('System Status Dashboard'),  # noqa: E128
            'latest_results': latest_results,
            'history_data': history_data,
            'refresh_url': reverse('admin:refresh_health_checks'),
            'validate_db_url': reverse('admin:validate_database'),
            **self.admin_site.each_context(request),
        }

        return TemplateResponse(
            request,  # noqa: E128
            'admin/monitoring/dashboard.html',
            context
        )

    def refresh_health_checks(self, request):

        """Run health checks and return the results as JSON."""
        try:
            results = run_all_health_checks()
            return JsonResponse({
                'success': True,  # noqa: E128
                'results': results
            })
        except Exception as e:
            return JsonResponse({
                'success': False,  # noqa: E128
                'error': str(e)
            }, status=500)

    def validate_database(self, request):
        """Run comprehensive database validation and return the results as JSON."""  # noqa: E501
        try:
            results = validate_database()
            return JsonResponse({
                'success': True,  # noqa: E128
                'results': results
            })
        except Exception as e:
            return JsonResponse({
                'success': False,  # noqa: E128
                'error': str(e)
            }, status=500)
  # noqa: F841


# Register the admin class with a better name to avoid duplicates in the admin sidebar  # noqa: E501
admin.site.register(HealthCheckResult, HealthCheckResultAdmin)
