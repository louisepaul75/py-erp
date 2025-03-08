"""
Legacy sync module for pyERP.

This module is deprecated and will be removed in a future version.
Please use pyerp.external_api.legacy_erp instead.
"""

import logging
import warnings

# Configure logging
logger = logging.getLogger(__name__)

# Show deprecation warning
warnings.warn(
    "The legacy_sync module is deprecated. Please use pyerp.external_api.legacy_erp instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Log deprecation
logger.warning(
    "The legacy_sync module is deprecated. Please use pyerp.external_api.legacy_erp instead."
)

default_app_config = "pyerp.legacy_sync.apps.LegacySyncConfig"

# Keep the old imports for backward compatibility
from .models import (  # noqa: F401
    SyncMapping,
    SyncSource,
    SyncTarget,
    EntityMappingConfig,
)
from .sync_tasks import (  # noqa: F401
    sync_products,
    sync_all,
    sync_entity,
)
from .tasks import (  # noqa: F401
    sync_products_task,
    sync_all_task,
)
