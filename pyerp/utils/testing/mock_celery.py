"""
Mock implementation of Celery for testing.

This module provides a mock implementation of the Celery package to allow
Django to run without actual Celery dependencies during testing.
"""

import sys
import types
from datetime import timedelta


class MockCelery:
    """Mock implementation of the Celery package."""
    
    def __init__(self):
        """Initialize the mock."""
        # Create the main celery module
        self.celery = types.ModuleType("celery")
        
        # Create the states module
        self.states = types.ModuleType("celery.states")
        self.states.PENDING = 'PENDING'
        self.states.RECEIVED = 'RECEIVED'
        self.states.STARTED = 'STARTED'
        self.states.SUCCESS = 'SUCCESS'
        self.states.FAILURE = 'FAILURE'
        self.states.REVOKED = 'REVOKED'
        self.states.RETRY = 'RETRY'
        self.states.IGNORED = 'IGNORED'
        self.states.READY_STATES = frozenset({self.states.SUCCESS, self.states.FAILURE, self.states.REVOKED})
        self.states.UNREADY_STATES = frozenset({self.states.PENDING, self.states.RECEIVED, 
                                              self.states.STARTED, self.states.RETRY})
        self.states.EXCEPTION_STATES = frozenset({self.states.FAILURE, self.states.RETRY, self.states.REVOKED})
        self.states.PROPAGATE_STATES = frozenset({self.states.FAILURE, self.states.REVOKED})
        
        # Create the result module
        self.result = types.ModuleType("celery.result")
        self.result.GroupResult = type('GroupResult', (), {})
        self.result.result_from_tuple = lambda x: None
        
        # Create the utils module
        self.utils = types.ModuleType("celery.utils")
        
        # Create the utils.time module
        self.utils_time = types.ModuleType("celery.utils.time")
        self.utils_time.maybe_timedelta = lambda x: x if isinstance(x, timedelta) else timedelta(seconds=x)
        
        # Create backends module
        self.backends = types.ModuleType("celery.backends")
        self.backends.database = types.ModuleType("celery.backends.database")
        self.backends.database.models = types.ModuleType("celery.backends.database.models")
        self.backends.database.models.Task = type('Task', (), {})
        
        # Create the django-celery-results helpers
        self.django_celery_results = types.ModuleType("django_celery_results")
        self.django_celery_results.managers = types.ModuleType("django_celery_results.managers")
        
        # Create the Celery class
        self.celery.Celery = type('Celery', (), {
            '__init__': lambda self, *args, **kwargs: None,
            'config_from_object': lambda self, *args, **kwargs: None,
            'autodiscover_tasks': lambda self, *args, **kwargs: None,
            'task': lambda self, *args, **kwargs: lambda func: func
        })
        
        # Connect modules
        self.celery.states = self.states
        self.celery.result = self.result
        self.celery.utils = self.utils
        self.utils.time = self.utils_time
        self.celery.backends = self.backends
        
        # Add app instance
        self.celery.app = self.celery.Celery()
    
    def install(self):
        """Install the mock into sys.modules."""
        # Check if real modules are already loaded
        modules_to_mock = [
            "celery", 
            "celery.states", 
            "celery.result", 
            "celery.utils",
            "celery.utils.time",
            "celery.backends",
            "celery.backends.database",
            "celery.backends.database.models"
        ]
        
        for name in modules_to_mock:
            if name in sys.modules:
                del sys.modules[name]
        
        # Install our mocks
        sys.modules["celery"] = self.celery
        sys.modules["celery.states"] = self.states
        sys.modules["celery.result"] = self.result
        sys.modules["celery.utils"] = self.utils
        sys.modules["celery.utils.time"] = self.utils_time
        sys.modules["celery.backends"] = self.backends
        sys.modules["celery.backends.database"] = self.backends.database
        sys.modules["celery.backends.database.models"] = self.backends.database.models
        
        return self 