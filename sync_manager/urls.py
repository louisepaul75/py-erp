from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SyncWorkflowViewSet, SyncJobViewSet, get_system_integration_data
)

router = DefaultRouter()
router.register(r'workflows', SyncWorkflowViewSet, basename='sync-workflow')
router.register(r'jobs', SyncJobViewSet, basename='sync-job')

app_name = 'sync_manager_api'

urlpatterns = [
    path('', include(router.urls)),
    path(
        'system-integrations/', 
        get_system_integration_data, 
        name='system_integration_data'
    ),
] 