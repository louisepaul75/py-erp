from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from django.utils import timezone
from pyerp.business_modules.sales.models import (
    SalesRecord, SalesRecordRelationship, Customer
)
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@override_settings(ROOT_URLCONF='pyerp.urls')
class SalesRecordRelationshipAPITests(TransactionTestCase):

    def setUp(self):
        """Set up data for each test method individually."""
        SalesRecordRelationship.objects.all().delete()

        # Create a user for authentication
        self.user = User.objects.create_user(
            username='api_test_user', password='password123'
        )
        # Instantiate APIClient and force authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create customer and records needed for relationships
        self.customer = Customer.objects.create(
            customer_number="CUST-API-001", name="API Test Customer"
        )
        self.record1 = SalesRecord.objects.create(
            customer=self.customer, record_number="API-REC-001",
            record_date=timezone.now().date(), record_type="INVOICE"
        )
        self.record2 = SalesRecord.objects.create(
            customer=self.customer, record_number="API-REC-002",
            record_date=timezone.now().date(), record_type="DELIVERY_NOTE"
        )
        self.record3 = SalesRecord.objects.create(
            customer=self.customer, record_number="API-REC-003",
            record_date=timezone.now().date(), record_type="CREDIT_NOTE"
        )
        # Create the relationship needed for list/retrieve/update/delete tests
        self.test_relationship = SalesRecordRelationship.objects.create(
            from_record=self.record1, to_record=self.record2,
            relationship_type="RELATES_TO"
        )

        # Base URL for the relationship endpoint
        self.base_url = reverse('sales_api:salesrecordrelationship-list')

    def test_create_relationship(self):
        """Test creating a new sales record relationship via POST."""
        url = self.base_url
        data = {
            "from_record": self.record2.pk,  # Use different records for create
            "to_record": self.record3.pk,
            "relationship_type": "REFERENCES",
            "notes": "Record 3 references Record 2",
        }
        initial_count = SalesRecordRelationship.objects.count()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check count increased by 1 from the state set in setUp
        self.assertEqual(
            SalesRecordRelationship.objects.count(), initial_count + 1
        )
        new_rel = SalesRecordRelationship.objects.get(
            relationship_type="REFERENCES"
        )
        self.assertEqual(new_rel.from_record, self.record2)
        self.assertEqual(new_rel.to_record, self.record3)

    def test_list_relationships(self):
        """Test retrieving a list of relationships via GET."""
        url = self.base_url
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only list the one created in setUp for this specific test run
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.test_relationship.pk)
        self.assertEqual(response.data[0]['from_record'], self.record1.pk)
        self.assertEqual(response.data[0]['to_record'], self.record2.pk)

    def test_retrieve_relationship(self):
        """Test retrieving a specific relationship via GET."""
        rel_pk = self.test_relationship.pk
        url = reverse(
            'sales_api:salesrecordrelationship-detail', kwargs={'pk': rel_pk}
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], rel_pk)
        self.assertEqual(response.data['relationship_type'], "RELATES_TO")

    def test_update_relationship(self):
        """Test updating a relationship via PUT."""
        rel_pk = self.test_relationship.pk
        url = reverse(
            'sales_api:salesrecordrelationship-detail', kwargs={'pk': rel_pk}
        )
        data = {
            "from_record": self.record1.pk,
            "to_record": self.record3.pk,  # Change target record
            "relationship_type": "CREDITS",  # Change type
            "notes": "Updated relationship",
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Fetch directly from DB to verify update
        updated_rel = SalesRecordRelationship.objects.get(pk=rel_pk)
        self.assertEqual(updated_rel.to_record, self.record3)
        self.assertEqual(updated_rel.relationship_type, "CREDITS")

    def test_partial_update_relationship(self):
        """Test partially updating a relationship via PATCH."""
        rel_pk = self.test_relationship.pk
        url = reverse(
            'sales_api:salesrecordrelationship-detail', kwargs={'pk': rel_pk}
        )
        data = {"notes": "Partially updated notes"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_rel = SalesRecordRelationship.objects.get(pk=rel_pk)
        self.assertEqual(updated_rel.notes, "Partially updated notes")
        self.assertEqual(updated_rel.relationship_type, "RELATES_TO")

    def test_delete_relationship(self):
        """Test deleting a relationship via DELETE."""
        # Target the one from setUp
        rel_pk_to_delete = self.test_relationship.pk
        initial_count = SalesRecordRelationship.objects.count()

        url = reverse(
            'sales_api:salesrecordrelationship-detail',
            kwargs={'pk': rel_pk_to_delete}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should be zero relationships left for this test's transaction
        self.assertEqual(
            SalesRecordRelationship.objects.count(), initial_count - 1
        )
        self.assertEqual(SalesRecordRelationship.objects.count(), 0)
        with self.assertRaises(SalesRecordRelationship.DoesNotExist):
            SalesRecordRelationship.objects.get(pk=rel_pk_to_delete)


@override_settings(ROOT_URLCONF='pyerp.urls')
class SalesRecordFlowDataAPITests(TransactionTestCase):

    def setUp(self):
        """Set up data for each flow test method individually."""
        # Create user and authenticate client for each test
        self.user = User.objects.create_user(
            username='flow_test_user', password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create data needed for flow tests
        self.customer = Customer.objects.create(
            customer_number="CUST-FLOW-001", name="Flow Test Customer"
        )
        self.record_center = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-CENTER",
            record_date=timezone.now().date(), record_type="INVOICE"
        )
        self.record_outgoing1 = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-OUT-1",
            record_date=timezone.now().date(), record_type="DELIVERY_NOTE"
        )
        self.record_outgoing2 = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-OUT-2",
            record_date=timezone.now().date(), record_type="DELIVERY_NOTE"
        )
        self.record_incoming1 = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-IN-1",
            record_date=timezone.now().date(), record_type="PROPOSAL"
        )
        self.record_incoming2 = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-IN-2",
            record_date=timezone.now().date(),
            record_type="ORDER_CONFIRMATION"
        )
        # Create relationships within setUp
        self.rel_out1 = SalesRecordRelationship.objects.create(
            from_record=self.record_center, to_record=self.record_outgoing1,
            relationship_type="RELATES_TO"
        )
        self.rel_out2 = SalesRecordRelationship.objects.create(
            from_record=self.record_center, to_record=self.record_outgoing2,
            relationship_type="SPLIT_FROM"
        )
        self.rel_in1 = SalesRecordRelationship.objects.create(
            from_record=self.record_incoming1, to_record=self.record_center,
            relationship_type="REFERENCES"
        )
        self.rel_in2 = SalesRecordRelationship.objects.create(
            from_record=self.record_incoming2, to_record=self.record_center,
            relationship_type="RELATES_TO"
        )

    def tearDown(self):
        """Clean up SalesRecordRelationship objects after each test."""
        SalesRecordRelationship.objects.all().delete()
        # Also potentially delete SalesRecord objects if they interfere,
        # but start with relationships
        SalesRecord.objects.all().delete()
        # Also delete the user
        self.user.delete()

    def test_flow_data_structure(self):
        """Test the structure of the flow-data endpoint response."""
        # Use the name generated by DefaultRouter: {basename}-{method_name}
        url = reverse(
            'sales_api:salesrecord-flow-data',
            kwargs={'pk': self.record_center.pk}
        )
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('nodes', response.data)
        self.assertIn('edges', response.data)

        nodes = response.data['nodes']
        edges = response.data['edges']

        # Expect 5 nodes: center, 2 outgoing, 2 incoming
        self.assertEqual(len(nodes), 5)
        # Expect 4 edges: 2 outgoing, 2 incoming
        self.assertEqual(len(edges), 4)

        node_ids = {node['id'] for node in nodes}
        expected_node_ids = {
            f'record_{self.record_center.pk}',
            f'record_{self.record_outgoing1.pk}',
            f'record_{self.record_outgoing2.pk}',
            f'record_{self.record_incoming1.pk}',
            f'record_{self.record_incoming2.pk}',
        }
        self.assertSetEqual(node_ids, expected_node_ids)

        # Check structure of one node
        center_node = next(
            n for n in nodes if n['id'] == f'record_{self.record_center.pk}'
        )
        self.assertEqual(center_node['type'], 'salesRecordNode')
        self.assertIn('position', center_node)
        self.assertIn('data', center_node)
        self.assertEqual(center_node['data']['pk'], self.record_center.pk)
        self.assertEqual(
            center_node['data']['record_number'],
            self.record_center.record_number
        )

        # Check structure of one edge (outgoing)
        edge_out1 = next(
            e for e in edges if e['id'] == f'rel_{self.rel_out1.pk}'
        )
        self.assertEqual(
            edge_out1['source'], f'record_{self.record_center.pk}'
        )
        self.assertEqual(
            edge_out1['target'], f'record_{self.record_outgoing1.pk}'
        )
        self.assertEqual(edge_out1['type'], 'relationshipEdge')
        self.assertEqual(
            edge_out1['label'], self.rel_out1.get_relationship_type_display()
        )
        self.assertIn('data', edge_out1)
        self.assertEqual(edge_out1['data']['pk'], self.rel_out1.pk)

        # Check structure of one edge (incoming)
        edge_in1 = next(
            e for e in edges if e['id'] == f'rel_{self.rel_in1.pk}'
        )
        self.assertEqual(
            edge_in1['source'], f'record_{self.record_incoming1.pk}'
        )
        self.assertEqual(edge_in1['target'], f'record_{self.record_center.pk}')
        self.assertEqual(edge_in1['type'], 'relationshipEdge')
        self.assertEqual(
            edge_in1['label'], self.rel_in1.get_relationship_type_display()
        )
        self.assertIn('data', edge_in1)
        self.assertEqual(edge_in1['data']['pk'], self.rel_in1.pk)

    def test_flow_data_no_relationships(self):
        """Test flow-data for a record with no relationships."""
        # Create a record with no links
        isolated_record = SalesRecord.objects.create(
            customer=self.customer, record_number="FLOW-ISOLATED",
            record_date=timezone.now().date(), record_type="INVOICE"
        )
        url = reverse(
            'sales_api:salesrecord-flow-data',
            kwargs={'pk': isolated_record.pk}
        )
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['nodes']), 1)
        self.assertEqual(len(response.data['edges']), 0)
        self.assertEqual(
            response.data['nodes'][0]['id'], f'record_{isolated_record.pk}'
        )

    def test_flow_data_not_found(self):
        """Test flow-data for a non-existent record ID."""
        # Get last existing pk and add a large number
        latest_pk = SalesRecord.objects.latest('pk').pk
        non_existent_pk = latest_pk + 1000
        url = reverse(
            'sales_api:salesrecord-flow-data', kwargs={'pk': non_existent_pk}
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 