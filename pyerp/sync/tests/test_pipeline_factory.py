from unittest import mock
from django.test import TestCase

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.pipeline import PipelineFactory, SyncPipeline
from pyerp.sync.extractors.base import BaseExtractor
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.sync.loaders.base import BaseLoader


class MockExtractor(BaseExtractor):
    """Mock extractor for testing."""
    
    def get_required_config_fields(self):
        return []
        
    def connect(self):
        pass
        
    def extract(self, query_params=None):
        return []


class MockTransformer(BaseTransformer):
    """Mock transformer for testing."""
    
    def transform(self, source_data):
        return []


class MockLoader(BaseLoader):
    """Mock loader for testing."""
    
    def get_required_config_fields(self):
        return []
        
    def prepare_record(self, record):
        return {}, {}
        
    def load_record(self, lookup_criteria, record, update_existing=True):
        return None


class TestPipelineFactory(TestCase):
    """Tests for the PipelineFactory class."""

    def setUp(self):
        """Set up test data."""
        # Create source, target, and mapping
        extractor_path = "pyerp.sync.tests.test_pipeline_factory.MockExtractor"
        loader_path = "pyerp.sync.tests.test_pipeline_factory.MockLoader"
        transformer_path = (
            "pyerp.sync.tests.test_pipeline_factory.MockTransformer"
        )
        
        self.source = SyncSource.objects.create(
            name="test_source",
            description="Test source",
            config={
                "extractor_class": extractor_path
            }
        )
        
        self.target = SyncTarget.objects.create(
            name="test_target",
            description="Test target",
            config={
                "loader_class": loader_path
            }
        )
        
        self.mapping = SyncMapping.objects.create(
            source=self.source,
            target=self.target,
            entity_type="test_entity",
            mapping_config={
                "transformer_class": transformer_path
            }
        )
        
        # Store paths for later use in tests
        self.extractor_path = extractor_path
        self.transformer_path = transformer_path
        self.loader_path = loader_path

    def test_create_pipeline_with_defaults(self):
        """Test creating a pipeline with default component classes."""
        pipeline = PipelineFactory.create_pipeline(self.mapping)
        
        # Check that pipeline is created with correct components
        self.assertIsInstance(pipeline, SyncPipeline)
        self.assertIsInstance(pipeline.extractor, MockExtractor)
        self.assertIsInstance(pipeline.transformer, MockTransformer)
        self.assertIsInstance(pipeline.loader, MockLoader)
        self.assertEqual(pipeline.mapping, self.mapping)

    def test_create_pipeline_with_explicit_classes(self):
        """Test creating a pipeline with explicitly provided component classes."""
        pipeline = PipelineFactory.create_pipeline(
            self.mapping,
            extractor_class=MockExtractor,
            transformer_class=MockTransformer,
            loader_class=MockLoader
        )
        
        # Check that pipeline is created with correct components
        self.assertIsInstance(pipeline, SyncPipeline)
        self.assertIsInstance(pipeline.extractor, MockExtractor)
        self.assertIsInstance(pipeline.transformer, MockTransformer)
        self.assertIsInstance(pipeline.loader, MockLoader)

    @mock.patch('pyerp.sync.pipeline.PipelineFactory._import_class')
    def test_import_class_called_correctly(self, mock_import_class):
        """Test that _import_class is called with correct paths."""
        # Set up mock to return the mock classes
        mock_import_class.side_effect = [
            MockExtractor,
            MockTransformer,
            MockLoader
        ]
        
        # Create pipeline
        PipelineFactory.create_pipeline(self.mapping)
        
        # Check that _import_class was called with correct paths
        mock_import_class.assert_any_call(self.extractor_path)
        mock_import_class.assert_any_call(self.transformer_path)
        mock_import_class.assert_any_call(self.loader_path)

    def test_import_class(self):
        """Test the _import_class method."""
        # Import a real class
        cls = PipelineFactory._import_class(self.extractor_path)
        self.assertEqual(cls, MockExtractor)

    def test_import_class_error(self):
        """Test that _import_class raises ImportError for invalid paths."""
        with self.assertRaises(ImportError):
            PipelineFactory._import_class("nonexistent.module.Class")

    def test_create_component(self):
        """Test the _create_component method."""
        # Create a component with config
        config = {"test_key": "test_value"}
        component = PipelineFactory._create_component(
            MockExtractor, config
        )
        
        # Check that component was created with config
        self.assertIsInstance(component, MockExtractor)
        self.assertEqual(component.config, config) 