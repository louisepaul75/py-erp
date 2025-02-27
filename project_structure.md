# Proposed Project Structure for pyERP

```
pyERP/
│
├── .github/                      # GitHub workflows and CI/CD configuration
│   └── workflows/                # GitHub Actions workflow files
│       ├── test.yml              # Testing and linting workflow
│       ├── dependency-scan.yml   # Security scanning workflow
│       ├── update-dependencies.yml # Dependency update workflow
│       └── docker-build.yml      # Docker build workflow
│
├── docker/                       # Docker configurations
│   ├── development/
│   ├── production/
│   └── docker-compose.yml
│
├── docs/                         # Project documentation
│   ├── api/                      # API documentation
│   ├── legacy_erp/               # Legacy ERP analysis docs
│   │   ├── schema/               # Schema documentation
│   │   └── api/                  # API documentation
│   └── user_guides/              # End-user documentation
│
├── pyerp/                        # Main Django project directory
│   ├── config/                   # Django settings module
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── testing.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── core/                     # Core functionality shared across apps
│   │   ├── management/
│   │   │   └── commands/         # Custom management commands
│   │   ├── migrations/
│   │   ├── models.py             # Base models, abstract models
│   │   ├── utils.py              # Utility functions
│   │   └── tests/
│   │
│   ├── legacy_sync/              # Legacy ERP sync functionality
│   │   ├── api/                  # Legacy ERP API client
│   │   │   ├── client.py         # API connection client
│   │   │   └── endpoints.py      # API endpoint definitions
│   │   ├── management/
│   │   │   └── commands/         # Sync commands
│   │   ├── migrations/
│   │   ├── models.py             # Sync tracking models
│   │   ├── services/             # Sync services
│   │   │   ├── mappers/          # Data mapping classes
│   │   │   └── transformers/     # Data transformation classes
│   │   ├── tasks.py              # Celery tasks for sync
│   │   └── tests/
│   │
│   ├── products/                 # Product management app
│   │   ├── admin.py
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   └── tests/
│   │
│   ├── sales/                    # Sales management app
│   │   ├── admin.py
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   └── tests/
│   │
│   ├── inventory/                # Inventory management app
│   │   ├── admin.py
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   └── tests/
│   │
│   ├── production/               # Production management app
│   │   ├── admin.py
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   └── tests/
│   │
│   ├── users/                    # User management app
│   │   ├── admin.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   └── tests/
│   │
│   └── templates/                # HTML templates
│
├── static/                       # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                        # User-uploaded media
│
├── tests/                        # Top-level test directory
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
│
├── .env.example                  # Example environment variables
├── .gitignore
├── manage.py
├── README.md
├── requirements/
│   ├── base.txt                  # Base requirements
│   ├── development.txt           # Development requirements
│   └── production.txt            # Production requirements
└── setup.py                      # Package setup for potential reusable apps
```

## Key Components

### Legacy Sync Module

The `legacy_sync` app is the central component for this first phase, responsible for:

1. **API Client**: Connects to the 4D legacy ERP and retrieves data
2. **Data Mapping**: Transforms legacy data to fit the new schema
3. **Synchronization Services**: Orchestrates the sync process
4. **Admin Interface**: Allows monitoring and manual triggering of sync jobs
5. **Celery Tasks**: Schedules regular sync jobs

### Core Module

The `core` app provides:

1. **Base Models**: Abstract models with common fields like timestamps, audit fields
2. **Utilities**: Shared functionality across apps
3. **Middleware**: Application-wide middleware

### Business Domain Apps

Each business domain (products, sales, inventory, etc.) follows a similar structure:

1. **Models**: Django ORM models for the domain
2. **Admin**: Django admin customization
3. **API**: REST endpoints for the domain
4. **Services**: Business logic and domain services
5. **Tests**: Unit and integration tests for the domain

## Next Steps

1. Set up the initial project structure
2. Create the legacy_sync app with API client functionality
3. Implement core models to support data synchronization
4. Begin analyzing legacy ERP schema
5. Implement the product domain as the first business module 