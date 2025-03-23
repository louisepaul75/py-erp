import pytest
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


@pytest.mark.unit
class TestPipelineFactory(TestCase):
    """Tests for the PipelineFactory class."""

    def setUp(self):
        """Set up test data with mocks instead of real DB objects."""
        # Define component paths
        extractor_path = "pyerp.sync.tests.test_pipeline_factory.MockExtractor"
        loader_path = "pyerp.sync.tests.test_pipeline_factory.MockLoader"
        transformer_path = "pyerp.sync.tests.test_pipeline_factory.MockTransformer"

        # Create mock objects instead of database objects
        self.source = mock.MagicMock(spec=SyncSource)
        self.source.name = "test_source"
        self.source.description = "Test source"
        self.source.config = {"extractor_class": extractor_path}

        self.target = mock.MagicMock(spec=SyncTarget)
        self.target.name = "test_target"
        self.target.description = "Test target"
        self.target.config = {"loader_class": loader_path}

        self.mapping = mock.MagicMock(spec=SyncMapping)
        self.mapping.source = self.source
        self.mapping.target = self.target
        self.mapping.entity_type = "test_entity"
        self.mapping.mapping_config = {"transformer_class": transformer_path}

        # Store paths for later use in tests
        self.extractor_path = extractor_path
        self.transformer_path = transformer_path
        self.loader_path = loader_path

    @mock.patch("pyerp.sync.pipeline.PipelineFactory._create_component")
    @mock.patch("pyerp.sync.pipeline.SyncPipeline")
















    def test_create_pipeline_with_defaults(self, mock_pipeline_class, mock_create_component):
        """Test creating a pipeline with default component classes."""
        # Create mock components to return
        mock_extractor = MockExtractor({})
        mock_transformer = MockTransformer({})
        mock_loader = MockLoader({})
        
        # Set up the mock to return our mock components
        mock_create_component.side_effect = [mock_extractor, mock_transformer, mock_loader]
        
        # Set up mock pipeline instance
        mock_pipeline_instance = mock.MagicMock()
        mock_pipeline_class.return_value = mock_pipeline_instance
        
        # Create pipeline
        pipeline = PipelineFactory.create_pipeline(self.mapping)

        # Check that SyncPipeline was initialized with correct components
        mock_pipeline_class.assert_called_once_with(
            self.mapping, mock_extractor, mock_transformer, mock_loader
        )
        
        # Check that pipeline is the mocked instance
        self.assertEqual(pipeline, mock_pipeline_instance)

    @mock.patch("pyerp.sync.pipeline.PipelineFactory._create_component")
    @mock.patch("pyerp.sync.pipeline.SyncPipeline")


    def test_create_pipeline_with_explicit_classes(self, mock_pipeline_class, mock_create_component):
        """Test creating a pipeline with explicitly provided component classes."""
        # Create mock components to return
        mock_extractor = MockExtractor({})
        mock_transformer = MockTransformer({})
        mock_loader = MockLoader({})
        
        # Set up the mock to return our mock components
        mock_create_component.side_effect = [mock_extractor, mock_transformer, mock_loader]
        
        # Set up mock pipeline instance
        mock_pipeline_instance = mock.MagicMock()
        mock_pipeline_class.return_value = mock_pipeline_instance
        
        pipeline = PipelineFactory.create_pipeline(
            self.mapping,
            extractor_class=MockExtractor,
            transformer_class=MockTransformer,
            loader_class=MockLoader,
        )

        # Check that SyncPipeline was initialized with correct components
        mock_pipeline_class.assert_called_once_with(
            self.mapping, mock_extractor, mock_transformer, mock_loader
        )
        
        # Check that pipeline is the mocked instance
        self.assertEqual(pipeline, mock_pipeline_instance)

    @mock.patch("pyerp.sync.pipeline.PipelineFactory._import_class")
    @mock.patch("pyerp.sync.pipeline.SyncPipeline")


    def test_import_class_called_correctly(self, mock_pipeline_class, mock_import_class):
        """Test that _import_class is called with correct paths."""
        # Set up mock to return the mock classes
        mock_import_class.side_effect = [MockExtractor, MockTransformer, MockLoader]
        
        # Set up mock pipeline instance
        mock_pipeline_instance = mock.MagicMock()
        mock_pipeline_class.return_value = mock_pipeline_instance

        # Create pipeline
        PipelineFactory.create_pipeline(self.mapping)

        # Check that _import_class was called with correct paths
        mock_import_class.assert_any_call(self.extractor_path)
        mock_import_class.assert_any_call(self.transformer_path)
        mock_import_class.assert_any_call(self.loader_path)




    def test_import_class(self):
        """Test the _import_class method."""
        # Import a real class from the current module
        cls = PipelineFactory._import_class("pyerp.sync.tests.test_pipeline_factory.MockExtractor")
        
        # Import the class directly for comparison
        from pyerp.sync.tests.test_pipeline_factory import MockExtractor as DirectMockExtractor
        
        # Verify they are the same class
        self.assertIs(cls, DirectMockExtractor)




    def test_import_class_error(self):
        """Test that _import_class raises ImportError for invalid paths."""
        with self.assertRaises(ImportError):
            PipelineFactory._import_class("nonexistent.module.Class")

    @mock.patch("pyerp.sync.pipeline.PipelineFactory._import_class")


    def test_create_component(self, mock_import_class):
        """Test the _create_component method."""
        # Set up mock to return MockExtractor
        mock_import_class.return_value = MockExtractor
        
        # Create a component with config
        config = {"test_key": "test_value"}
        component = PipelineFactory._create_component(MockExtractor, config)

        # Check that component was created with config
        self.assertIsInstance(component, MockExtractor)
        self.assertEqual(component.config, config)
