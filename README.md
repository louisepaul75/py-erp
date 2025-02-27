# pyERP

A modern Django-based ERP system designed to replace a legacy 4D-based ERP, focusing on manufacturing operations with both B2B and B2C sales channels.

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

## Getting Started

### Prerequisites

- Python 3.13.2
- PostgreSQL 13+
- Docker and Docker Compose (for development environment)

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

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific tests
pytest pyerp/products/tests/

# Run with coverage report
pytest --cov=pyerp
```

## Continuous Integration

The project uses GitHub Actions for continuous integration with the following workflows:

- **Test and Lint**: Runs on every push to main/master and pull requests to verify code quality
- **Dependency Security Scan**: Runs weekly to check for security vulnerabilities
- **Update Dependencies**: Runs weekly to update dependencies and create pull requests with updates
- **Build Docker Image**: Builds and publishes Docker images on merges to main/master and tags

CI/CD workflows can be found in the `.github/workflows` directory.

## Deployment

For production deployment:

1. Set up a production-ready database (PostgreSQL)
2. Configure environment variables
3. Use Gunicorn as WSGI server
4. Set up Nginx as reverse proxy
5. Configure static files serving

See detailed deployment instructions in `docs/deployment.md`

## Project Structure

```
pyERP/
├── .github/                  # GitHub Actions workflows for CI/CD
├── docker/                   # Docker configurations
├── docs/                     # Documentation
├── pyerp/                    # Main Django project
│   ├── config/               # Django settings
│   ├── core/                 # Core functionality
│   ├── legacy_sync/          # Legacy ERP integration
│   ├── products/             # Product management app
│   ├── sales/                # Sales management app
│   ├── inventory/            # Inventory management app
│   ├── production/           # Production management app
│   └── users/                # User management app
├── static/                   # Static files
├── media/                    # User-uploaded media
├── tests/                    # Top-level tests
├── .env.example              # Example environment variables
├── manage.py                 # Django management script
└── requirements/             # Python dependencies
```

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