# External API Integration

This package contains modules for integrating with external APIs used by the pyERP system.

## Structure

The package is organized by external API system:

- `legacy_erp/` - Integration with the legacy 4D-based ERP system
- `images_cms/` - Integration with the external image content management system

## Legacy ERP API

The `legacy_erp` module provides functionality for interacting with the legacy 4D-based ERP system. It includes:

- Authentication and session management
- Data retrieval and updates
- Error handling and retry logic

For usage examples, see the module's README.md file.

## Images CMS API

The `images_cms` module provides functionality for interacting with the external image content management system. It includes:

- Authentication and connection management
- Image search and retrieval
- Image metadata parsing
- Format and resolution prioritization

For usage examples, see the module's README.md file.

## Migration from Previous Structure

This package replaces the following modules:

- `pyerp.direct_api` → `pyerp.external_api.legacy_erp`
- `pyerp.legacy_sync.api_client` → `pyerp.external_api.legacy_erp.api_client`
- `pyerp.products.image_api` → `pyerp.external_api.images_cms`

The old modules will continue to work through compatibility imports, but new code should use the new structure. 