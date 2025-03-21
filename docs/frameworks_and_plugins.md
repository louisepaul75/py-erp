# pyERP Frameworks and Plugins Documentation

## Backend Frameworks and Libraries

### Core Django
- Django 5.1.6 - Main web framework
- Django REST Framework 3.15.2 - API framework
- Django Filter 23.5 - Query filtering for APIs
- Django CORS Headers 4.3.1 - Cross-origin request handling

### Database
- PostgreSQL (via psycopg2-binary 2.9.9)
- Sqlite3 (Development/testing/fallback db)
- DJ Database URL 2.1.0 - Database URL configuration

### Authentication
- Django Allauth 0.61.1 - Authentication, registration, account management
- DRF SimpleJWT 5.3.1 - JWT authentication for API

### Internationalization
- Django's built-in i18n - Translation system with gettext for backend
- Django LocaleMiddleware - Language detection via URL prefixes (/de/, /en/)
- i18n_patterns - URL-based language switching
- Supported languages: German (primary) and English (secondary)
- Django ModelsTranslation - Alternative for database content translation (planned)

### Real-time Communication
- Django Channels 4.0.0 - WebSockets support
- Channels Redis 4.1.0 - Redis channel layer backend for Channels

### Background Processing
- Celery 5.4.0 - Asynchronous task queue
- Redis 5.0.2 - Message broker, caching, and WebSocket backing store
- Django Redis 5.4.0 - Redis integration for Django
- Django Celery Results 2.5.1 - Store Celery results
- Django Celery Beat 2.7.0 - Periodic tasks

### API Documentation
- DRF YASG 1.21.9 - Swagger documentation

### File Storage
- Django Storages 1.14.2 - File storage backends
- Boto3 1.33.13 - AWS SDK for Python

### Document Generation
- WeasyPrint 60.2 - HTML to PDF converter
- ReportLab 4.1.0 - PDF generation library

### Utilities
- Pillow 10.2.0 - Image processing
- Pydantic 2.6.3 - Data validation
- Pandas 2.2.0 - Data analysis
- Tabulate 0.9.0 - Pretty-print tabular data


### Logging
- StructLog 24.1.0 - Structured logging
- Python JSON Logger 3.2.1 - JSON logging format

### Security
- 1Password Connect SDK - Secrets management

### Deployment
- Gunicorn 21.2.0 - WSGI HTTP server
- Whitenoise 6.9.0 - Static file serving
- Ddtrace 2.0.0 - Datadog APM and tracing

## Frontend Frameworks and Libraries

### React Frontend
- React 18.3.1 - UI library
- Next.js 14.2.24 - React framework
- TypeScript 5.3.3 - Type-safe JavaScript
- Recharts 2.x - React Charts


### State Management
- React Query (TanStack Query) 5.69.0 - Server state management and data fetching
- React Context API - UI state management for components
- React useState - Local component state management

### Internationalization
- react-i18next 14.1.0 - React UI translation framework with useTranslation hook
- i18next 23.10.1 - Core i18n system
- i18next-browser-languagedetector 7.2.0 - Language detection from browser settings
- i18next-http-backend 2.5.0 - Loads translation files from server
- Support for translation namespaces and TypeScript integration

### UI Components
- shadcn/ui - Component library built on Radix UI and Tailwind CSS
- Radix UI - Headless UI components:
  - Dialog, Dropdown Menu, Separator, Slot, Tabs, Tooltip
- Lucide React 0.344.0 - Icon library
- Tailwind CSS 3.4.17 - Utility-first CSS framework
- Tailwind Merge 2.6.0 - Merge Tailwind CSS classes
- Tailwind Animate 1.0.7 - Animations for Tailwind
- Class Variance Authority 0.7.1 - Component variants

### Data Fetching
- Tanstack React Query 5.69.0 - Data fetching and caching
- Ky 1.7.5 - HTTP client
- JWT Decode 4.0.0 - JWT parsing

## Development Tools

### Code Quality
- Black 24.2.0 - Python code formatter
- Flake8 7.0.0 - Python linter
- isort 5.13.2 - Import sorter
- Mypy 1.8.0 - Static type checker
- Ruff 0.2.1 - Fast Python linter

### Testing
- Pytest 8.0.2 - Testing framework
- Pytest Django 4.8.0 - Django testing integration
- Pytest Cov 4.1.0 - Coverage reporting
- mutmut 3.x - test Mutation
- Factory Boy 3.3.0 - Test fixtures
- Faker 22.5.1 - Fake data generation
- Jest 6.x - React Testing
- Jest-junit 16.x - Jest coverage report
- stryker 8.x - Jest Mutation

### Documentation
- Sphinx 7.3.7 - Documentation generator
- Sphinx RTD Theme 2.0.0 - ReadTheDocs theme

### Development Utilities
- Django Debug Toolbar 4.3.0 - Debugging panel
- Django Extensions 3.2.3 - Additional commands
- Django Browser Reload 1.12.1 - Auto browser reload
- Watchdog 4.0.0 - File system monitoring

## DevOps and Deployment

### Docker
- Docker Compose - Multi-container Docker applications
- Nginx - Web server and reverse proxy
- Supervisord - Process control system

### Monitoring
- Datadog - Performance monitoring
- Elasticsearch - Log storage and search
- Kibana - Log visualization
- Filebeat - Log shipping

## Third-Party Integrations
- Email via Django Anymail 10.2
- AWS S3 for storage

## Version Control
- Git
- GitHub Actions for CI/CD (based on .github directory)
- Pre-commit hooks (via .pre-commit-config.yaml) 