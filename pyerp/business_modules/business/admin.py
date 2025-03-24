from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for the Employee model."""
    
    list_display = [
        'employee_number',
        'last_name',
        'first_name',
        'email',
        'phone',
        'is_active',
        'hire_date',
    ]
    list_filter = [
        'is_terminated',
        'is_present',
    ]
    search_fields = [
        'employee_number',
        'last_name',
        'first_name',
        'email',
        'phone',
        'ad_username',
    ]
    fieldsets = [
        (_('Basic Information'), {
            'fields': (
                'employee_number',
                'legacy_id',
                'first_name',
                'last_name',
                'birth_date',
            ),
        }),
        (_('Contact Information'), {
            'fields': (
                'email',
                'phone',
                'mobile_phone',
                'street',
                'postal_code',
                'city',
            ),
        }),
        (_('Employment Details'), {
            'fields': (
                'hire_date',
                'termination_date',
                'is_terminated',
                'is_present',
            ),
        }),
        (_('Working Hours'), {
            'fields': (
                'weekly_hours',
                'daily_hours',
            ),
        }),
        (_('Financial Information'), {
            'fields': (
                'salary_code',
                'annual_salary',
                'monthly_salary',
                'annual_vacation_days',
            ),
            'classes': ('collapse',),
        }),
        (_('System Information'), {
            'fields': (
                'ad_username',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
