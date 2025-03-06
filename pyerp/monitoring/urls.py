"""
URL configuration for the monitoring app.
"""

from django.urls import path
from pyerp.monitoring import views

app_name = 'monitoring'
  # noqa: F841

urlpatterns = [
  # noqa: F841
    # Use the original path but still with the endpoint that doesn't require auth  # noqa: E501
    path('health-check/', views.run_health_checks, name='health_check'),
  # noqa: F841
]
