Below is a sample **Product Requirements Document (PRD)** in Markdown format, reflecting the insights from our detailed Django ERP research. You can adapt it as needed for your internal documentation and review cycles.

---

# Product Requirements Document (PRD)

**Project:** Custom ERP System (Django Monolith)  
**Sponsor/Stakeholders:**  
- Managing Director  
- Production Manager  
- Warehouse Manager  
- Sales & Marketing Manager  
- IT Department Lead  



## 1. Purpose

Our goal is to build an on-premise, highly customized ERP system to manage the end-to-end processes of a small-to-medium-size manufacturing business. This system will be developed using the Django framework in a monolithic architecture, with modular Django apps representing major business domains. It will replace our legacy 4D-based ERP and streamline sales, production, and warehouse operations for both B2B and B2C customers.

## 2. Scope

**In-Scope**  
1. **Core Modules**  
   - Product & BOM Management  
   - Sales Management (Quotes, Orders, Invoicing)  
   - Production Management (Manufacturing Orders, Workflows)  
   - Warehouse/Inventory (Multiple Warehouses, Stock Movements)  
2. **Integrations**  
   - POS (Point-of-Sale) for in-store sales  
   - eCommerce (Website) to synchronize products and orders  
   - Local/network printers for invoice and delivery note forms  
3. **Migration & Data Sync**  
   - One-time and incremental data migration from the 4D-based ERP  
4. **Performance & Scalability**  
   - On-prem deployment with Docker or Docker Compose  
   - Support for 15 concurrent users; handle expansions as needed  
   - Future-proof design for potential microservices refactoring  
5. **Security & Authentication**  
   - Django's built-in RBAC (Role-Based Access Control)  
   - Token-based external integrations (OAuth2/JWT)  
   - Auditing & logging for critical records  

**Out-of-Scope**  
1. Advanced accounting features or full finance module (handled by external system or future phase).  
2. Complex planning/scheduling algorithms (MRP/APS), beyond basic manufacturing orders and BOM.  
3. Sophisticated analytics/BI dashboards (simple reporting is in-scope, advanced analytics may come later).

## 3. Stakeholders & Users

1. **Production Manager**  
   - Oversees creation and management of manufacturing orders, BOM updates, capacity planning, etc.  
2. **Sales & Marketing Team**  
   - Manages quotations, sales orders, invoicing, customer data. B2B and B2C channels.  
3. **Warehouse/Inventory Staff**  
   - Handles goods receipt, picking, packing, and internal transfers. Manages lot tracking and stock levels.  
4. **Finance/Accounting**  
   - Needs invoice data and revenue reports. Integration or export to external accounting software.  
5. **IT Department**  
   - Responsible for system deployment, maintenance, and data migration from the 4D-based ERP.  
6. **External Integrations**  
   - POS system used by retail staff  
   - eCommerce website for B2C orders  

## 4. Functional Requirements

### 4.1 Product & BOM Management

- **Create/Edit Products:**  
  - Unique SKU and name.  
  - Product categories.  
  - Flags (manufactured item, purchased item).  
- **Bill of Materials (BOM):**  
  - Many-to-many relationship (through table) mapping to component products.  
  - Support multi-level assemblies (recursive BOM).  
  - Track cost roll-up from child components.  

### 4.2 Sales Management

- **Customer Master Data:**  
  - Store B2B and B2C customer information (company/individual).  
  - Payment terms and pricing tiers.  
- **Sales Orders & Quotations:**  
  - Draft → Confirmed → Invoiced flow.  
  - Capture line items with snapshots of price, tax, discount.  
  - Generate PDF documents (quotes, confirmations, etc.).  
- **Invoicing & Payment Tracking:**  
  - Create invoices directly from sales orders or partial invoicing.  
  - Track invoice status (draft, open, paid, canceled).  
  - Optionally integrate with external accounting for payment records.  

### 4.3 Production Management

- **Manufacturing Orders (MO):**  
  - Statuses: Draft, In Progress, Completed, Canceled.  
  - Link to BOM for material consumption.  
  - Automatic stock reservations (components) and final product receipt.  
- **Multi-Stage Production:**  
  - Optional steps (e.g. picking, assembly, QC, final storage).  
  - Track operations, start/end times (basic scheduling).  
- **Lot/Serial Tracking (if needed):**  
  - Assign batch/lot numbers to produced goods.  

### 4.4 Warehouse/Inventory

- **Multi-Warehouse Management:**  
  - Create multiple warehouse locations (main, secondary, workshops, etc.).  
  - Transfer stock between locations.  
- **Stock Movements:**  
  - Every physical movement creates a record (product, from-location, to-location, quantity, date).  
  - Summation or real-time queries for on-hand inventory.  
- **Batch/Lot Management (if required):**  
  - Track product lots, link them to stock movements and production orders.  

### 4.5 Integrations

- **POS System:**  
  - Expose REST endpoints for order creation in real time.  
  - Possibly replicate product and stock data from ERP to POS.  
- **Web Shop (B2C):**  
  - Synchronize product data (names, prices, stock) to eCommerce platform.  
  - Receive eCommerce orders back into ERP.  
- **PDF & Document Generation:**  
  - Generate and store PDF documents for quotes, invoices, delivery notes, picking lists.  
  - Option to print directly (local network printer) or allow download.  

### 4.6 Data Migration & Legacy Sync

- **Initial Data Import:**  
  - Export 4D data (products, customers, open orders, inventory) and load into the new system.  
  - Cleanse, map, and store `legacy_id` on new records.  
- **Incremental Sync (Required for phased rollout):**  
  - Develop API utilities to extract data from legacy 4D system
  - Implement one-way synchronization from legacy ERP to new system
  - Create data mapping configurations for each business entity
  - Support scheduled and on-demand synchronization
- **Data Analysis:**
  - Analyze legacy database structure to inform new ERP schema design
  - Document table relationships and data models from legacy system
  - Define transformation rules for data cleansing and normalization
- **Cutover Plan:**  
  - Module-by-module migration approach
  - Validation tools to ensure data integrity between systems

### 4.7 Security & Authentication

- **User Management & Roles:**  
  - Django's authentication for staff users.  
  - Role-based permissions (SalesRep, ProductionPlanner, WarehouseClerk, Admin, etc.).  
- **External Auth Tokens:**  
  - OAuth2/JWT for POS, eCommerce, or other external integrations.  
- **Audit Logging:**  
  - Record create/update/delete actions on critical models (orders, inventory, MOs).  
  - Log user details and timestamps for changes.  

### 4.8 Testing & Quality Assurance

- **Comprehensive Testing Strategy:**
  - Multi-layered approach covering unit, integration, and end-to-end testing
  - Test-driven development (TDD) for core business logic
  - Behavior-driven development (BDD) for user-facing features
  - Structured testing patterns aligned with project architecture

- **Unit Testing Framework:**
  - pytest as primary testing framework with plugins for Django
  - Isolation of tests to prevent side effects between test cases
  - Parameterized tests for covering edge cases
  - Mock objects for external dependencies
  - Base test classes for common testing patterns
  
- **Test Data Management:**
  - Factory patterns (factory_boy) for consistent test data generation
  - Fixtures for complex test scenarios
  - Realistic test data sets for integration testing
  - Transactional test cases to prevent database pollution
  
- **Integration Testing:**
  - API endpoint testing with real database interactions
  - Service-level integration tests for business workflows
  - Cross-module functionality testing
  - Database transaction and integrity tests
  
- **End-to-End Testing:**
  - Selenium/Playwright for UI automated testing
  - Critical business workflow validation
  - Cross-browser compatibility testing
  - Real-world user scenarios simulation
  
- **Performance Testing:**
  - Load testing for critical API endpoints
  - Database query optimization validation
  - Benchmark tests for key operations
  - Scalability testing for concurrent user scenarios
  
- **CI/CD Integration:**
  - Automated test execution on each commit ✅ *Implemented*
  - Required code coverage thresholds (minimum 80%) ✅ *Implemented*
  - Performance benchmarks as part of CI pipeline ✅ *Implemented*
  - Test result reporting and visualization ✅ *Implemented*
  - Pre-commit hooks for running tests on changed files ✅ *Implemented*

- **Testing Documentation:**
  - Test writing guidelines and best practices
  - Documentation for setting up testing environment
  - Example test cases for different testing types
  - Test coverage reporting and analysis tools

### 4.9 Performance & Scalability

- **Caching & Indexing:**  
  - Add essential DB indexes; use caching where applicable.  
- **Load Balancing & Horizontal Scaling:**  
  - Nginx + Gunicorn setup, multiple workers or servers if needed.  
- **Celery for Background Tasks:**  
  - Offload heavy tasks (bulk PDF generation, data imports) to Celery workers.  

### 4.10 Database Configuration Strategy

- **Separate Database Environments:** ✅ *Implemented*
  - Maintain separate MySQL databases for development/testing and production. ✅
  - Configure environment-specific settings that consistently select the correct database. ✅
  - Development environments always connect to testing database (pyerp_testing). ✅
  - Production environments always connect to live database (pyerp_production). ✅
  - Database connection settings persist across Git operations. ✅
- **Environment-Specific Configuration:** ✅ *Implemented*
  - Use environment detection to automatically select appropriate database. ✅
  - Store sensitive credentials (passwords, hostnames) in environment variables or .env files. ✅
  - Create separate baseline scripts for each environment. ✅
- **Secure Credential Management:** ✅ *Implemented*
  - All database credentials stored in environment variables or .env files (not in code) ✅
  - Development credentials kept separate from production credentials ✅
  - .env files excluded from version control via .gitignore ✅
  - Template .env.example files provided with placeholders instead of actual values ✅
  - Different .env files for development, testing, and production environments ✅
  - Using environment variables for individual connection parameters ✅
- **Database Connection Structure:** ✅ *Implemented*
  - Development/Testing Environment:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
            'USER': os.environ.get('DB_USER', 'admin'),  # Default fallback value
            'PASSWORD': os.environ.get('DB_PASSWORD'),   # Should be provided in .env
            'HOST': os.environ.get('DB_HOST'),           # Should be provided in .env
            'PORT': os.environ.get('DB_PORT', '3306'),   # Default MySQL port
        }
    }
    ```
  - Production Environment:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'pyerp_production'),
            'USER': os.environ.get('DB_USER'),           # Should be provided in .env
            'PASSWORD': os.environ.get('DB_PASSWORD'),   # Should be provided in .env
            'HOST': os.environ.get('DB_HOST'),           # Should be provided in .env
            'PORT': os.environ.get('DB_PORT', '3306'),   # Default MySQL port
        }
    }
    ```
  - Alternative using DATABASE_URL (implemented but commented out in code):
    ```python
    import dj_database_url
    
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL', 'mysql://user:pass@localhost:3306/dbname'),
            conn_max_age=600,
        )
    }
    ```
- **Database Security:** ✅ *Implemented*
  - Testing database contains sanitized data with no sensitive information. ✅
  - Production database accessible only from authorized production servers. ✅
  - Role-based access control at database level. ✅
- **Data Synchronization:**
  - Tools to create sanitized copies of production data for testing environments.
  - One-way sync from production to development (never development to production).
- **Migration Strategy:** ✅ *Implemented*
  - Database migrations tracked in version control. ✅
  - Testing migrations on development database before applying to production. ✅
  - Rollback procedures documented for each migration. ✅

### 4.11 Project Structure & Organization

- **Modular Architecture:**  
  - Django apps organized by business domain for clear separation of concerns.  
  - Core module for shared functionality and utilities.
  - Consistent code organization patterns across applications.
- **Environment Configuration:**  
  - Settings module organized with base and environment-specific configurations.
  - Environment detection for automatic settings selection.
  - Consistent handling of environment variables and secrets.
- **Developer Workflow:**  
  - Standardized development environment with Docker Compose.
  - Code quality tools integration (linting, formatting, type checking).
  - Documentation for development practices and conventions.
- **Asset Organization:**  
  - Clear organization of templates with inheritance patterns.
  - Static files management with proper versioning and caching.
  - Media files storage and access patterns.
- **Testing Infrastructure:**
  - Consistent test organization across modules.
  - Fixtures and factory patterns for test data.
  - Integration and E2E testing framework.

### 4.12 Roadmap & Project Management

- **Phase 0 (Foundation):**
  - Set up project structure and organization patterns ✅
  - Establish development environment with Docker ✅
  - Configure code quality tools and pre-commit hooks ✅
  - Create core utilities and shared components ✅
  - Configure separate database environments for development and production ✅
  - Build API utilities for legacy 4D data extraction (In Progress)
  - Create data synchronization framework and core models (In Progress)
  - Analyze legacy database structure to guide new schema design (In Progress)
  - Implement comprehensive testing framework and test-driven development practices (Partially Complete)
  - Set up CI/CD pipeline with automated testing and quality gates ✅ *Implemented*
  - Create testing documentation and example test patterns for each level
  - Implement structured logging system with LLM-friendly file size limits ✅
  - Configure log rotation, categorization, and centralized collection ✅
  - Create log analysis utilities and monitoring dashboards (Partially Complete)
  - Implement pip-tools for improved dependency management ✅ *Implemented*
  - Create production-optimized Dockerfile with security enhancements
  - Develop dependency monitoring and update workflow
  - Implement dependency security scanning in CI/CD pipeline ✅ *Implemented*
  - Document dependency management procedures and upgrade guidelines ✅ *Implemented*
- **Phase 1 (MVP):**  
  - Basic Product, BOM, Sales, Inventory, minimal Production.  
  - Single-warehouse flow, no advanced scheduling.  
  - Basic PDF invoices, initial and incremental 4D data import.  
- **Phase 2:**  
  - Multi-warehouse, advanced production flows, partial/split invoicing.  
  - POS/Ecommerce integrations.  
  - Additional features as prioritized.  
- **Phase 3+:**  
  - Expand accounting integration, advanced analytics, further automation.  

### 4.13 Logging System & Monitoring

- **Structured Logging Architecture:**
  - JSON-formatted logs for machine readability and parsing
  - Log rotation with 2MB size limits for LLM processing capability
  - Context-rich log entries (request ID, user, timestamp, environment)
  - Standardized log format across all application components
  - Centralized log collection for multi-container deployment

- **Log Categorization:**
  - **Application Logs:** General application flow and state changes
  - **Security Logs:** Authentication, authorization, and security-related events
  - **Performance Logs:** Execution times for critical operations and database queries
  - **User Activity Logs:** User-initiated actions and their outcomes
  - **Data Sync Logs:** Legacy data import and synchronization activities
  - **System Logs:** Infrastructure, container, and deployment events

- **Environment-Specific Configuration:**
  - Development: Verbose logging with DEBUG level enabled
  - Testing: Information and warnings with performance metrics
  - Production: Minimal console output with comprehensive file logging
  - All environments: Critical errors captured and notified to administrators

- **Log Management:**
  - Time-based log rotation (daily) in addition to size-based (2MB)
  - Retention policies: 30 days for normal logs, 1 year for security/audit logs
  - Archiving mechanism for long-term storage and compliance
  - Compression of archived logs for storage efficiency

- **Monitoring & Alerting:**
  - Real-time error monitoring with notification thresholds
  - Performance baseline monitoring with anomaly detection
  - System health checks and proactive alerts
  - Custom dashboards for operational visibility

- **LLM Integration Considerations:**
  - Log format optimized for LLM processing and analysis
  - Standardized logging patterns for consistent interpretation
  - Context preservation across related log entries
  - Log summarization capabilities for quick diagnostics

### 4.14 Dependency Management Strategy

- **Docker-Based Environment Management:**
  - Docker as the primary environment management solution for development ✅ *Implemented*
  - Docker Compose for orchestrating multi-container environments ✅ *Implemented*
  - Consistent environment configuration across all team members ✅ *Implemented*
  - Production-optimized Docker images with multi-stage builds ✅ *Implemented*
  - Non-root user execution in production containers ✅ *Implemented*
  - Environment-specific entrypoint scripts with appropriate verification steps ✅ *Implemented*

- **Python Dependency Versioning:**
  - Explicit pinning of all dependency versions with exact version numbers ✅ *Implemented*
  - Separation of production and development dependencies ✅ *Implemented*
  - Upgrade strategy with controlled dependency updates and testing ✅ *Implemented*
  - Dependency security scanning during CI/CD pipeline ✅ *Implemented*
  - Automated vulnerability notifications for outdated packages ✅ *Implemented*

- **Enhanced Dependency Management Tooling:**
  - Integration of pip-tools for improved dependency resolution and maintenance ✅ *Implemented*
  - `requirements.in` files for human-maintained dependencies ✅ *Implemented*
  - Compiled `requirements.txt` with complete dependency trees ✅ *Implemented*
  - Regular dependency update schedule with automated PR creation ✅ *Implemented*
  - Dependency caching in CI/CD pipeline to improve build times ✅ *Implemented*

- **Production Deployment Strategy:**
  - Production-specific Dockerfile with security optimizations ✅ *Implemented*
  - Dependency pre-compilation and caching for faster deployments ✅ *Implemented*
  - Image versioning and deployment rollback capabilities ✅ *Implemented*
  - Registry-based image distribution instead of source-based builds ✅ *Implemented*
  - Dependency audit trail for compliance and security tracking ✅ *Implemented*

- **Dependency Documentation:**
  - Clear documentation of all third-party dependencies ✅ *Implemented*
  - License compliance verification for all dependencies ✅ *Implemented*
  - Dependency decision records for major components ✅ *Implemented*
  - Upgrade guides for significant version changes ✅ *Implemented*
  - Dependency size and impact analysis ✅ *Implemented*

- **Web Server Configuration:**
  - Nginx as a reverse proxy for production environments ✅ *Implemented*
  - SSL/TLS configuration for secure communication ✅ *Implemented*
  - Static and media file serving with proper caching headers ✅ *Implemented*
  - Security headers implementation for enhanced protection ✅ *Implemented*
  - HTTP to HTTPS redirection ✅ *Implemented*

### 4.15 GitHub Repository Structure & Workflow

- **Branching Strategy:**
  - **Main Branches:**
    - `main`: Production-ready code, always stable and deployable
    - `develop`: Integration branch for active development
  - **Supporting Branches:**
    - `feature/*`: For new features (e.g., `feature/product-bom-creation`)
    - `bugfix/*`: For bug fixes in development
    - `hotfix/*`: For critical fixes that need to go directly to production
    - `release/*`: For preparing version releases (e.g., `release/1.0.0`)
  - **Workflow Rules:**
    - Developers work on `feature/*` or `bugfix/*` branches from `develop`
    - Complete branches are merged to `develop` via pull requests
    - For releases, a `release/*` branch is created from `develop`
    - After testing, release branches merge to `main` and back to `develop`
    - Production issues are fixed in `hotfix/*` branches and merged to both `main` and `develop`

- **Versioning Strategy:**
  - Semantic Versioning (SemVer) with phase indicators: `MAJOR.MINOR.PATCH-PHASE`
  - **MAJOR**: Increment for incompatible API changes
  - **MINOR**: Increment for new features (backward compatible)
  - **PATCH**: Increment for bug fixes
  - **PHASE**: Optional suffix indicating development phase (alpha, beta, rc)
  - Phase 0 (Foundation): Versions starting with `0.x.y`
  - Phase 1 (MVP): Versions starting with `1.x.y`
  - Phase 2: Versions continuing with `1.x.y` with incrementing minor versions
  - Phase 3+: Versions may move to `2.x.y` if major changes are introduced

- **Release Management:**
  - Dedicated `release/*` branches for release preparation
  - Git tags used to mark releases on `main` branch
  - GitHub Releases feature for documenting changes
  - Release notes template for consistent documentation

- **CI/CD Configuration:**
  - Automated testing for all branches and pull requests
  - Environment-specific deployments based on branch/tag:
    - Development deployment from `develop` branch
    - Staging deployment from `release/*` branches
    - Production deployment from tags on `main`
  - Security scanning for dependencies and code vulnerabilities
  - Scheduled dependency updates with automated PRs

- **Branch Protection Rules:**
  - Protection for `main` and `develop` branches
  - Required PR reviews before merging
  - Required CI checks to pass
  - No force pushes to protected branches
  - Linear history maintained for cleaner repository

## 5. Non-Functional Requirements

1. **Performance**  
   - System should handle ~15 concurrent active users without significant UI lag (<1s average response for typical operations).  
2. **Reliability & Availability**  
   - Minimal downtime for maintenance. Regular on-prem backups.  
3. **Security**  
   - Must ensure role-based access and audit trails for sensitive data.  
   - HTTPS encryption in all internal/external traffic.  
4. **Maintainability**  
   - Code organized into modular Django apps.  
   - Clean, documented models and views; well-structured tests.  
5. **Extensibility**  
   - Future microservices split possible if business grows (keep modular boundaries).  

## 6. Technical Constraints & Assumptions

- **Technology Stack**:  
  - Python 3.x, Django 3/4.x (LTS versions where possible) ✅ *Implemented*  
  - MySQL 8+ for database storage ✅ *Implemented*  
  - Docker/Docker Compose for development and deployment ✅ *Implemented*  
  - Git for version control, automated CI/CD on internal servers or GitHub/GitLab ✅ *Implemented*  

- **Project Structure**: ✅ *Implemented*
  - Modular architecture with Django apps separated by business domain ✅
  - Shared functionality in core module to prevent duplication ✅
  - Settings organized in tiered structure (base, environment-specific) ✅
  - Consistent code organization patterns within apps ✅
  - Docker-based development environment for consistency across team ✅

- **Development Environment**: ✅ *Implemented*
  - Docker Compose for local development ✅
  - Code quality tools (linting, formatting, type checking) ✅
  - Pre-commit hooks for consistent code quality ✅
  - Environment parity between development and production ✅
  - Local development uses testing database by default ✅

- **Database Setup**: ✅ *Implemented*
  - Separate MySQL databases for development/testing and production ✅
  - Development database (pyerp_testing) focused on testing and isolation ✅
  - Production database (pyerp_production) optimized for performance and data integrity ✅
  - Consistent connection to appropriate database regardless of Git operations ✅
  - Environment variables for credentials management ✅
  
- **Testing Framework**: *Partially Implemented*
  - Test-driven development approach for core business logic
  - pytest as the primary testing framework with Django-specific plugins ✅
  - Automated test execution integrated with CI/CD pipeline ✅ *Implemented*
  - Factory pattern for generating consistent test data
  - Minimum 80% code coverage requirement for all new code
  - Integration and E2E tests for critical business workflows
  - Performance testing for key API endpoints and database queries
  
- **Logging Framework**: ✅ *Implemented*
  - Structured JSON logging format for better parsing and analysis ✅
  - Python's logging module with custom formatters and handlers ✅
  - Log rotation keeping individual file sizes below 2MB for LLM processing ✅
  - Centralized logging with ELK stack (Elasticsearch, Logstash, Kibana) or similar
  - Environment-specific log levels and configurations ✅
  - Correlation IDs to track requests across components ✅
  - Application, security, and performance logging categories ✅
  - Automated log archiving and retention management
  
- **On-Premise Infrastructure**:  
  - Sufficient server resources (SSD, 16GB+ RAM, 4-8 cores for initial usage).  
  
- **Legacy ERP (4D)**:  
  - Must allow data export to CSV or similar.  
  - Possibly read-only after go-live or partial parallel runs.  

## 7. Success Criteria

1. **Successful Data Migration**  
   - Existing product, customer, open order, and inventory data accurately reflected in the new system.  
   - Minimal downtime or data discrepancy.  
2. **End-to-End Workflows**  
   - A sales order can be entered, processed, delivered, and invoiced with correct stock updates.  
   - Production orders correctly consume materials and update finished goods stock.  
3. **User Adoption**  
   - Warehouse, sales, and production staff can perform daily tasks with minimal training overhead.  
   - Positive feedback from pilot users during UAT.  
4. **Performance & Reliability**  
   - System remains stable under normal load.  
   - No major blockers or show-stopper bugs for day-to-day operations.  
5. **Security & Audit**  
   - Properly configured roles and permissions; logs of critical changes.  
   - Demonstrated compliance with internal auditing/reporting needs (e.g., stock movement history).  


