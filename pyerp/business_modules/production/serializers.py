from rest_framework import serializers
from pyerp.business_modules.production.models import Mold, MoldProduct


class MoldSerializer(serializers.ModelSerializer):
    """Serializer for the Mold model."""
    
    # Computed field to match the frontend expected format
    legacyMoldNumber = serializers.CharField(source='legacy_form_nr')
    moldNumber = serializers.CharField(source='legacy_form_nr')  # Temporary mapping until we have proper moldNumber field
    technology = serializers.CharField(default='', read_only=True)  # Will be added in future
    
    # Update alloy field to handle multiple alloys
    alloy = serializers.SerializerMethodField()  # Keep for backward compatibility
    alloys = serializers.SerializerMethodField()  # New field for multiple alloys
    
    warehouseLocation = serializers.CharField(source='storage_location')
    numberOfArticles = serializers.SerializerMethodField()
    isActive = serializers.BooleanField(source='is_active')
    activityStatus = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    createdDate = serializers.DateTimeField(source='created_at')
    
    class Meta:
        model = Mold
        fields = [
            'id', 
            'legacyMoldNumber', 
            'moldNumber', 
            'technology', 
            'alloy',  # Keep for backward compatibility
            'alloys',  # New field for multiple alloys
            'warehouseLocation',
            'numberOfArticles', 
            'isActive', 
            'activityStatus', 
            'tags', 
            'createdDate',
            'description',
            'notes'
        ]
    
    def get_numberOfArticles(self, obj):
        """Return the number of associated products."""
        return obj.products.count()
    
    def get_activityStatus(self, obj):
        """Return the activity status."""
        # For now, simply use 'ACTIVE' or 'INACTIVE' based on is_active
        return 'ACTIVE' if obj.is_active else 'INACTIVE'
    
    def get_tags(self, obj):
        """Return tags."""
        # For the initial implementation, return an empty list
        # This will be enhanced in the future
        return []
        
    def get_alloy(self, obj):
        """
        Return the primary alloy name for backward compatibility.
        Returns the first alloy if available, otherwise empty string.
        """
        alloys = obj.alloys.all()
        if alloys.exists():
            return alloys.first().name
        return ""
        
    def get_alloys(self, obj):
        """Return a list of all alloy names associated with this mold."""
        return [alloy.name for alloy in obj.alloys.all()]


class MoldProductSerializer(serializers.ModelSerializer):
    """Serializer for the MoldProduct model."""
    
    class Meta:
        model = MoldProduct
        fields = [
            'id', 
            'mold', 
            'parent_product', 
            'products_per_mold', 
            'weight_per_product'
        ] 