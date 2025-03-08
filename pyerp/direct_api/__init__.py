"""
Direct API module for the legacy ERP system.

This module is kept for backward compatibility. New code should use 
pyerp.external_api.legacy_erp instead.
"""

import importlib
import logging
import sys
import warnings

# Configure logging
logger = logging.getLogger(__name__)

# Import everything from the new structure
from pyerp.external_api.legacy_erp import *

# Show deprecation warning
warnings.warn(
    "The direct_api module is deprecated. Please use pyerp.external_api.legacy_erp instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Log deprecation
logger.warning(
    "The direct_api module is deprecated. Please use pyerp.external_api.legacy_erp instead."
)
