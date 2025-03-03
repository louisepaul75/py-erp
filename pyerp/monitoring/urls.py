"""
URL configuration for the monitoring app.
"""

from django.urls import path
from pyerp.monitoring import views

app_name = 'monitoring'

urlpatterns = [
    # Use the original path but still with the endpoint that doesn't require auth
    path('health-check/', views.run_health_checks, name='health_check'),
] 