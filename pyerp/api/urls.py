from django.urls import path, include
from .views import (
    PermissionCategoriesView,
    PermissionListView,
    GroupPermissionsView,
    get_git_branch,
)

# Remove potentially conflicting app_name
app_name = 'api'  # Optional, but good practice

urlpatterns = [
    path('v1/', include([
        path(
            'permission-categories/',
            PermissionCategoriesView.as_view(),
            name='permission-categories',
        ),
        path(
            'permissions/',
            PermissionListView.as_view(),
            name='permission-list',
        ),
        path(
            'groups/<int:group_id>/permissions/',
            GroupPermissionsView.as_view(),
            name='group-permissions',
        ),
        path(
            'users/',
            include('users.urls'),
        ),  # Include the users app URLs under /v1/users/
        path(
            'products/',
            include('pyerp.business_modules.products.api_urls'),
        ),  # Include the products API URLs
         path(
            'currency/',
            include('pyerp.business_modules.currency.urls'),
        ),  # Include the products API URLs
        path(
            'sales/',
            include('pyerp.business_modules.sales.api_urls'),
        ), # Include the sales API URLs
        path(
            'business/',
            include('pyerp.business_modules.business.api_urls'),
        ), # Include the business API URLs
        path(
            'git/branch/',
            get_git_branch,
            name='get_git_branch',
        ),
    ])),
    # Add other API endpoints here later (permissions, group permissions, etc.)
] 