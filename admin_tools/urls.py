from django.urls import path
from admin_tools import views

app_name = "admin_tools"

urlpatterns = [
    path("database/tables/", views.list_tables, name="list_tables"),
    path(
        "database/table-data/<str:table_name>/",
        views.get_table_data,
        name="get_table_data",
    ),
]
