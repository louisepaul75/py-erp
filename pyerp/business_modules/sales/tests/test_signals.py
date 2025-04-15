from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from pyerp.business_modules.sales.models import (
    SalesRecord, SalesRecordItem, Customer
)

# Define status constants locally for clarity in tests
PENDING = "PENDING"
PARTIALLY_DELIVERED = "PARTIALLY_DELIVERED"
FULLY_DELIVERED = "FULLY_DELIVERED"
CANCELLED = "CANCELLED"  # Item fulfillment status


class DeliveryStatusSignalTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a dummy customer needed for SalesRecord foreign key
        cls.customer = Customer.objects.create(
            customer_number="CUST-001", name="Test Customer Signal"
        )
        # Create a sales record to test with
        cls.record = SalesRecord.objects.create(
            customer=cls.customer,
            record_number="SIG-TEST-001",
            record_date=timezone.now().date(),
            record_type="INVOICE",
        )
        # Ensure initial status is PENDING after creation (no items yet)
        cls.record.refresh_from_db()
        assert cls.record.delivery_status == PENDING

    def test_01_no_items_status(self):
        """Test that a record with no items has PENDING status."""
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PENDING)

    def test_02_add_pending_item(self):
        """Test adding an item with zero fulfillment keeps status PENDING."""
        SalesRecordItem.objects.create(
            sales_record=self.record,
            position=1,
            description="Item 1",
            quantity=Decimal("10.00"),
            unit_price=Decimal("5.00"),
            fulfilled_quantity=Decimal("0.00"),
            fulfillment_status=PENDING,  # Explicitly PENDING item status
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PENDING)

    def test_03_update_to_partial_fulfillment(self):
        """Test update item to partial fulfillment changes status to PARTIALLY_DELIVERED."""
        item = SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=0
        )
        # Update the item - this triggers the post_save signal
        item.fulfilled_quantity = Decimal("5.00")
        item.fulfillment_status = "PARTIAL"  # Update item status too
        item.save()
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)

    def test_04_add_second_item_partial(self):
        """Test adding a 2nd partially fulfilled item keeps PARTIALLY_DELIVERED."""
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=5, fulfillment_status="PARTIAL"
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=2, fulfillment_status="PARTIAL"
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)

    def test_05_update_one_item_to_full(self):
        """Test updating one item to full, while another is partial -> PARTIALLY_DELIVERED."""
        item1 = SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=5, fulfillment_status="PARTIAL"
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=2, fulfillment_status="PARTIAL"
        )
        # Update item1 to full
        item1.fulfilled_quantity = item1.quantity
        item1.fulfillment_status = "FULFILLED"
        item1.save()
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)

    def test_06_update_all_items_to_full(self):
        """Test updating all items to full fulfillment changes status to FULLY_DELIVERED."""
        item1 = SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=5
        )
        item2 = SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=2
        )
        # Update both items to full
        item1.fulfilled_quantity = item1.quantity
        item1.fulfillment_status = "FULFILLED"
        item1.save()
        item2.fulfilled_quantity = item2.quantity
        item2.fulfillment_status = "FULFILLED"
        item2.save()
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, FULLY_DELIVERED)

    def test_07_delete_item_from_fully_delivered(self):
        """Test deleting an item when FULLY_DELIVERED updates status correctly."""
        item1 = SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=10, fulfillment_status="FULFILLED"
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=5, fulfillment_status="FULFILLED"
        )
        # Ensure it starts as fully delivered
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, FULLY_DELIVERED)
        # Delete item1 - triggers post_delete signal
        item1.delete()
        self.record.refresh_from_db()
        # Should still be fully delivered as remaining item is full
        self.assertEqual(self.record.delivery_status, FULLY_DELIVERED)

    def test_08_delete_last_item(self):
        """Test deleting the last item changes status back to PENDING."""
        item1 = SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=5, fulfillment_status="PARTIAL"
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)
        # Delete the only item
        item1.delete()
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PENDING)

    def test_09_cancelled_item_ignored(self):
        """Test that items with fulfillment_status='CANCELLED' are ignored."""
        # Add one fulfilled item and one cancelled item
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=10, fulfillment_status="FULFILLED"
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=0, fulfillment_status=CANCELLED
        )
        self.record.refresh_from_db()
        # Should be FULLY_DELIVERED as the cancelled item is ignored
        self.assertEqual(self.record.delivery_status, FULLY_DELIVERED)

    def test_10_only_cancelled_items(self):
        """Test that if all items are cancelled, status becomes PENDING."""
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=0, fulfillment_status=CANCELLED
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=0, fulfillment_status=CANCELLED
        )
        self.record.refresh_from_db()
        # According to logic (item_count becomes 0), defaults to PENDING
        self.assertEqual(self.record.delivery_status, PENDING)

    def test_11_mix_pending_and_partial(self):
        """Test mix of pending/partial items results in PARTIALLY_DELIVERED."""
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=0, fulfillment_status=PENDING
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=2, fulfillment_status="PARTIAL"
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)

    def test_12_mix_pending_and_fulfilled(self):
        """Test mix of pending/fulfilled items results in PARTIALLY_DELIVERED."""
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=0, fulfillment_status=PENDING
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=5, fulfillment_status="FULFILLED"
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED)

    def test_13_mix_partial_and_fulfilled(self):
        """Test mix of partial/fulfilled items results in PARTIALLY_DELIVERED."""
        SalesRecordItem.objects.create(
            sales_record=self.record, position=1, quantity=10,
            fulfilled_quantity=3, fulfillment_status="PARTIAL"
        )
        SalesRecordItem.objects.create(
            sales_record=self.record, position=2, quantity=5,
            fulfilled_quantity=5, fulfillment_status="FULFILLED"
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.delivery_status, PARTIALLY_DELIVERED) 