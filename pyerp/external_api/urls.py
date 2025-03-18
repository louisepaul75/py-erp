"""
URL patterns for external API management.
"""

from django.urls import path

from . import views

app_name = "external_api"

urlpatterns = [
    path("connections/", views.get_connections, name="get_connections"),
    path(
        "connections/<str:connection_name>/",
        views.update_connection,
        name="update_connection",
    ),
]
