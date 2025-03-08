"""
Test database queries for pyERP.

This module contains tests to ensure that database queries work correctly,
including complex queries, aggregations, and performance.
"""

import pytest
from django.db.models import Count, Q
from pyerp.products.models import ParentProduct, VariantProduct


@pytest.mark.django_db
class TestProductQueries:
    """Test suite for product-related queries."""

    @pytest.fixture
    def sample_products(self):
        """Create sample products for testing."""
        parent1 = ParentProduct.objects.create(
            sku="PARENT001",
            name="Parent 1",
            base_sku="BASE001"
        )
        parent2 = ParentProduct.objects.create(
            sku="PARENT002",
            name="Parent 2",
            base_sku="BASE002"
        )

        # Create variants for parent1
        for i in range(3):
            VariantProduct.objects.create(
                sku=f"VAR00{i+1}",
                name=f"Variant {i+1}",
                parent=parent1
            )

        # Create variants for parent2
        for i in range(2):
            VariantProduct.objects.create(
                sku=f"VAR10{i+1}",
                name=f"Variant {i+1}",
                parent=parent2
            )

        return {"parent1": parent1, "parent2": parent2}

    def test_parent_with_variants_count(self, sample_products):
        """Test counting variants per parent."""
        variants_per_parent = (
            ParentProduct.objects
            .annotate(variant_count=Count("variants"))
            .values("sku", "variant_count")
            .order_by("sku")
        )

        results = list(variants_per_parent)
        assert len(results) == 2
        assert results[0]["sku"] == "PARENT001"
        assert results[0]["variant_count"] == 3
        assert results[1]["sku"] == "PARENT002"
        assert results[1]["variant_count"] == 2

    def test_complex_product_query(self, sample_products):
        """Test complex query with multiple conditions."""
        # Find variants that belong to a parent with more than 2 variants
        complex_query = (
            VariantProduct.objects
            .filter(parent__variants__count__gt=2)
            .distinct()
            .order_by("sku")
        )

        results = list(complex_query)
        assert len(results) == 3  # Only variants from parent1
        assert all(v.parent.sku == "PARENT001" for v in results) 