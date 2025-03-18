"""
Unit tests for product signal handlers.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from pyerp.business_modules.products.signals import variant_product_pre_save


@pytest.fixture
def mock_variant_product():
    """Create a mock variant product instance."""
    instance = MagicMock()
    instance.pk = None  # New instance by default
    instance.sku = None
    instance.variant_code = None
    instance.parent = None
    instance.created_at = None
    instance.updated_at = None
    return instance


def test_variant_product_pre_save_new_instance_no_parent():
    """Test pre-save signal for new variant product without parent."""
    instance = MagicMock()
    instance.pk = None
    instance.parent = None
    instance.created_at = None
    instance.updated_at = None

    with patch("django.utils.timezone.now") as mock_now:
        now = timezone.now()
        mock_now.return_value = now
        variant_product_pre_save(instance=instance)

        assert instance.created_at == now
        assert instance.updated_at == now
        assert instance.sku is instance.sku  # Should not be modified


def test_variant_product_pre_save_existing_instance():
    """Test pre-save signal for existing variant product."""
    instance = MagicMock()
    instance.pk = 1  # Existing instance
    instance.parent = None
    instance.created_at = timezone.now()
    old_created_at = instance.created_at
    instance.updated_at = None

    with patch("django.utils.timezone.now") as mock_now:
        now = timezone.now()
        mock_now.return_value = now
        variant_product_pre_save(instance=instance)

        assert instance.created_at == old_created_at  # Should not change
        assert instance.updated_at == now
        assert instance.sku is instance.sku  # Should not be modified


def test_variant_product_pre_save_with_parent_and_variant():
    """Test pre-save signal for variant product with parent and variant code."""
    parent = MagicMock()
    parent.sku = "PARENT-SKU"
    parent.legacy_id = None

    instance = MagicMock()
    instance.pk = None
    instance.parent = parent
    instance.variant_code = "VAR1"
    instance.sku = None
    instance.created_at = None
    instance.updated_at = None

    with patch("django.utils.timezone.now") as mock_now:
        now = timezone.now()
        mock_now.return_value = now
        variant_product_pre_save(instance=instance)

        assert instance.sku == "PARENT-SKU-VAR1"
        assert instance.created_at == now
        assert instance.updated_at == now


def test_variant_product_pre_save_with_parent_legacy_id():
    """Test pre-save signal for variant product with parent legacy ID."""
    parent = MagicMock()
    parent.sku = None
    parent.legacy_id = "12345"

    instance = MagicMock()
    instance.pk = None
    instance.parent = parent
    instance.variant_code = "VAR1"
    instance.sku = None
    instance.created_at = None
    instance.updated_at = None

    with patch("django.utils.timezone.now") as mock_now:
        now = timezone.now()
        mock_now.return_value = now
        variant_product_pre_save(instance=instance)

        assert instance.sku == "12345-VAR1"
        assert instance.created_at == now
        assert instance.updated_at == now
