import unittest
from django.test import RequestFactory

from pyerp.business_modules.sales.views import SalesViewSet


class TestViewSet(unittest.TestCase):
    """Test the SalesViewSet class in sales module"""

    def setUp(self):
        """Set up test case"""
        self.viewset = SalesViewSet()
        self.factory = RequestFactory()

    def test_viewset_init(self):
        """Test that SalesViewSet initializes correctly"""
        # Check that the ViewSet exists
        self.assertIsNotNone(self.viewset)

    def test_docstring(self):
        """Test that SalesViewSet has a docstring"""
        self.assertIsNotNone(SalesViewSet.__doc__) 