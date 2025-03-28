# pyERP Frameworks and Plugins Documentation

## Backend Frameworks and Libraries

### Core Django
- Django 5.x - Main web framework
- Django REST Framework 3.x - API framework
- Django Filter 23.x - Query filtering for APIs
- Django CORS Headers 4.x - Cross-origin request handling

### Database
- PostgreSQL (via psycopg2-binary 2.x)
- Sqlite3 (Development/testing/fallback db)
- DJ Database URL 2.x - Database URL configuration

### Authentication
- Django Allauth 65.x - Authentication, registration, account management
- DRF SimpleJWT 5.x - JWT authentication for API

### Internationalization
- Django's built-in i18n - Translation system with gettext for backend
- Django LocaleMiddleware - Language detection via URL prefixes (/de/, /en/)
- i18n_patterns - URL-based language switching
- Supported languages: German (primary) and English (secondary)
- Django ModelsTranslation - Alternative for database content translation (planned)

### Real-time Communication
- Django Channels 4.x - WebSockets support
- Channels Redis 4.x - Redis channel layer backend for Channels

### Background Processing
- Celery 5.x - Asynchronous task queue
- Redis 5.x - Message broker, caching, and WebSocket backing store
- Django Redis 5.x - Redis integration for Django
- Django Celery Results 2.x - Store Celery results
- Django Celery Beat 2.x - Periodic tasks

### API Documentation
- DRF YASG 1.x - Swagger documentation

### File Storage
- Django Storages 1.x - File storage backends
- Boto3 1.x - AWS SDK for Python

### Document Generation
- WeasyPrint 65.x - HTML to PDF converter
- ReportLab 4.x - PDF generation library

### Utilities
- Pillow 11.x - Image processing
- Pydantic 2.x - Data validation
- Pandas 2.x - Data analysis
- Tabulate 0.x - Pretty-print tabular data

### Logging
- StructLog 25.x - Structured logging
- Python JSON Logger 3.x - JSON logging format

### Security
- 1Password Connect SDK 1.x - Secrets management

### Deployment
- Gunicorn 23.x - WSGI HTTP server
- Whitenoise 6.x - Static file serving
- Ddtrace 3.x - Datadog APM and tracing

## Frontend Frameworks and Libraries

### React Frontend
- React 19.x - UI library
- Next.js 15.x - React framework
- TypeScript 5.x - Type-safe JavaScript
- Recharts 2.x - React Charts

### State Management
- React Query (TanStack Query) 5.x - Server state management and data fetching
- React Context API - UI state management for components
- React useState - Local component state management

### Internationalization
- react-i18next 14.x - React UI translation framework with useTranslation hook
- i18next 23.x - Core i18n system
- i18next-browser-languagedetector 7.x - Language detection from browser settings
- i18next-http-backend 2.x - Loads translation files from server
- Support for translation namespaces and TypeScript integration

### UI Components
- shadcn/ui - Component library built on Radix UI and Tailwind CSS
- Radix UI - Headless UI components:
  - Dialog, Dropdown Menu, Separator, Slot, Tabs, Tooltip
- Lucide React 0.x - Icon library
- Tailwind CSS 3.x - Utility-first CSS framework
- Tailwind Merge 2.x - Merge Tailwind CSS classes
- Tailwind Animate 1.x - Animations for Tailwind
- Class Variance Authority 0.x - Component variants

### Data Fetching
- Tanstack React Query 5.x - Data fetching and caching
- Ky 1.x - HTTP client
- JWT Decode 4.x - JWT parsing

## Development Tools

### Code Quality
- Black 25.x - Python code formatter
- Flake8 7.x - Python linter
- isort 6.x - Import sorter
- Mypy 1.x - Static type checker
- Ruff 0.x - Fast Python linter

### Testing
- Pytest 8.x - Testing framework
- Pytest Django 4.x - Django testing integration
- Pytest Cov 6.x - Coverage reporting
- mutmut 3.x - test Mutation
- hypothesis 6.x - pytest Property-Based & Randomized Testing
- Factory Boy 3.x - Test fixtures
- Faker 37.x - Fake data generation
- Jest 6.x - React Testing
- Jest-junit 16.x - Jest coverage report
- Jest-fuzz - Jest Property-Based & Randomized Testing
- stryker 8.x - Jest Mutation

### Documentation
- Sphinx 8.x - Documentation generator
- Sphinx RTD Theme 3.x - ReadTheDocs theme

### Development Utilities
- Django Debug Toolbar 5.x - Debugging panel
- Django Extensions 3.x - Additional commands
- Django Browser Reload 1.x - Auto browser reload
- Watchdog 6.x - File system monitoring

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
- Email via Django Anymail 12.x
- AWS S3 for storage

## Version Control
- Git
- GitHub Actions for CI/CD (based on .github directory)
- Pre-commit hooks (via .pre-commit-config.yaml) 