from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SyncWorkflowViewSet, SyncJobViewSet

router = DefaultRouter()
router.register(r'workflows', SyncWorkflowViewSet, basename='sync-workflow')
router.register(r'jobs', SyncJobViewSet, basename='sync-job')

app_name = 'sync_manager'

urlpatterns = [
    path('', include(router.urls)),
] 