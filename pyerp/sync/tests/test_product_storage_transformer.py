"""Tests for the product storage transformer module."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
import datetime
from typing import Any, Dict, List, Optional
import json
import logging
import math
import re

from pyerp.sync.transformers.product_storage import (
    ProductStorageTransformer,
    BoxStorageTransformer,
    parse_decimal,
    parse_date
)

# Import models needed for test setup
from pyerp.business_modules.inventory.models import ProductStorage, BoxSlot, Box, StorageLocation
from pyerp.business_modules.products.models import VariantProduct
from pyerp.sync.exceptions import TransformError

# Import mock patch
from unittest.mock import patch, MagicMock
import pandas as pd # Needed for mocking fetch_table

# --- Fixtures for TestProductStorageTransformer ---
@pytest.fixture
def product_storage_transformer():
    return ProductStorageTransformer({})

@pytest.fixture
def db_setup_product_storage(db): # db fixture from pytest-django
    product_refOld = VariantProduct.objects.create(
        sku="SKU-REFOLD", name="Product By RefOld", refOld="refold-123"
    )
    product_legacy_id = VariantProduct.objects.create(
        sku="SKU-LEGACYID", name="Product By LegacyID", legacy_id="legacyid-456"
    )
    product_sku = VariantProduct.objects.create(
        sku="sku-789", name="Product By SKU"
    )
    product_legacy_sku = VariantProduct.objects.create(
        sku="SKU-LEGACY-SKU", name="Product By Legacy SKU", legacy_sku="legacy-sku-101"
    )
    location_direct = StorageLocation.objects.create(
        name="Direct Location", legacy_id="direct-uuid-123",
        country="DE", city_building="B1", unit="U1", compartment="C1", shelf="S1"
    )
    location_fallback = StorageLocation.objects.create(
        name="Fallback Location", legacy_id="fallback-id-456",
        country="DE", city_building="B2", unit="U2", compartment="C2", shelf="S2"
    )
    try:
        from pyerp.business_modules.inventory.models import BoxType
        box_type, _ = BoxType.objects.get_or_create(name="Test Type")
    except ImportError:
        box_type = None

    # Create Box in two steps to potentially avoid DoesNotExist during save
    box1 = Box.objects.create(
        code="BOX1-CODE", 
        box_type=box_type, 
        legacy_id="box-123"
        # storage_location=location_direct # Assign after initial save
    )
    box1.storage_location = location_direct
    box1.save()
    
    box1_slot1 = BoxSlot.objects.create(box=box1, slot_code="S1.1", legacy_slot_id="S1")
    box1_slot2 = BoxSlot.objects.create(box=box1, slot_code="S1.2", legacy_slot_id="S2")
    
    box2_no_slots = Box.objects.create(
        code="BOX2-CODE",
        box_type=box_type,
        legacy_id="box-noslots-456"
        # storage_location=location_direct # Assign after initial save
    )
    box2_no_slots.storage_location = location_direct
    box2_no_slots.save()

    return {
        "product_refOld": product_refOld,
        "product_legacy_id": product_legacy_id,
        "product_sku": product_sku,
        "product_legacy_sku": product_legacy_sku,
        "location_direct": location_direct,
        "location_fallback": location_fallback,
        "box1": box1,
        "box1_slot1": box1_slot1,
        "box1_slot2": box1_slot2,
        "box2_no_slots": box2_no_slots,
    }

# --- Test Classes --- 

@pytest.mark.unit
class TestHelperFunctions:
    """Tests for the helper functions in the product_storage module."""

    def test_parse_decimal_valid(self):
        """Test parsing valid decimal values."""
        # Test valid formats
        assert parse_decimal("123.45") == Decimal("123.45")
        assert parse_decimal("123,45") == Decimal("12345")  # Comma is removed
        assert parse_decimal("-123.45") == Decimal("-123.45")
        assert parse_decimal("1,234.56") == Decimal("1234.56")  # Commas are removed but decimal point is kept
        assert parse_decimal("€ 123.45") == Decimal("123.45")  # Currency symbol removed
        
    def test_parse_decimal_invalid(self):
        """Test parsing invalid decimal values."""
        # Test invalid formats - should return 0
        assert parse_decimal("") == Decimal("0")
        assert parse_decimal(None) == Decimal("0")
        assert parse_decimal("abc") == Decimal("0")
        assert parse_decimal("123.45.67") == Decimal("0")  # Multiple decimal points
        
    def test_parse_date_valid(self):
        """Test parsing valid date strings."""
        # Test DD.MM.YYYY format
        result = parse_date("01.02.2025")
        assert isinstance(result, datetime.date)
        assert result.day == 1
        assert result.month == 2
        assert result.year == 2025
        
    def test_parse_date_invalid(self):
        """Test parsing invalid date strings."""
        # Test invalid formats
        assert parse_date("") is None
        assert parse_date(None) is None
        assert parse_date("2025-02-01") is None  # Wrong format
        assert parse_date("01/02/2025") is None  # Wrong format
        assert parse_date("32.01.2025") is None  # Invalid day
        assert parse_date("01.13.2025") is None  # Invalid month


# --- Test Functions for ProductStorageTransformer (was TestProductStorageTransformer class) --- #

@pytest.mark.unit
def test_product_storage_transformer_init(product_storage_transformer):
    """Test initialization of ProductStorageTransformer."""
    assert product_storage_transformer._product_cache == {}
    assert product_storage_transformer._storage_location_cache == {}
    assert product_storage_transformer._box_slot_cache == {}

@pytest.mark.unit
@pytest.mark.django_db 
def test_get_product_by_refOld(product_storage_transformer, db_setup_product_storage):
    """Test getting a product by refOld using the real transformer."""
    transformer = product_storage_transformer
    product_refOld = db_setup_product_storage['product_refOld']
    transformer._product_cache = {} # Reset cache for isolation
    product = transformer._get_product("refold-123")
    assert product == product_refOld
    assert transformer._product_cache["refold-123"] == product_refOld

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_by_legacy_id(product_storage_transformer, db_setup_product_storage):
    """Test getting a product by legacy_id after refOld fails."""
    transformer = product_storage_transformer
    product_legacy_id = db_setup_product_storage['product_legacy_id']
    transformer._product_cache = {}
    product = transformer._get_product("legacyid-456")
    assert product == product_legacy_id
    assert transformer._product_cache["legacyid-456"] == product_legacy_id

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_by_sku(product_storage_transformer, db_setup_product_storage):
    """Test getting a product by SKU after refOld and legacy_id fail."""
    transformer = product_storage_transformer
    product_sku = db_setup_product_storage['product_sku']
    transformer._product_cache = {}
    product = transformer._get_product("sku-789")
    assert product == product_sku
    assert transformer._product_cache["sku-789"] == product_sku

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_by_legacy_sku(product_storage_transformer, db_setup_product_storage):
    """Test getting a product by legacy_sku after other lookups fail."""
    transformer = product_storage_transformer
    product_legacy_sku = db_setup_product_storage['product_legacy_sku']
    transformer._product_cache = {}
    product = transformer._get_product("legacy-sku-101")
    assert product == product_legacy_sku
    assert transformer._product_cache["legacy-sku-101"] == product_legacy_sku

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_not_found(product_storage_transformer, db_setup_product_storage):
    """Test getting a product that doesn't exist using any ID."""
    transformer = product_storage_transformer
    transformer._product_cache = {}
    product = transformer._get_product("nonexistent-id")
    assert product is None
    assert "nonexistent-id" not in transformer._product_cache

@pytest.mark.unit
@pytest.mark.django_db
def test_storage_location(product_storage_transformer, db_setup_product_storage):
    """Test getting a storage location directly by legacy_id (UUID)."""
    transformer = product_storage_transformer
    location_direct = db_setup_product_storage['location_direct']
    transformer._storage_location_cache = {}
    location = transformer._get_storage_location("direct-uuid-123")
    assert location == location_direct
    assert transformer._storage_location_cache["direct-uuid-123"] == location_direct

@pytest.mark.unit
@pytest.mark.django_db
def test_get_storage_location_not_found(product_storage_transformer, db_setup_product_storage):
    """Test getting a location that doesn't exist by UUID or fallback."""
    transformer = product_storage_transformer
    transformer._storage_location_cache = {}
    with patch('pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table') as mock_fetch:
        mock_fetch.return_value = pd.DataFrame()
        location = transformer._get_storage_location("nonexistent-uuid")
        assert location is None
        assert "nonexistent-uuid" not in transformer._storage_location_cache
        mock_fetch.assert_called_once()

@pytest.mark.unit
@pytest.mark.django_db
def test_get_storage_location_fallback_success(product_storage_transformer, db_setup_product_storage):
    """Test getting a location via the legacy DB fallback."""
    transformer = product_storage_transformer
    location_fallback = db_setup_product_storage['location_fallback']
    transformer._storage_location_cache = {}
    with patch('pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table') as mock_fetch:
        mock_fetch.return_value = pd.DataFrame({'ID_Lagerort': ["fallback-id-456"]})
        location = transformer._get_storage_location("trigger-fallback-uuid")
        assert location == location_fallback
        assert transformer._storage_location_cache["trigger-fallback-uuid"] == location_fallback
        mock_fetch.assert_called_once_with(table_name='Stamm_Lagerorte', filter_query=[['UUID', '==', 'trigger-fallback-uuid']])

@pytest.mark.unit
@pytest.mark.django_db
def test_get_storage_location_fallback_legacy_not_found(product_storage_transformer, db_setup_product_storage):
    """Test fallback when UUID is not found in the legacy DB."""
    transformer = product_storage_transformer
    transformer._storage_location_cache = {}
    with patch('pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table') as mock_fetch:
        mock_fetch.return_value = pd.DataFrame()
        location = transformer._get_storage_location("legacy-not-found-uuid")
        assert location is None
        assert "legacy-not-found-uuid" not in transformer._storage_location_cache
        mock_fetch.assert_called_once()

@pytest.mark.unit
@pytest.mark.django_db
def test_get_storage_location_fallback_exception(product_storage_transformer, db_setup_product_storage):
    """Test fallback when legacy DB query raises an exception."""
    transformer = product_storage_transformer
    transformer._storage_location_cache = {}
    with patch('pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table') as mock_fetch:
        mock_fetch.side_effect = Exception("Legacy DB Error")
        location = transformer._get_storage_location("exception-uuid")
        assert location is None
        assert "exception-uuid" not in transformer._storage_location_cache
        mock_fetch.assert_called_once()

@pytest.mark.unit
@pytest.mark.django_db
def test_get_storage_location_no_uuid(product_storage_transformer):
    """Test calling _get_storage_location with None or empty string."""
    transformer = product_storage_transformer
    assert transformer._get_storage_location(None) is None
    assert transformer._get_storage_location("") is None
    assert None not in transformer._storage_location_cache
    assert "" not in transformer._storage_location_cache

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_with_box_id_only(product_storage_transformer, db_setup_product_storage):
    """Test getting the first box slot when only box_id is provided."""
    transformer = product_storage_transformer
    box1_slot1 = db_setup_product_storage['box1_slot1']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("box-123")
    assert slot == box1_slot1 
    assert transformer._box_slot_cache["box-123:1"] == box1_slot1

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_with_both_ids(product_storage_transformer, db_setup_product_storage):
    """Test getting a specific box slot using box_id and legacy_slot_id."""
    transformer = product_storage_transformer
    box1_slot2 = db_setup_product_storage['box1_slot2']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("box-123", legacy_slot_id="S2")
    assert slot == box1_slot2
    assert transformer._box_slot_cache["box-123:S2"] == box1_slot2

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_box_not_found(product_storage_transformer, db_setup_product_storage):
    """Test getting a slot when the box_id does not exist."""
    transformer = product_storage_transformer
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("nonexistent-box")
    assert slot is None
    assert "nonexistent-box:1" not in transformer._box_slot_cache
    slot = transformer._get_box_slot("nonexistent-box", legacy_slot_id="S1")
    assert slot is None
    assert "nonexistent-box:S1" not in transformer._box_slot_cache

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_no_slots_found(product_storage_transformer, db_setup_product_storage):
    """Test getting a slot for a box that exists but has no slots."""
    transformer = product_storage_transformer
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("box-noslots-456")
    assert slot is None
    # Verify that None is cached for this key
    assert transformer._box_slot_cache.get("box-noslots-456:1") is None

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_slot_not_found(product_storage_transformer, db_setup_product_storage):
    """Test getting a specific slot that doesn't exist for a valid box."""
    transformer = product_storage_transformer
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("box-123", legacy_slot_id="S3")
    assert slot is None
    assert "box-123:S3" not in transformer._box_slot_cache

@pytest.mark.unit
@pytest.mark.django_db
def test_get_box_slot_no_box_id(product_storage_transformer):
    """Test calling _get_box_slot with None or empty string for box_id."""
    transformer = product_storage_transformer
    assert transformer._get_box_slot(None) is None
    assert transformer._get_box_slot("") is None
    assert "None:1" not in transformer._box_slot_cache
    assert ":1" not in transformer._box_slot_cache

@pytest.mark.unit
def test_parse_quantity_valid(product_storage_transformer):
    """Test parsing valid quantity values."""
    transformer = product_storage_transformer
    assert transformer._parse_quantity(10) == 10
    assert transformer._parse_quantity("10") == 10
    assert transformer._parse_quantity(10.0) == 10
    assert transformer._parse_quantity("10.0") == 10
    assert transformer._parse_quantity("10.5") == 10

@pytest.mark.unit
def test_parse_quantity_invalid(product_storage_transformer):
    """Test parsing invalid quantity values."""
    transformer = product_storage_transformer
    assert transformer._parse_quantity("10abc") == 10
    assert transformer._parse_quantity("abc") == 0
    assert transformer._parse_quantity(None) == 0
    assert transformer._parse_quantity("") == 0
    assert transformer._parse_quantity(float('nan')) == 0

@pytest.mark.unit
def test_determine_status_available(product_storage_transformer):
    """Test that the default status is AVAILABLE."""
    transformer = product_storage_transformer
    assert transformer._determine_status({}) == ProductStorage.ReservationStatus.AVAILABLE
    assert transformer._determine_status({"Reserved": "FALSE", "Auftrags_Nr": "0"}) == ProductStorage.ReservationStatus.AVAILABLE

@pytest.mark.unit
def test_determine_status_reserved(product_storage_transformer):
    """Test detection of RESERVED status."""
    transformer = product_storage_transformer
    assert transformer._determine_status({"Reserved": "TRUE"}) == ProductStorage.ReservationStatus.RESERVED
    assert transformer._determine_status({"Reserved": "1"}) == ProductStorage.ReservationStatus.RESERVED
    assert transformer._determine_status({"Reserved": " Y "}) == ProductStorage.ReservationStatus.RESERVED
    assert transformer._determine_status({"Reserved": "YES", "Auftrags_Nr": "123"}) == ProductStorage.ReservationStatus.RESERVED

@pytest.mark.unit
def test_determine_status_allocated(product_storage_transformer):
    """Test detection of ALLOCATED status."""
    transformer = product_storage_transformer
    assert transformer._determine_status({"Auftrags_Nr": "12345"}) == ProductStorage.ReservationStatus.ALLOCATED
    assert transformer._determine_status({"Auftrags_Nr": " ORDER-XYZ "}) == ProductStorage.ReservationStatus.ALLOCATED
    assert transformer._determine_status({"Auftrags_Nr": " 0 "}) == ProductStorage.ReservationStatus.AVAILABLE
    assert transformer._determine_status({"Auftrags_Nr": ""}) == ProductStorage.ReservationStatus.AVAILABLE
    assert transformer._determine_status({"Reserved": "TRUE", "Auftrags_Nr": "12345"}) == ProductStorage.ReservationStatus.RESERVED

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_artikel_lagerorte_basic(product_storage_transformer, db_setup_product_storage):
    """Test basic successful transformation of an Artikel_Lagerorte record."""
    transformer = product_storage_transformer
    product_refOld = db_setup_product_storage['product_refOld']
    location_direct = db_setup_product_storage['location_direct']
    record = {
        "UUID": "ps-record-uuid-1",
        "ID_Artikel_Stamm": product_refOld.refOld,
        "UUID_Stamm_Lagerorte": location_direct.legacy_id,
        "Bestand": "50",
        "Reserved": "FALSE",
        "Auftrags_Nr": "ORD-111"
    }
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 1
    t_record = transformed[0]
    assert t_record["legacy_id"] == "ps-record-uuid-1"
    assert t_record["product"] == product_refOld
    assert t_record["storage_location"] == location_direct
    assert t_record["quantity"] == 50
    assert t_record["reservation_status"] == ProductStorage.ReservationStatus.ALLOCATED
    assert t_record["reservation_reference"] == "ORD-111"

@pytest.mark.unit
def test_transform_artikel_lagerorte_missing_product_id(product_storage_transformer):
    """Test skipping record if product ID is missing."""
    transformer = product_storage_transformer
    record = {"UUID": "ps-record-uuid-2", "UUID_Stamm_Lagerorte": "uuid"}
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_artikel_lagerorte_product_not_found(product_storage_transformer, db_setup_product_storage):
    """Test skipping record if product is not found."""
    transformer = product_storage_transformer
    record = {"ID_Artikel_Stamm": "nonexistent-prod", "UUID_Stamm_Lagerorte": "uuid"}
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_artikel_lagerorte_missing_location_uuid(product_storage_transformer, db_setup_product_storage):
    """Test skipping record if location UUID is missing."""
    transformer = product_storage_transformer
    product_refOld = db_setup_product_storage['product_refOld']
    record = {"ID_Artikel_Stamm": product_refOld.refOld}
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_artikel_lagerorte_location_not_found(product_storage_transformer, db_setup_product_storage):
    """Test skipping record if storage location is not found."""
    transformer = product_storage_transformer
    product_refOld = db_setup_product_storage['product_refOld']
    with patch('pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table') as mock_fetch:
        mock_fetch.return_value = pd.DataFrame()
        record = {
            "ID_Artikel_Stamm": product_refOld.refOld, 
            "UUID_Stamm_Lagerorte": "nonexistent-loc-uuid"
        }
        transformed = transformer.transform_artikel_lagerorte([record])
        assert len(transformed) == 0
        mock_fetch.assert_called_once()

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_artikel_lagerorte_no_reservation_ref(product_storage_transformer, db_setup_product_storage):
    """Test transformation when Auftrags_Nr is 0 or empty."""
    transformer = product_storage_transformer
    product_refOld = db_setup_product_storage['product_refOld']
    location_direct = db_setup_product_storage['location_direct']
    record = {
        "UUID": "ps-record-uuid-3",
        "ID_Artikel_Stamm": product_refOld.refOld,
        "UUID_Stamm_Lagerorte": location_direct.legacy_id,
        "Bestand": "10",
        "Auftrags_Nr": "0"
    }
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 1
    assert "reservation_reference" not in transformed[0]
    assert transformed[0]["reservation_status"] == ProductStorage.ReservationStatus.AVAILABLE
    record["Auftrags_Nr"] = "" 
    transformer._product_cache = {}
    transformer._storage_location_cache = {}
    transformed = transformer.transform_artikel_lagerorte([record])
    assert len(transformed) == 1
    assert "reservation_reference" not in transformed[0]
    assert transformed[0]["reservation_status"] == ProductStorage.ReservationStatus.AVAILABLE

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_selects_artikel_lagerorte(db_setup_product_storage):
    """Test that transform calls transform_artikel_lagerorte by default or explicitly."""
    product_refOld = db_setup_product_storage['product_refOld']
    location_direct = db_setup_product_storage['location_direct']
    transformer_explicit = ProductStorageTransformer({'source': 'Artikel_Lagerorte'})
    transformer_default = ProductStorageTransformer({})
    record = {
        "UUID": "ps-select-1",
        "ID_Artikel_Stamm": product_refOld.refOld, 
        "UUID_Stamm_Lagerorte": location_direct.legacy_id,
        "Bestand": "1"
    }
    with patch.object(transformer_explicit, 'transform_artikel_lagerorte', return_value=[]) as mock_transform_al:
        transformer_explicit.transform([record])
        mock_transform_al.assert_called_once_with([record])
    with patch.object(transformer_default, 'transform_artikel_lagerorte', return_value=[]) as mock_transform_al_default:
        transformer_default.transform([record])
        mock_transform_al_default.assert_called_once_with([record])

@pytest.mark.unit
def test_transform_selects_lager_schuetten_deprecated(caplog):
    """Test that transform handles the deprecated Lager_Schuetten source."""
    transformer = ProductStorageTransformer({'source': 'Lager_Schuetten'})
    record = {'ID': 'ls-select-1'}
    caplog.set_level(logging.INFO)
    result = transformer.transform([record])
    assert len(result) == 0
    assert "Transforming data from Lager_Schuetten" in caplog.text
    assert "transform_lager_schuetten is deprecated. Use BoxStorageTransformer instead." in caplog.text

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_selects_combined_deprecated(db_setup_product_storage, caplog):
    """Test that transform handles the deprecated combined source."""
    product_refOld = db_setup_product_storage['product_refOld']
    location_direct = db_setup_product_storage['location_direct']
    transformer = ProductStorageTransformer({'source': 'combined'})
    record = {
        "UUID": "ps-select-combined",
        "ID_Artikel_Stamm": product_refOld.refOld, 
        "UUID_Stamm_Lagerorte": location_direct.legacy_id,
        "Bestand": "1"
    }
    caplog.set_level(logging.WARNING)
    with patch.object(transformer, 'transform_artikel_lagerorte', return_value=[]) as mock_transform_al:
        transformer.transform([record])
        mock_transform_al.assert_called_once_with([record])
        assert "Combined source is deprecated. Use separate transformers for each table." in caplog.text

@pytest.mark.unit
def test_transform_unknown_source():
    """Test that transform raises error for unknown source."""
    transformer = ProductStorageTransformer({'source': 'invalid_source'})
    record = {'ID': 'unknown-select-1'}
    with pytest.raises(TransformError, match="Unknown source table: invalid_source"):
        transformer.transform([record])


# --- Fixtures for BoxStorageTransformer (no longer a class) --- #
@pytest.fixture
def box_storage_transformer():
    return BoxStorageTransformer({})

@pytest.fixture
def db_setup_box_storage(db):
    product = VariantProduct.objects.create(sku="BOX-TEST-SKU", name="Box Test Product")
    location = StorageLocation.objects.create(
        name="Box Test Location", legacy_id="box-loc-uuid",
        country="DE", city_building="B3", unit="U3", compartment="C3", shelf="S3"
    )
    product_storage = ProductStorage.objects.create(
        product=product, 
        storage_location=location, 
        quantity=100, 
        legacy_id="ps-uuid-123"
    )
    try:
        from pyerp.business_modules.inventory.models import BoxType
        box_type, _ = BoxType.objects.get_or_create(name="BST Test Type")
    except ImportError:
        box_type = None
        
    # Create Box in two steps
    box1 = Box.objects.create(
        code="BST-BOX1-CODE",
        box_type=box_type,
        legacy_id="bst-box-1" 
        # storage_location=location # Assign after save
    )
    box1.storage_location = location
    box1.save()
    
    box1_slot1 = BoxSlot.objects.create(box=box1, slot_code="BST-S1.1", legacy_slot_id="BST-S1")
    box1_slot2 = BoxSlot.objects.create(box=box1, slot_code="BST-S1.2", legacy_slot_id="BST-S2")
    
    box2_no_slots = Box.objects.create(
        code="BST-BOX2-CODE",
        box_type=box_type,
        legacy_id="bst-box-2"
        # storage_location=location # Assign after save
    )
    box2_no_slots.storage_location = location
    box2_no_slots.save()

    return {
        "product": product,
        "location": location,
        "product_storage": product_storage,
        "box1": box1,
        "box1_slot1": box1_slot1,
        "box1_slot2": box1_slot2,
        "box2_no_slots": box2_no_slots,
    }

# --- Test Functions for BoxStorageTransformer (was TestBoxStorageTransformer class) --- #

@pytest.mark.unit
def test_box_storage_transformer_init(box_storage_transformer):
    """Test initialization of BoxStorageTransformer."""
    transformer = box_storage_transformer
    assert transformer._product_storage_cache == {}
    assert transformer._box_slot_cache == {}

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_storage(box_storage_transformer, db_setup_box_storage):
    """Test getting a product storage by legacy_id (UUID)."""
    transformer = box_storage_transformer
    product_storage = db_setup_box_storage['product_storage']
    transformer._product_storage_cache = {}
    storage = transformer._get_product_storage("ps-uuid-123")
    assert storage == product_storage
    assert transformer._product_storage_cache["ps-uuid-123"] == product_storage

@pytest.mark.unit
@pytest.mark.django_db
def test_get_product_storage_not_found(box_storage_transformer, db_setup_box_storage):
    """Test getting a ProductStorage that doesn't exist."""
    transformer = box_storage_transformer
    transformer._product_storage_cache = {}
    storage = transformer._get_product_storage("nonexistent-ps-uuid")
    assert storage is None
    assert "nonexistent-ps-uuid" not in transformer._product_storage_cache

@pytest.mark.unit
@pytest.mark.django_db
def test_bst_get_box_slot_with_box_id_only(box_storage_transformer, db_setup_box_storage):
    """Test getting the first box slot using BoxStorageTransformer's method."""
    transformer = box_storage_transformer
    box1_slot1 = db_setup_box_storage['box1_slot1']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("bst-box-1")
    assert slot == box1_slot1
    assert transformer._box_slot_cache["bst-box-1:1"] == box1_slot1

@pytest.mark.unit
@pytest.mark.django_db
def test_bst_get_box_slot_with_both_ids(box_storage_transformer, db_setup_box_storage):
    """Test getting a specific box slot using BoxStorageTransformer's method."""
    transformer = box_storage_transformer
    box1_slot2 = db_setup_box_storage['box1_slot2']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("bst-box-1", legacy_slot_id="BST-S2")
    assert slot == box1_slot2
    assert transformer._box_slot_cache["bst-box-1:BST-S2"] == box1_slot2

@pytest.mark.unit
@pytest.mark.django_db
def test_bst_get_box_slot_box_not_found(box_storage_transformer, db_setup_box_storage):
    """Test BoxStorageTransformer's _get_box_slot when box not found."""
    transformer = box_storage_transformer
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot("bst-box-nonexistent")
    assert slot is None
    slot = transformer._get_box_slot("bst-box-nonexistent", legacy_slot_id="BST-S1")
    assert slot is None

@pytest.mark.unit
@pytest.mark.django_db
def test_bst_get_box_slot_no_slots_found(box_storage_transformer, db_setup_box_storage):
    """Test BoxStorageTransformer's _get_box_slot for box with no slots."""
    transformer = box_storage_transformer
    box2_no_slots = db_setup_box_storage['box2_no_slots']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot(box2_no_slots.legacy_id)
    assert slot is None

@pytest.mark.unit
@pytest.mark.django_db
def test_bst_get_box_slot_slot_not_found(box_storage_transformer, db_setup_box_storage):
    """Test BoxStorageTransformer's _get_box_slot for non-existent slot ID."""
    transformer = box_storage_transformer
    box1 = db_setup_box_storage['box1']
    transformer._box_slot_cache = {}
    slot = transformer._get_box_slot(box1.legacy_id, legacy_slot_id="BST-S3")
    assert slot is None

@pytest.mark.unit
def test_extract_box_data(box_storage_transformer):
    """Test extracting box data from input data."""
    transformer = box_storage_transformer
    input_data = {
        "ID": "legacy-id-123",
        "ID_Stamm_Lager_Schuetten": "box-123",
        "UUID_Artikel_Lagerorte": "storage-uuid-456",
        "data_": json.dumps({
            "Schuetten_ID": "schuette-789",
            "Artikel_Lagerort": "art-lager-101112",
            "Stamm_Lagerort": "stamm-lager-131415"
        }),
        "Relation_95_zurueck": json.dumps({
            "ID_Lager_Schuetten_Slots": "slot-5"
        })
    }
    result = transformer._extract_box_data(input_data)
    assert result["legacy_id"] == "legacy-id-123"
    assert result["box_id"] == "box-123"
    assert result["artikel_lagerorte_uuid"] == "storage-uuid-456"
    assert result["schuetten_id"] == "schuette-789"
    assert result["artikel_lagerort"] == "art-lager-101112"
    assert result["stamm_lagerort"] == "stamm-lager-131415"
    assert result["slot_id"] == "slot-5"

@pytest.mark.unit
def test_extract_box_data_missing_json(box_storage_transformer):
    """Test _extract_box_data when data_ or Relation_95_zurueck is missing/invalid."""
    transformer = box_storage_transformer
    input_data = {
        "ID": "legacy-id-nojson",
        "ID_Stamm_Lager_Schuetten": "box-nojson",
        "UUID_Artikel_Lagerorte": "storage-uuid-nojson",
        "data_": None,
        "Relation_95_zurueck": "invalid json"
    }
    result = transformer._extract_box_data(input_data)
    assert result["schuetten_id"] is None
    assert result["artikel_lagerort"] is None
    assert result["stamm_lagerort"] is None
    assert result.get("slot_id") is None
    input_data["data_"] = "invalid json"
    input_data["Relation_95_zurueck"] = None
    result = transformer._extract_box_data(input_data)
    assert result["schuetten_id"] is None
    assert result["artikel_lagerort"] is None
    assert result["stamm_lagerort"] is None
    assert result.get("slot_id") is None

@pytest.mark.unit
def test_bst_parse_quantity(box_storage_transformer):
    """Test parsing quantity values using BoxStorageTransformer."""
    transformer = box_storage_transformer
    assert transformer._parse_quantity(10) == 10
    assert transformer._parse_quantity("10") == 10
    assert transformer._parse_quantity(10.0) == 10
    assert transformer._parse_quantity("10.0") == 10
    assert transformer._parse_quantity("10.5") == 10
    assert transformer._parse_quantity("10abc") == 10
    assert transformer._parse_quantity("abc") == 0
    assert transformer._parse_quantity(None) == 0
    assert transformer._parse_quantity("") == 0
    assert transformer._parse_quantity(float('nan')) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_box_storage_basic(box_storage_transformer, db_setup_box_storage):
    """Test basic successful transformation of a Lager_Schuetten record."""
    transformer = box_storage_transformer
    product_storage = db_setup_box_storage['product_storage']
    box1 = db_setup_box_storage['box1']
    box1_slot1 = db_setup_box_storage['box1_slot1']
    record = {
        "ID": "bs-record-1",
        "UUID_Artikel_Lagerorte": product_storage.legacy_id,
        "ID_Stamm_Lager_Schuetten": box1.legacy_id,
        "Menge": "15",
        "Chargen_Nr": "BATCH123",
        "Ablaufdatum": "31.12.2025",
        "Relation_95_zurueck": json.dumps({
            "ID_Lager_Schuetten_Slots": box1_slot1.legacy_slot_id
        })
    }
    transformed = transformer.transform([record])
    assert len(transformed) == 1
    t_record = transformed[0]
    assert t_record["legacy_id"] == "bs-record-1"
    assert t_record["product_storage"] == product_storage
    assert t_record["box_slot"] == box1_slot1
    assert t_record["quantity"] == 15
    assert t_record["batch_number"] == "BATCH123"
    assert t_record["expiry_date"] == datetime.date(2025, 12, 31)
    assert t_record["position_in_slot"] == ""

@pytest.mark.unit
def test_transform_box_storage_missing_product_storage_uuid(box_storage_transformer):
    """Test skipping record if UUID_Artikel_Lagerorte is missing."""
    transformer = box_storage_transformer
    record = {"ID": "bs-record-2", "ID_Stamm_Lager_Schuetten": "box"}
    transformed = transformer.transform([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_box_storage_product_storage_not_found(box_storage_transformer, db_setup_box_storage):
    """Test skipping record if ProductStorage is not found."""
    transformer = box_storage_transformer
    record = {"UUID_Artikel_Lagerorte": "nonexistent-ps-uuid", "ID_Stamm_Lager_Schuetten": "box"}
    transformed = transformer.transform([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_box_storage_box_slot_not_found(box_storage_transformer, db_setup_box_storage):
    """Test skipping record if BoxSlot is not found."""
    transformer = box_storage_transformer
    product_storage = db_setup_box_storage['product_storage']
    record = {
        "UUID_Artikel_Lagerorte": product_storage.legacy_id,
        "ID_Stamm_Lager_Schuetten": "nonexistent-box"
    }
    transformed = transformer.transform([record])
    assert len(transformed) == 0

@pytest.mark.unit
@pytest.mark.django_db
def test_transform_box_storage_invalid_expiry_date(box_storage_transformer, db_setup_box_storage):
    """Test transformation with an invalid expiry date format."""
    transformer = box_storage_transformer
    product_storage = db_setup_box_storage['product_storage']
    box1 = db_setup_box_storage['box1']
    record = {
        "ID": "bs-record-3",
        "UUID_Artikel_Lagerorte": product_storage.legacy_id,
        "ID_Stamm_Lager_Schuetten": box1.legacy_id,
        "Menge": "5",
        "Ablaufdatum": "2025-12-31"
    }
    transformed = transformer.transform([record])
    assert len(transformed) == 1
    assert transformed[0]["expiry_date"] is None 