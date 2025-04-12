from rest_framework import serializers
from .models import Employee, Supplier
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model (for selection)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for the Employee model."""
    full_name = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    # Allow user ID to be passed in for updates, and include it in responses
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        allow_null=True, 
        required=False # Make it optional for updates
    )

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
            'updated_at',
            'user' # Include user ID
        ]
        read_only_fields = [
            'id', 
            'legacy_id', 
            'full_name', 
            'is_active', 
            'created_at', 
            'updated_at'
            # Remove user from read_only_fields
        ] 


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "synced_at") 