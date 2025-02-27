# User Stories

## Phase 0: Foundation

### Epic: Legacy ERP Data Integration

**Context:**  
To facilitate a smooth transition from the legacy 4D-based ERP to our new Django-based system, we need to build robust utilities for data extraction, analysis, and synchronization. This will enable module-by-module development while maintaining data integrity between systems.

#### Story 1: Set Up Development Environment ✅
**As a** Developer  
**I want to** set up a standardized development environment  
**So that** all team members can work consistently on the project

**Acceptance Criteria:**
- Docker Compose configuration for local development ✅
- PostgreSQL database setup with initial schema ✅
- Django project structure with core configurations ✅
- Development, testing, and production settings separation ✅
- Environment-specific configurations that persist across Git operations ✅
- Consistent code formatting and linting setup ✅
- Dependency management with version pinning ✅
- README with detailed setup instructions ✅

**Tasks:**
- Create project directory structure ✅
- Configure Django settings for development, testing, and production environments ✅
- Set up Docker Compose with PostgreSQL, Redis, and Django ✅
- Create initial requirements files with pinned dependencies ✅
- Configure logging and debugging tools ✅
- Implement environment detection mechanism ✅
- Set up pre-commit hooks for code quality ✅
- Configure linting and formatting tools (flake8, black, isort) ✅
- Document setup process in README ✅

#### Story 2: Project Structure Organization ✅
**As a** Developer  
**I want to** establish a well-organized project structure  
**So that** the codebase is maintainable and follows best practices

**Acceptance Criteria:**
- Clear separation of Django apps by business domain ✅
- Properly organized settings module with environment-specific configurations ✅
- Consistent code organization patterns within apps ✅
- Shared utilities and base components in core module ✅
- Documentation about project structure and organization patterns ✅
- Consistent import conventions across the project ✅
- Proper management of static files and templates ✅

**Tasks:**
- Create top-level project structure ✅
- Set up settings module with base, development, testing, and production configuration ✅
- Create core Django app for shared functionality ✅
- Set up template structure with inheritance patterns ✅
- Establish static files organization ✅
- Create module structure for business domain apps ✅
- Document naming conventions and organization patterns ✅
- Set up URL routing structure with proper namespacing ✅
- Create base templates and style guide ✅

#### Story 3: Database Environment Configuration ✅
**As a** Developer  
**I want to** set up separate database environments for development and production  
**So that** development work doesn't affect production data and settings persist across Git operations

**Acceptance Criteria:**
- Separate MySQL databases for testing and production ✅
- Environment-specific Django settings that automatically select the correct database ✅
- Development environments always connect to testing database (pyerp_testing) ✅
- Production environments always connect to live database (pyerp_production) ✅
- Connection settings persist across Git operations (pulls, merges, etc.) ✅
- Environment variables for database credentials ✅
- Documentation for database setup and connection ✅

**Tasks:**
- Create development/testing MySQL database (pyerp_testing) ✅
- Create production MySQL database (pyerp_production) ✅
- Configure Django settings for environment-specific database connections ✅
- Implement environment detection for automatic database selection ✅
- Set up .env file templates for environment variables ✅
- Add .env files to .gitignore to prevent credentials from being committed ✅
- Create database initialization scripts for fresh installations ✅
- Document database configuration in project wiki/documentation ✅
- Install necessary MySQL client libraries (mysqlclient) ✅

#### Story 3.1: MySQL Database Migration ✅
**As a** Developer  
**I want to** migrate the database configuration from PostgreSQL to MySQL  
**So that** the system can use MySQL for all environments

**Acceptance Criteria:**
- Django settings updated to use MySQL database engine ✅
- MySQL client libraries installed and configured ✅
- Development and production settings updated with MySQL-specific configurations ✅
- Database connection verified in all environments ✅
- Migration commands tested and working ✅

**Tasks:**
- Install MySQL client library (mysqlclient) ✅
- Update development.py with MySQL database configuration ✅
- Update production.py with MySQL database configuration ✅
- Update testing.py with MySQL database configuration ✅
- Test database connectivity with python manage.py check ✅
- Verify migration status with python manage.py showmigrations ✅
- Update documentation to reflect MySQL usage ✅
- Update PRD to replace PostgreSQL references with MySQL ✅

#### Story 3.2: Secure Database Credential Management ✅
**As a** Developer  
**I want to** implement secure handling of database credentials  
**So that** sensitive information is not exposed in code or documentation

**Acceptance Criteria:**
- All database credentials removed from settings files and stored in environment variables ✅
- Development and production credentials kept separate ✅
- Use of DATABASE_URL format for simplified configuration ✅
- Example templates provided with placeholders instead of actual credentials ✅
- Documentation updated to not include actual credentials ✅
- .env files excluded from version control ✅

**Tasks:**
- Remove hardcoded credentials from all Django settings files ✅
- Update settings to read credentials from environment variables ✅
- Create example .env templates with placeholders ✅
- Update the PRD to document credential management strategy without exposing actual credentials ✅
- Ensure .env files are in .gitignore ✅
- Refactor relevant code to use dj-database-url package for connection handling ✅

#### Story 4: Legacy ERP API Client
**As a** Developer  
**I want to** create an API client for the legacy 4D ERP  
**So that** I can extract data from the existing system

**Acceptance Criteria:**
- Ability to connect to the legacy 4D ERP API
- Authentication mechanism for secure data access
- Methods to query and retrieve data from specific tables
- Error handling and retry mechanisms
- Configuration for connection parameters

**Tasks:**
- Research 4D API access methods
- Implement connection module with authentication
- Create data retrieval functions for common operations
- Add logging and error handling
- Write tests for API client functionality

#### Story 5: Legacy Database Schema Analysis
**As a** Developer  
**I want to** analyze and document the legacy ERP database structure  
**So that** I can design an appropriate schema for the new system

**Acceptance Criteria:**
- Documentation of all relevant tables and their relationships
- Field mappings between legacy and new system
- Identification of data quality issues and normalization needs
- ERD (Entity Relationship Diagram) of legacy system
- Recommended data structure for new system

**Tasks:**
- Extract database schema from legacy system
- Document table structures and relationships
- Identify primary/foreign keys and constraints
- Analyze data quality and consistency
- Create mapping document for field transformations

#### Story 6: Core Models Definition
**As a** Developer  
**I want to** define the core Django models for the new ERP  
**So that** I can begin storing and processing data

**Acceptance Criteria:**
- Base models for primary entities (Products, Customers, Orders, etc.)
- Migration files for initial database setup
- Legacy ID fields for mapping to original system
- Admin interface for data inspection
- Tests for model validation and relationships

**Tasks:**
- Define Django models with appropriate fields
- Add validation rules and constraints
- Create migrations for database schema
- Set up Django admin for data inspection
- Write unit tests for model functionality

#### Story 7: Data Synchronization Framework
**As a** Developer  
**I want to** create a framework for one-way data synchronization  
**So that** data can be imported from legacy to new system incrementally

**Acceptance Criteria:**
- Configurable mapping between legacy and new data models
- Scheduled and manual synchronization options
- Transformation pipeline for data cleansing
- Conflict resolution strategies
- Detailed logging of sync operations
- Validation tools to verify data integrity

**Tasks:**
- Design synchronization architecture
- Implement mapper for field transformations
- Create scheduler for automatic sync
- Add validation and conflict resolution
- Implement transaction handling for data integrity
- Create admin interface for manual sync operations

#### Story 8: Product Module Synchronization
**As a** Business User  
**I want to** synchronize product data from the legacy system  
**So that** I can begin using the product management features of the new ERP

**Acceptance Criteria:**
- All product data correctly imported from legacy system
- Categories, attributes, and pricing information preserved
- BOM relationships maintained
- Product images and attachments migrated
- UI for viewing and managing products
- Validation report showing data integrity

**Tasks:**
- Create product data extractor for legacy system
- Implement transformations for product data
- Build product models in new system
- Add sync job for products
- Create validation reports
- Build basic product management UI

#### Story 9: Comprehensive Testing Framework
**As a** Developer  
**I want to** implement a comprehensive testing framework  
**So that** we can ensure code quality, prevent regressions, and facilitate continuous integration

**Acceptance Criteria:**
- Multi-level testing strategy (unit, integration, and end-to-end tests)
- Automated test execution in development and CI environments ✅ *Implemented*
- Test fixtures and factories for consistent test data generation
- Mocking framework for external dependencies
- Code coverage reporting with minimum threshold requirements
- Performance testing tools for critical workflows
- Documentation for writing and running tests
- Clear test organization patterns matching the project structure

**Tasks:**
- Set up pytest configuration with appropriate plugins
- Create base test classes for common testing patterns
- Implement factory_boy factories for model test data
- Configure mocking framework for external services
- Set up Selenium/Playwright for E2E testing
- Integrate coverage reporting with CI pipeline ✅ *Implemented*
- Implement performance testing for critical paths
- Create test documentation and examples
- Set up pre-commit hooks for running tests on changed code ✅ *Implemented*
- Configure CI pipeline for test execution ✅ *Implemented*

#### Story 10: Structured Logging System (Partially Complete)
**As a** Developer  
**I want to** implement a comprehensive logging system with LLM-friendly log files  
**So that** we can effectively monitor, debug, and analyze system behavior

**Acceptance Criteria:**
- Structured log format (JSON) for better parsing and analysis ✅
- Configurable log levels for different environments (DEBUG, INFO, WARNING, ERROR, CRITICAL) ✅
- Log rotation to keep individual file sizes below 2MB for LLM processing ✅
- Categorized logs (application, security, performance, user activity, data sync) ✅
- Centralized log collection for multi-container deployment
- Human and machine-readable log formats ✅
- Context-enriched log entries (request ID, user, timestamp, environment) ✅
- Log retention policies and archiving mechanism
- Searchable logs with appropriate indexing
- Performance monitoring for log generation overhead

**Tasks:**
- Configure Django's logging framework with appropriate handlers and formatters ✅
- Implement log rotation with size-based triggers (2MB max file size) ✅
- Create custom log formatters for structured JSON output ✅
- Set up environment-specific logging configurations ✅
- Implement middleware for request/response logging ✅
- Create utility functions for standardized logging across the application ✅
- Configure log storage and archiving mechanism
- Implement security event logging framework
- Set up performance monitoring for critical operations
- Create documentation for logging standards and practices ✅
- Implement log analysis utilities for common debugging tasks

## Next Steps
After completing the foundation phase, we will prioritize business modules based on:
1. Business criticality
2. Complexity
3. Dependencies between modules

Our implementation sequence will be:

1. **Project Structure & Environment Setup** ✅
   - Establish project organization and architecture ✅
   - Set up Docker-based development environment ✅
   - Configure code quality tools and CI pipeline ✅
   - Establish development workflow and practices ✅

2. **Environment & Database Setup** ✅
   - Set up consistent development and production MySQL database environments ✅
   - Ensure environment-specific settings persist across Git operations ✅
   - Create database initialization and migration scripts ✅
   - Configure proper MySQL database connections and client libraries ✅

3. **Legacy System Integration** (In Progress)
   - Implement API client for legacy 4D ERP
   - Analyze legacy database schema
   - Create data mapping and transformation components

4. **Core Functionality** (Partially Complete)
   - Implement user authentication and permissions
   - Create base models and shared utilities ✅
   - Build admin interfaces for key functionality

5. **Business Modules** (Not Started)
   - Start with Products module (including BOM)
   - Proceed to Sales Management
   - Follow with Inventory Management
   - Finally implement Production Management

Each module will be developed with a test-driven approach, ensuring proper test coverage before moving to the next module.

# User Stories for PyERP

This document outlines the key user stories for the PyERP system. Each story represents a specific user need or feature requirement.

## Product Management

### US-PM-001: Import Products from Legacy System

**As a** Product Manager  
**I want to** import products from the legacy 4D system  
**So that** I can migrate our product catalog to the new ERP system without manual data entry

**Acceptance Criteria:**
- ✅ Products are imported from Artikel_Variante table (replacing previous Artikel_Stamm approach)
- ✅ Base SKUs and variant codes are correctly extracted from composite SKUs
- ✅ Parent products are automatically created for product variants sharing the same base SKU
- ✅ Product pricing is correctly imported from complex nested price structures
- ✅ Import supports dry-run mode for testing without making database changes
- ✅ Import provides detailed logs and error reporting
- ✅ Import can be limited to a specific number of products for testing
- ⬜ Product categories are imported based on Familie_ field
- ⬜ Additional product attributes are imported (dimensions, descriptions, tags)
- ⬜ Product import includes validation and data quality checks
- ⬜ Image and media assets are imported

**Implementation Notes:**
- Implementation based on Django management command
- See detailed progress in [Product Import from Artikel_Variante](./stories/product_import_artikel_variante.md)
- Command: `python manage.py import_products [options]`

**Status:** In Progress 