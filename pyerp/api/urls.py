from django.urls import path, include
from .views import PermissionCategoriesView, PermissionListView, GroupPermissionsView

app_name = 'api' # Optional, but good practice

urlpatterns = [
    path('v1/', include([
        path('permission-categories/', PermissionCategoriesView.as_view(), name='permission-categories'),
        path('permissions/', PermissionListView.as_view(), name='permission-list'),
        path('groups/<int:group_id>/permissions/', GroupPermissionsView.as_view(), name='group-permissions'),
        path('users/', include('users.urls')),  # Include the users app URLs under /v1/users/
    ])),
    # Add other API endpoints here later (permissions, group permissions, etc.)
] 