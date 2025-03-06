"""
URL configuration for the monitoring app.
"""

from django.urls import path
from pyerp.monitoring import views

app_name = 'monitoring'

urlpatterns = [
               path('health-check/', views.run_health_checks, name='health_check'),  # noqa: E501
               # noqa: F841
]
