from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for the Employee model."""
    full_name = serializers.CharField(source='full_name', read_only=True)
    is_active = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 
            'employee_number', 
            'legacy_id', 
            'first_name', 
            'last_name', 
            'full_name', # Added property
            'birth_date', 
            'email', 
            'phone', 
            'mobile_phone', 
            'street', 
            'postal_code', 
            'city', 
            'hire_date', 
            'termination_date', 
            'is_terminated', 
            'is_present', 
            'is_active', # Added property
            'weekly_hours', 
            'daily_hours', 
            'salary_code', 
            'annual_salary', 
            'monthly_salary', 
            'annual_vacation_days', 
            'ad_username', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'legacy_id', 
            'full_name', 
            'is_active', 
            'created_at', 
            'updated_at'
        ] 