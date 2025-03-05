# pyERP

A modern Django-based ERP system designed to replace a legacy 4D-based ERP, focusing on manufacturing operations with both B2B and B2C sales channels.

[![Lint](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml/badge.svg?job=lint)](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml)
[![Tests](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml/badge.svg?job=tests)](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml)
[![Build](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml/badge.svg?job=build)](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/docker-build.yml)
[![Deploy](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/deploy.yml/badge.svg)](https://github.com/Wilhelm-Schweizer/pyERP/actions/workflows/deploy.yml)
[![codecov](https://codecov.io/gh/Wilhelm-Schweizer/pyERP/branch/main/graph/badge.svg)](https://codecov.io/gh/Wilhelm-Schweizer/pyERP)

## Project Overview

pyERP is a monolithic Django application organized into modular Django apps representing key business domains. The system manages:

- Product & BOM Management
- Sales Management (Quotes, Orders, Invoicing)
- Production Management
- Warehouse/Inventory Management
- Integration with POS and eCommerce systems

## Development Approach

This project uses a phased development approach:

1. **Phase 0: Foundation** - Setting up the project structure, legacy data synchronization, and core models
2. **Phase 1: MVP** - Basic functionality for Products, Sales, Inventory and minimal Production
3. **Phase 2: Enhanced Features** - Multi-warehouse, advanced production, and external integrations
4. **Phase 3: Advanced Features** - Accounting integration, analytics, and further automation

The development strategy includes building a one-way synchronization with the legacy ERP system to facilitate a module-by-module migration approach.

## Git Workflow & Branching Strategy

This project follows a modified GitFlow workflow:

### Main Branches
- **`prod`**: Production-ready code, always stable and deployable
- **`dev`**: Integration branch for active development

### Supporting Branches
- **`feature/*`**: For new features (e.g., `feature/product-bom-creation`)
- **`bugfix/*`**: For bug fixes in development
- **`hotfix/*`**: For critical fixes that need to go directly to production
- **`release/*`**: For preparing version releases (e.g., `release/1.0.0`)

### Version Strategy
We use Semantic Versioning (SemVer) with phase indicators: `MAJOR.MINOR.PATCH-PHASE`

- Current version: See [VERSION.md](VERSION.md)
- Version lifecycle: alpha → beta → release candidate → final release

### Contributing
For detailed contribution guidelines, including branch naming conventions, commit message formats, and pull request procedures, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Getting Started

### Prerequisites

- Python 3.13.2
- PostgreSQL 15.0+
- Docker and Docker Compose (for development environment)

### Environment Configuration

Environment configuration files are located in the `config/env/` directory:

- `.env` or `.env.dev` - Development environment variables
- `.env.prod` - Production environment variables
- `.env.dev.example` - Example development configuration template
- `.env.prod.example` - Example production configuration template

For compatibility, symlinks to these files exist in the project root. Always make changes to the original files in `config/env/`.

#### Database Configuration

The project uses PostgreSQL for all environments (development, staging, and production) to ensure consistency. For detailed PostgreSQL setup instructions, see [docs/development/postgres_setup.md](docs/development/postgres_setup.md).

Key database environment variables:
```
DB_NAME=pyerp_testing
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/your-organization/pyERP.git
cd pyERP
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements/development.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the development environment with Docker Compose:

```bash
./scripts/docker/run_docker_dev.sh
```

Or manually:

```bash
docker-compose up -d
```

6. Run migrations:

```bash
python manage.py migrate
```

7. Create a superuser:

```bash
python manage.py createsuperuser
```

8. Run the development server:

```bash
python manage.py runserver
```

9. Visit http://localhost:8000/admin/ to access the admin interface

### Legacy ERP Synchronization

To sync data from the legacy 4D ERP system:

1. Configure legacy ERP connection settings in `.env` file:

```
LEGACY_API_HOST=your-legacy-erp-host
LEGACY_API_PORT=8080
LEGACY_API_USERNAME=your-username
LEGACY_API_PASSWORD=your-password
```

2. Run synchronization commands:

```bash
# Sync products
python manage.py sync_products --full

# Sync customers
python manage.py sync_customers --full

# Other sync commands...
```

## Documentation

- Project documentation is available in the `docs/` directory
- API documentation can be accessed at `/api/docs/` when the server is running
- Vue.js frontend documentation:
  - README files in the `frontend/` directory
  - Component documentation in the `frontend/src/components/` directory

### Module Documentation

- [Product Module Implementation Progress](docs/implementation/product_module_progress.md) - Details of the product module implementation including parent-variant models and image integration
- [Product Model Split](docs/product_model_split.md) - Documentation of the migration from a single Product model to separate ParentProduct and VariantProduct models

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific tests
pytest pyerp/products/tests/

# Run with coverage report
pytest --cov=pyerp --cov-report=xml
```

Code coverage reports are automatically generated by Codecov during CI runs. You can view the latest coverage report at [codecov.io/gh/your-organization/pyERP](https://codecov.io/gh/your-organization/pyERP).

Our CI pipeline ensures that:
- All tests pass before deployment
- Code coverage meets minimum thresholds (currently 80%)
- Coverage reports are uploaded to Codecov for visualization and tracking

## Continuous Integration

The project uses GitHub Actions for continuous integration with the following workflow jobs:

- **Lint**: Runs code quality checks including:
  - Flake8 for Python syntax and style validation
  - MyPy for static type checking
  
- **Tests**: Runs the test suite with pytest to validate functionality
  - Runs unit and integration tests
  - Uploads test coverage results to Codecov
  - Enforces minimum code coverage thresholds (80%)

- **Build**: Builds the Docker image for deployment
  - Creates a containerized version of the application
  - Pushes to GitHub Container Registry with appropriate tags
  
- **Deploy**: Deploys to appropriate environments based on branch/tag:
  - `develop` branch → Development environment
  - `release/*` branches → Staging environment
  - Tags (`v*`) → Production environment
  - Requires successful tests before deployment

- **Additional Workflows**:
  - **Dependency Security Scan**: Runs weekly to check for security vulnerabilities
  - **Update Dependencies**: Runs weekly to update dependencies and create pull requests with updates

Branch protection rules ensure:
- Pull request reviews are required for merges to `main` and `develop`
- CI checks must pass before merging
- Force pushes are not allowed to protected branches

CI/CD workflows can be found in the `.github/workflows` directory.

## Deployment

The project uses a CI/CD pipeline to automate testing, building, and deployment processes.

### Environments

- **Development**: Automatically deployed from the `dev` branch
- **Staging**: Deployed from `release/*` branches
- **Production**: Deployed when:
  - A version tag (`v*`) is pushed
  - The `dev` branch is merged into the `prod` branch

### Deployment Process

The CI/CD pipeline follows these steps:
1. Run linting and tests
2. Build Docker image
3. Push image to GitHub Container Registry
4. Deploy to the appropriate environment

### Server Setup

The project includes an automated server setup script that prepares a server for deployment:

```bash
# Basic usage (uses default values)
sudo ./scripts/setup_deployment_server.sh

# Custom configuration
sudo ./scripts/setup_deployment_server.sh <app_user> <app_path> <env_file>
```

The script requires GitHub credentials in the specified environment file:

```
# GitHub credentials for container registry (required)
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-github-personal-access-token
```

The script intelligently uses all available environment variables from your source .env file, with sensible defaults for any missing values. It automatically:

- Uses existing configuration values when available
- Generates secure random values for sensitive fields
- Detects server hostname and IP addresses
- Includes any custom environment variables

See the [CI/CD documentation](.github/README.md) for more details on the deployment process and server setup.

## Project Structure

```
pyERP/
├── .github/                  # GitHub Actions workflows for CI/CD
├── config/                   # Configuration files
│   └── env/                  # Environment configuration files
├── docker/                   # Docker configurations
├── docs/                     # Documentation
├── logs/                     # Log files
├── pyerp/                    # Main Django project
│   ├── config/               # Django settings
│   ├── core/                 # Core functionality
│   ├── legacy_sync/          # Legacy ERP integration
│   ├── products/             # Product management app
│   │   ├── management/       # Management commands
│   │   │   └── commands/     # Custom Django commands
│   │   │       └── sync_product_images.py  # Product image sync command
│   │   ├── models/           # Product-related models
│   │   │   └── product_image.py  # ProductImage and ImageSyncLog models
│   │   └── image_api.py      # External image API client
│   ├── sales/                # Sales management app
│   ├── inventory/            # Inventory management app
│   ├── production/           # Production management app
│   ├── scripts/              # Python scripts for various tasks
│   └── users/                # User management app
├── scripts/                  # Utility scripts
│   ├── docker/               # Docker-related scripts
│   ├── tools/                # Development tools
│   ├── db_migrations/        # Database migration scripts
│   └── utilities/            # Utility scripts
├── static/                   # Static files
├── media/                    # User-uploaded media
├── tests/                    # Top-level tests
│   └── coverage/             # Test coverage reports
├── manage.py                 # Django management script
└── requirements/             # Python dependencies
```

## Data Validation Framework

pyERP includes a robust data validation framework designed to enforce data integrity across the application:

- **Core Validation**: The `pyerp/core/validators.py` module provides a flexible, extensible validation system
- **Multiple Validation Levels**:
  - Model-level validation (using Django's clean method)
  - Form-level validation (with custom Django form integrations)
  - Import-level validation (for data importing from legacy systems or files)
- **Validation Features**:
  - Field-specific validators (required fields, regex patterns, numeric ranges, etc.)
  - Cross-field validation (business rules that span multiple fields)
  - Compound validators (combine multiple validation rules)
  - Warning vs. Error distinction (flexibility in validation strictness)
  - Data transformation during validation

### Using Validation

**Model Validation Example**:
```python
from pyerp.core.validators import validate_model_data

def clean(self):
    # Apply validators to model instance
    validate_model_data(self)
    super().clean()
```

**Form Validation Example**:
```python
from pyerp.core.form_validation import ValidatedForm
from pyerp.core.validators import RequiredValidator, RegexValidator

class ProductForm(ValidatedForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_validator('sku', RegexValidator(pattern=r'^[A-Z0-9-]+$'))
```

**Import Validation Example**:
```python
from pyerp.core.validators import ImportValidator

validator = ProductImportValidator(strict=False)
for row in data:
    is_valid, validated_data, result = validator.validate_row(row)
    if is_valid:
        # Process valid data
        create_product(validated_data)
    else:
        # Handle validation errors
        log_errors(result.errors)
```

For detailed documentation on the validation framework, see [Validation Framework Guide](docs/validation_framework.md).

## Product Image Integration

pyERP includes a comprehensive product image integration feature:

- **API Integration**: ✅ Implemented
  - Connects to an external image database API to retrieve product images
  - Supports authentication and pagination
  - Includes caching for performance optimization
  - Robust error handling and fallback logic

- **Image Prioritization**: ✅ Implemented
  - Smart prioritization of images based on type and "front" flag
  - Format preference system (PNG > JPEG > original format)
  - Resolution-appropriate image selection
  - Parent-variant aware image selection

- **Synchronization**: ✅ Implemented
  - Management command for initial and incremental sync
  - Detailed logging of sync operations
  - Status tracking with ImageSyncLog model

- **Parent-Variant Aware**: ✅ Implemented
  - Smart article number selection based on product hierarchy
  - Variant products use parent's images for consistency
  - Comprehensive fallback strategy for maximum image coverage

- **Frontend Integration**: ✅ Partially Implemented
  - Product list and detail views display appropriate images
  - Responsive image galleries
  - Thumbnail support

For detailed documentation on the product image integration feature, see:
- [Product Module Implementation Progress](docs/implementation/product_module_progress.md)
- [Product Image Integration Story](docs/images_api/product_image_integration_story.md)
- [Product Model Split](docs/product_model_split.md)

## Security and Audit Logging

pyERP includes a comprehensive security system with audit logging capabilities:

### Features

- **Centralized Audit Logging**: Records critical security events in a dedicated `AuditLog` model
- **Automatic Event Tracking**: Captures authentication events (login, logout, failed attempts)
- **User Activity Monitoring**: Logs user creation, updates, and permission changes
- **Contextual Data Recording**: Stores IP addresses, user agent information, and timestamps
- **Administrative Review**: Searchable and filterable admin interface for security review
- **Non-repudiation**: Immutable logs that cannot be modified through the interface
- **Extensible Design**: Easy to add custom event types and specialized logging

### Event Types

The system logs various event types including:
- Authentication events (login, logout, failed logins)
- User management activities
- Permission changes
- Critical data access and modifications
- System security events

### Integration

The audit logging system integrates with Django's authentication framework and signals system, providing automatic capture of key security events without requiring explicit logging calls in views.

### Usage

Developers can easily add audit logging to security-sensitive operations:

```python
from pyerp.core.services import AuditService

# Log data access event
AuditService.log_data_access(
    user=request.user,
    obj=sensitive_record,
    request=request,
    action="exported customer data"
)
```

For detailed documentation on security features and audit logging, see:
- [docs/security/audit_logging.md](docs/security/audit_logging.md)

## Dependency Management

The project uses pip-tools for dependency management. Dependencies are organized into three categories:

- **Base Dependencies** (`requirements/base.in`): Core dependencies used in all environments
- **Production Dependencies** (`requirements/production.in`): Dependencies needed specifically for production
- **Development Dependencies** (`requirements/development.in`): Additional dependencies needed for development and testing

### Adding or Updating Dependencies

1. Add the dependency to the appropriate `.in` file
2. Compile the requirements using pip-compile
3. Install the updated dependencies

For detailed instructions, see [Dependency Management Guide](docs/dependency_management.md).

### Known Issues

Some dependencies like `psycopg2-binary` require system-level libraries. See [Dependency Updates](docs/dependency_updates.md) for known issues and solutions.

## License

[Your License Information]

## Contributors

[Your Team Information]

## Type Checking with Mypy

This project uses [mypy](https://mypy.readthedocs.io/) for static type checking. To ensure proper type checking:

1. Install the required type stubs:
   ```bash
   pip install -r requirements-types.txt
   ```
   
   Or run the provided script:
   ```bash
   ./scripts/tools/install_type_stubs.sh
   ```

2. Run mypy with the provided configuration:
   ```bash
   ./scripts/tools/run_mypy.sh
   ```
   
   Or manually:
   ```bash
   mypy --config-file scripts/tools/mypy.ini .
   ```

### Handling Missing Type Stubs

For third-party libraries without type stubs, we use the following approaches:
- Install type stubs when available (e.g., `pandas-stubs`, `types-polib`)
- Configure mypy to ignore missing imports for specific modules in `mypy.ini`
- Add inline `# type: ignore` comments for specific import statements when necessary

For the `wsz_api` module, which is a custom module without type stubs, we've configured mypy to ignore missing imports.

## Vue.js Integration

The project now includes a Vue.js 3.5 frontend integration. The Vue.js application is located in the `frontend/` directory and is integrated with Django.

### Setup

1. Install Node.js dependencies:

```bash
cd frontend
npm install
```

2. Run the Vue.js development server:

```bash
cd frontend
npm run dev
```

3. Access the Vue.js application at `/vue/` in your Django application.

### Development

The Vue.js application is set up with the following features:

- Vue.js 3.5 with Composition API
- TypeScript for type safety
- Vite for fast development and builds
- ESLint and Prettier for code quality
- Hot Module Replacement for rapid development
- JWT-based authentication with automatic token refresh
- Protected routes with navigation guards
- Centralized state management with Pinia

The development workflow allows for:

- Real-time updates using the Vite dev server
- Integration with Django templates
- API calls to Django endpoints
- Secure authentication with the Django backend

### Authentication

The Vue.js frontend implements a comprehensive authentication system that integrates with Django's authentication backend:

- **JWT-based Authentication**: Secure token-based authentication
- **User Management**: Login, logout, profile management, and password changes
- **Protected Routes**: Navigation guards for authenticated routes
- **Role-based Access**: Different access levels for admin and regular users
- **Automatic Token Refresh**: Seamless user experience with token refresh
- **Centralized State**: Authentication state managed with Pinia

For detailed documentation, see [Authentication Implementation](docs/vue_auth_implementation.md).

### Building for Production

To build the Vue.js application for production:

```bash
cd frontend
npm run build
```

This will generate optimized assets in the `static/vue/` directory, which Django will serve in production mode. 