"""
URL configuration for the monitoring app.
"""

from django.urls import path

from pyerp.monitoring import views

app_name = "monitoring"

urlpatterns = [
    # API endpoints
    path("health-checks/", views.run_health_checks, name="health_checks"),
    path("db-stats/", views.get_db_statistics, name="db_statistics"),
    path("host-resources/", views.get_host_resources_view, name="host_resources"),
]
