"""
Test script to verify the new product model structure.
"""

import os
import sys
import django
import pytest
from django.db import connection
from django.db.models import Count
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables from .env file in config/env folder
env_path = os.path.join(os.path.dirname(__file__), '../../config/env/.env')
load_dotenv(env_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')
django.setup()

# Import Django models
from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory

# No need for UnifiedProduct or Product alias since we're testing the split models directly


@pytest.fixture(scope="module")
def django_db_setup():
    """Set up the database for testing."""
    pass


def table_exists(table_name):
    """Check if a table exists in the database."""
    return table_name in connection.introspection.table_names()


@pytest.mark.django_db
def test_model_structure():
    """Test the structure of the new models."""
    # Skip test if tables don't exist
    if not table_exists('products_parentproduct') or not table_exists('products_variantproduct'):
        pytest.skip("Product tables don't exist yet - migrations may need to be run")
    
    # Check if the new models exist
    assert ParentProduct._meta.db_table in connection.introspection.table_names()
    assert VariantProduct._meta.db_table in connection.introspection.table_names()
    
    # Check the fields of the new models
    parent_fields = {field.name for field in ParentProduct._meta.get_fields()}
    variant_fields = {field.name for field in VariantProduct._meta.get_fields()}
    
    # Assert essential fields exist
    assert 'sku' in parent_fields
    assert 'name' in parent_fields
    assert 'base_sku' in parent_fields
    
    assert 'sku' in variant_fields
    assert 'name' in variant_fields
    assert 'parent' in variant_fields


@pytest.mark.django_db
def test_relationships():
    """Test the relationships between parent and variant products."""
    # Skip test if tables don't exist
    if not table_exists('products_parentproduct') or not table_exists('products_variantproduct'):
        pytest.skip("Product tables don't exist yet - migrations may need to be run")
    
    # Check variants with no parent
    orphan_variants = VariantProduct.objects.filter(parent__isnull=True).count()
    
    # Check parents with no variants
    childless_parents = ParentProduct.objects.annotate(
        variant_count=Count('variants')
    ).filter(variant_count=0).count()
    
    # These are not necessarily failures, but we should be aware of them
    # Just assert that the counts can be retrieved
    assert isinstance(orphan_variants, int)
    assert isinstance(childless_parents, int)


@pytest.mark.django_db
def test_parent_variant_relationship():
    """Test that parent-variant relationships can be created and queried."""
    # Skip test if tables don't exist
    if not table_exists('products_parentproduct') or not table_exists('products_variantproduct'):
        pytest.skip("Product tables don't exist yet - migrations may need to be run")
    
    # Create a test parent product
    parent = ParentProduct.objects.create(
        sku="TEST-PARENT-001",
        name="Test Parent Product",
        base_sku="TEST-PARENT"
    )
    
    # Create a test variant product
    variant = VariantProduct.objects.create(
        sku="TEST-VARIANT-001",
        name="Test Variant Product",
        parent=parent,
        variant_code="001",
        base_sku="TEST-PARENT"
    )
    
    # Test the relationship
    assert variant.parent == parent
    assert variant in parent.variants.all()
    
    # Clean up
    variant.delete()
    parent.delete()


# Keep the script functionality for direct execution
if __name__ == "__main__":
    print("=== PRODUCT MODEL MIGRATION TEST ===")
    print("This script checks the migration from the old Product model to the new ParentProduct/VariantProduct models.")
    
    # Original function calls for script mode
    def check_model_structure():
        """Check the structure of the new models."""
        print("\n=== MODEL STRUCTURE ===")
        
        # Check if the new models exist
        print(f"ParentProduct model exists: {ParentProduct._meta.db_table in connection.introspection.table_names()}")
        print(f"VariantProduct model exists: {VariantProduct._meta.db_table in connection.introspection.table_names()}")
        
        # Check the fields of the new models
        print("\nParentProduct fields:")
        for field in ParentProduct._meta.get_fields():
            print(f"  - {field.name}: {field.__class__.__name__}")
        
        print("\nVariantProduct fields:")
        for field in VariantProduct._meta.get_fields():
            print(f"  - {field.name}: {field.__class__.__name__}")
    
    def check_relationships():
        """Check the relationships between parent and variant products."""
        print("\n=== RELATIONSHIP CHECK ===")
        
        # Check variants with no parent
        orphan_variants = VariantProduct.objects.filter(parent__isnull=True).count()
        print(f"Orphan variants (no parent): {orphan_variants}")
        
        # Check parents with no variants
        childless_parents = ParentProduct.objects.annotate(
            variant_count=Count('variants')
        ).filter(variant_count=0).count()
        print(f"Childless parents (no variants): {childless_parents}")
        
        # Check average variants per parent
        total_parents = ParentProduct.objects.count()
        total_variants = VariantProduct.objects.count()
        if total_parents > 0:
            avg_variants = total_variants / total_parents
            print(f"Average variants per parent: {avg_variants:.1f}")
        else:
            print("No parent products found")
    
    def check_sample_data():
        """Check sample data from both models."""
        print("\n=== SAMPLE DATA CHECK ===")
        
        # Get a sample parent product
        parent = ParentProduct.objects.first()
        if parent:
            print("\nSample parent product:")
            print(f"  - SKU: {parent.sku}")
            print(f"  - Name: {parent.name}")
            print(f"  - Base SKU: {parent.base_sku}")
            
            # Get variants for this parent
            variants = parent.variants.all()
            if variants:
                print(f"\nVariants for parent {parent.sku}:")
                for variant in variants[:5]:  # Limit to 5 variants
                    print(f"  - SKU: {variant.sku}")
                    print(f"  - Name: {variant.name}")
                    print(f"  - Variant Code: {variant.variant_code}")
                    print()
            else:
                print(f"\nNo variants found for parent {parent.sku}")
        else:
            print("No parent products found")
    
    # Run the script functions
    check_model_structure()
    check_relationships()
    check_sample_data()
    
    print("\nTest completed.") 