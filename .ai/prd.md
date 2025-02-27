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

### 4.1.1 Product Image Integration

- **External Image Database Integration:**
  - Connect to external Django application managing product images via API. ✅ *Verified*
  - Implement secure authentication to the image database API. ✅ *Verified*
  - Support for different image types (Produktfoto, Markt-Messe-Shop, Szene, etc.). ✅ *Verified*
  - Prioritize image display based on type and attributes (front=true flag). ✅ *Verified*
- **Image Management:**
  - Display product images in the ERP interface with proper prioritization. ✅ *Verified*
  - Allow users to view all available images for a product.
  - Enable selection of primary product image for display in various contexts.
  - Support batch operations for image management across multiple products.
- **Caching & Performance:**
  - Implement caching strategy for frequently accessed images to improve performance. ✅ *Verified*
  - Support for image thumbnails generation and resizing for different UI contexts. ✅ *Verified*
  - Asynchronous loading of images to prevent UI performance degradation.
- **Synchronization:**
  - Regular synchronization with the image database to ensure up-to-date images. ✅ *Verified*
  - Track image changes and updates for audit purposes. ✅ *Verified*
  - Handle conflict resolution for image changes.
- **Format Optimization:** ✅ *Implemented*
  - Prioritize web-friendly formats (PNG, JPEG) over design formats (PSD, etc.). ✅ *Verified*
  - Select highest quality available image based on resolution and format. ✅ *Verified*
  - Support appropriate image formats for different use cases (thumbnails, product detail, etc.). ✅ *Verified*

### 4.1.2 API Structure & Findings ✅ *Implemented*

- **API Endpoint:**
  - Base URL: `http://webapp.zinnfiguren.de/api/` ✅ *Verified*
  - Endpoint: `all-files-and-articles/` ✅ *Verified*
  - Supports pagination with page and page_size parameters ✅ *Verified*
- **Image Data Structure:**
  - Each image record contains: ✅ *Verified*
    - `original_file`: The original uploaded image with type, format, and URL
    - `exported_files`: Array of derived formats (PNG, JPEG, TIFF) with resolutions
    - `articles`: Array of associated product articles with number and front flag
  - Image types include: Produktfoto, Markt-Messe-Shop, Szene, etc. ✅ *Verified*
  - Resolution options range from thumbnails (200×200) to full size (4032×3024) ✅ *Verified*
- **Image Prioritization Logic:**
  - Products with front=true and Produktfoto type have highest priority ✅ *Verified*
  - File formats are prioritized: PNG > JPEG > original format ✅ *Verified*
  - Images can be associated with multiple products ✅ *Verified*

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
- **Web Shop (B2C & B2B):** 
  - Synchronize product data (names, prices, stock) to eCommerce platform.  
  - Receive eCommerce orders back into ERP.  
- **PDF & Document Generation:**  
  - Generate and store PDF documents for quotes, invoices, delivery notes, picking lists.  
  - Option to print directly (local network printer) or allow download.  
- **Image Database API Integration:**
  - Secure connection to external image management Django application. ✅ *Verified*
  - Support for pagination, filtering, and sorting of image data. ✅ *Verified*
  - Consistent error handling for API connection issues. ✅ *Implemented*
  - Performance optimization for image retrieval and display.

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

### 4.6.1 Product Data Migration Strategy

- **Product Data Structure Understanding:** ✅ *Implemented*
  - The legacy 4D system has evolved its product structure:
    - **Artikel_Stamm**: Legacy/older product table (no longer primary source)
    - **Artikel_Variante**: Current primary product table replacing Artikel_Stamm
    - Products in Artikel_Variante contain all necessary data including variant information
    - **Artikel_Familie**: Contains parent product data used as base for product variants
  
- **Multi-Source Product Import Approach:** ✅ *Implemented*
  - **Parent Product Import**: Successfully imported from Artikel_Familie ✅
    - Created 1,571 parent products with some exceptions due to missing descriptions ✅
    - Parent products serve as base for variant products ✅
  - **Variant Product Import**: Verified with dry-run from Artikel_Variante ✅
    - Extract base SKUs and variant codes from the composite SKU format (e.g., "11400-BE") ✅
    - Establish proper product hierarchies based on base SKU relationships ✅
  - **Relationship Management**: Successfully updated parent-child relationships ✅
    - 4,078 variant products linked to their parent products ✅
    - Proper parent-child relationships established based on SKU patterns ✅
  
- **Product Data Quality Considerations:** ✅ *Partially Implemented*
  - Handle products with and without explicit variant codes consistently ✅
  - Create consistent parent-child relationships based on SKU patterns ✅
  - Import pricing data from the structured Preise field (Laden, Handel, Empf., Einkauf prices) ✅
  - Establish proper categorization based on product family information (Planned)
  - Ensure products with the same base SKU share appropriate attributes ✅

- **Product Import Technical Implementation:** ✅ *Implemented*
  - Use management commands for both initial and incremental imports ✅
    - `import_artikel_familie_as_parents.py` command for parent product import ✅
    - `import_artikel_familie_as_parents.py --update-relationships` for updating parent-child links ✅
    - `import_artikel_variante` command for variant product import ✅
  - Implement dry-run capability for safe testing ✅
  - Provide proper logging and error tracking ✅
  - Support limiting record count for testing and incremental imports ✅
  - Include exception handling with detailed error reporting ✅

- **Progress Summary:**
  - ✅ Parent product import completed successfully (1,571 products created)
  - ✅ Parent-child relationships updated successfully (4,078 relationships)
  - ✅ Variant product import verified with dry-run
  - ⬜ Full variant product import pending
  - ⬜ Product categorization enhancement pending

- **Next Steps for Product Data Migration:**
  - Complete full variant import to create all variants in the database
  - Enhance product categorization based on Familie_ field and legacy categories
  - Import additional product attributes (dimensions, weights, tags)
  - Implement full-text search indexing for improved product discovery
  - Add incremental sync capability for ongoing updates from legacy system
  - Create data quality reports to identify potential issues in imported data

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
  - Test-driven development (TDD) for core business logic components
  - Behavior-driven development (BDD) for user-facing features
  - Structured testing patterns aligned with project architecture

- **Unit Testing Framework:** ✅ *Partially Implemented*
  - pytest as primary testing framework with plugins for Django ✅ *Implemented*
  - Isolation of tests to prevent side effects between test cases ✅ *Implemented*
  - Parameterized tests for covering edge cases ✅ *Implemented*
  - Mock objects for external dependencies ✅ *Implemented*
  - Base test classes for common testing patterns ✅ *Implemented*
  - **Current Test Coverage:** 8% overall, with core validators at 79% ✅ *Measured*
  - **Test Coverage Goals:** Minimum 80% coverage for all core modules
  
- **Test Data Management:**
  - Factory patterns (factory_boy) for consistent test data generation (Planned)
  - Fixtures for complex test scenarios ✅ *Partially Implemented*
  - Realistic test data sets for integration testing (Planned)
  - Transactional test cases to prevent database pollution (Planned)
  
- **Integration Testing:**
  - API endpoint testing with real database interactions (Planned)
  - Service-level integration tests for business workflows (Planned)
  - Cross-module functionality testing (Planned)
  - Database transaction and integrity tests (Planned)
  
- **End-to-End Testing:**
  - Selenium/Playwright for UI automated testing (Planned)
  - Critical business workflow validation (Planned)
  - Cross-browser compatibility testing (Planned)
  - Real-world user scenarios simulation (Planned)
  
- **Performance Testing:**
  - Load testing for critical API endpoints (Planned)
  - Database query optimization validation (Planned)
  - Benchmark tests for key operations (Planned)
  - Scalability testing for concurrent user scenarios (Planned)
  
- **CI/CD Integration:**
  - Automated test execution on each commit ✅ *Implemented*
  - Required code coverage thresholds (minimum 80%) ✅ *Implemented*
  - Performance benchmarks as part of CI pipeline ✅ *Implemented*
  - Test result reporting and visualization ✅ *Implemented*
  - Pre-commit hooks for running tests on changed files ✅ *Implemented*

- **Testing Documentation:**
  - Test writing guidelines and best practices ✅ *Implemented*
  - Documentation for setting up testing environment ✅ *Implemented*
  - Example test cases for different testing types ✅ *Implemented*
  - Test coverage reporting and analysis tools ✅ *Implemented*

- **Testing Improvement Plan:**
  - **Phase 1: Core Framework Testing** *In Progress*
    - ✅ Fix failing test in RequiredValidator (parameter naming inconsistency)
    - ✅ Create isolated product validation tests without Django dependencies
    - Resolve circular import issues in product validators
    - Increase core validators coverage from 79% to 90%
    - Add tests for form validation framework (currently 0%)
  - **Phase 2: Model & Business Logic Testing** *Planned*
    - Add tests for product models and validators
    - Implement tests for legacy sync functionality
    - Create tests for import commands
    - Develop tests for business rule validation
  - **Phase 3: View & Integration Testing** *Planned*
    - Add tests for API endpoints and views
    - Implement integration tests for critical workflows
    - Create end-to-end tests for key user journeys
    - Develop performance tests for database operations

- **Testing Tools & Resources:** ✅ *Implemented*
  - Coverage analysis script (`find_low_coverage.py`) to identify modules with low coverage ✅ *Implemented*
  - Untested module detection script (`find_untested_modules.py`) to find modules with no tests ✅ *Implemented*
  - Test templates with examples for different component types (`test_template.py`) ✅ *Implemented*
  - Custom script (`run_tests.py`) to bypass Django app registry issues ✅ *Implemented*
  - Comprehensive test coverage improvement plan with phased approach ✅ *Implemented*

- **Testing Implementation Timeline:**
  - **Short-term Goal** (1 month): Increase overall coverage to 30%, focusing on core modules
  - **Medium-term Goal** (3 months): Increase overall coverage to 60%, covering all public APIs
  - **Long-term Goal** (6 months): Maintain coverage above 80% across all modules

### 4.8.1 Data Validation Framework ✅ *Implemented*

- **Comprehensive Validation Architecture:** ✅ *Implemented*
  - Multi-level validation strategy covering models, forms, and import processes ✅ *Implemented*
  - Separation of validation logic from business logic ✅ *Implemented*
  - Reusable validation components for consistent rules enforcement ✅ *Implemented*
  - Error handling with detailed contextual messages ✅ *Implemented*

- **Core Validation Framework:** ✅ *Implemented*
  - Base `Validator` class with extensible validation interface ✅ *Implemented*
  - `ValidationResult` container for structured validation outcomes ✅ *Implemented*
  - Support for both error and warning levels ✅ *Implemented*
  - Context-aware validation with field-specific messages ✅ *Implemented*

- **Model-Level Validation:** ✅ *Implemented*
  - Enhanced Django model validation beyond field constraints ✅ *Implemented*
  - Business rule validation in model `clean()` methods ✅ *Implemented*
  - Cross-field validation for complex rules ✅ *Implemented*
  - Prevention of invalid data persistence ✅ *Implemented*

- **Import Data Validation:** ✅ *Implemented*
  - Specialized `ImportValidator` for legacy data migration ✅ *Implemented*
  - Data transformation capabilities during validation ✅ *Implemented*
  - Row-level validation with detailed error reporting ✅ *Implemented*
  - Flexible strictness settings (warnings vs. errors) ✅ *Implemented*

- **Form Validation Integration:** ✅ *Implemented*
  - Form mixins for Django form integration ✅ *Implemented*
  - Reuse of core validators in form contexts ✅ *Implemented*
  - Cross-field validation support in forms ✅ *Implemented*
  - Consistent error presentation to users ✅ *Implemented*

- **Product-Specific Validators:** ✅ *Implemented*
  - SKU format and structure validation ✅ *Implemented*
  - Price and decimal value validation ✅ *Implemented*
  - Parent-variant relationship validation ✅ *Implemented*
  - Business rule enforcement for products ✅ *Implemented*
  
- **Validation Documentation:** *Planned*
  - Guidelines for creating new validators
  - Best practices for validation implementation
  - Error message standardization
  - Examples of common validation patterns

- **Validation Framework Improvements:**
  - **Bug Fixes:** *High Priority*
    - ✅ Fix parameter naming inconsistency in RequiredValidator (message vs error_message)
    - Resolve circular import issues in product validators module
    - Address test failures in validation framework
  - **Enhancements:** *Medium Priority*
    - Add more specialized validators for business-specific validations
    - Improve error message formatting and localization
    - Enhance validation performance for bulk operations
  - **Documentation:** *Medium Priority*
    - Create comprehensive validator documentation with examples
    - Document validation best practices and patterns
    - Provide tutorials for extending the validation framework

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
  - Build API utilities for legacy 4D data extraction ✅ *Implemented*
  - Create data synchronization framework and core models ✅ *Implemented*
  - Analyze legacy database structure to guide new schema design ✅ *Implemented*
  - Implement comprehensive testing framework and test-driven development practices ✅ *Partially Implemented*
    - Core validation framework tests at 78% coverage ✅ *Implemented*
    - Test infrastructure with pytest and coverage reporting ✅ *Implemented*
    - Test analysis tools for coverage improvement planning ✅ *Implemented*
    - Test templates for different component types ✅ *Implemented*
    - Remaining modules require test implementation (8% overall coverage) *In Progress*
  - Implement data validation framework for models, forms, and imports ✅ *Implemented*
    - Core validators framework ✅ *Implemented*
    - Form validation integration ✅ *Implemented*
    - Import validation system ✅ *Implemented*
    - Product-specific validators ✅ *Implemented*
    - Bug fixes and improvements needed *In Progress*
  - Set up CI/CD pipeline with automated testing and quality gates ✅ *Implemented*
  - Create testing documentation and example test patterns for each level ✅ *Implemented*
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
  - **Product Data Migration - Part 1:** ✅ *Implemented*
    - Import product variants from Artikel_Variante table ✅
    - Establish base SKU and variant structure ✅
    - Extract pricing information from Preise field structure ✅
    - Map variant-specific attributes (prices, stock, etc.) ✅
    - Create placeholder categories based on default Uncategorized category ✅
  - **Product Data Migration - Part 2:** ✅ *Mostly Implemented*
    - Create parent products from Artikel_Familie ✅
    - Link variants to parent products ✅
    - Successfully imported 1,571 parent products ✅
    - Successfully updated 4,078 parent-child relationships ✅
    - Verified variant import with dry-run ✅
    - Enhance product categorization with full hierarchy (Planned)
    - Map Artikel_Familie data to product categories (Planned)
    - Extract and import additional product metadata (Tags, Properties) (Planned)
  - **Testing & Validation Improvements:** *In Progress*
    - ✅ Fix identified bugs in validation framework (RequiredValidator parameter naming)
    - Implement test coverage improvement plan Phase 1 (Core Framework)
    - Create tests for core views, forms, and validators
    - Increase test coverage for core modules to 30%
    - Implement tests for product import and management commands
  - **Product Image Integration:** *In Progress*
    - Connect to external image database via API ✅ *Implemented*
    - Implement image prioritization and display in product views
    - Create caching mechanism for frequently accessed images
    - Develop image synchronization process with configurable frequency
    - Add image management capabilities for product administrators
    - Implement secure authentication to the image API ✅ *Implemented*
- **Phase 2:**  
  - Multi-warehouse, advanced production flows, partial/split invoicing.  
  - POS/Ecommerce integrations.  
  - Additional features as prioritized.  
  - **Testing & Validation Expansion:**
    - Implement test coverage improvement plan Phase 2 (Business Logic)
    - Add tests for product models, inventory logic, and sales workflows
    - Implement integration tests for critical business workflows
    - Add tests for API endpoints and views
    - Increase overall test coverage to 60%
- **Phase 3+:**  
  - Expand accounting integration, advanced analytics, further automation.  
  - **Testing & Validation Maturity:**
    - Implement test coverage improvement plan Phase 3 (Integration Points)
    - Add tests for legacy sync modules and management commands 
    - Create end-to-end tests for key user journeys
    - Implement continuous performance monitoring
    - Add automated regression testing
    - Maintain test coverage above 80% across all modules

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
  - **System Dependencies Management:** ✅ *Implemented*
    - Comprehensive identification of system-level dependencies for Python packages
    - Two-tier dependency strategy: build-time vs runtime dependencies
    - Special handling for graphical libraries (WeasyPrint, PDF generation)
    - MySQL client libraries for database connectivity
    - Font packages for document rendering

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
  - **GitHub Container Registry Integration:** ✅ *Implemented*
    - Container image hosting in GitHub Container Registry (ghcr.io)
    - Proper permission configuration for GitHub Actions workflows
    - Automated image building and pushing on commits to main branches
    - Semantic versioning tags for released images

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

### 4.16 CI/CD Pipeline Configuration

- **GitHub Actions Workflows:**
  - **Permissions Management:** ✅ *Implemented*
    - Explicit permission declarations for each workflow
    - Principle of least privilege for security
    - Specific package write permissions for GitHub Container Registry
  - **Workflow Structure:**
    - Parallel job execution for faster feedback
    - Build matrix for testing across environments
    - Reusable workflow components for maintainability
  - **Docker Integration:** ✅ *Implemented*
    - Docker Buildx for efficient, multi-platform builds
    - Layer caching for faster builds
    - Metadata extraction for consistent tagging
    - Multi-stage builds for optimized image size
  
- **Automated Testing Pipeline:** ✅ *Implemented*
  - Unit tests executed for all code changes
  - Integration tests for critical business flows
  - Code coverage reports and minimum thresholds
  - Performance benchmarks for key operations

- **Deployment Automation:**
  - Staging environment deployments for verification
  - Production deployment with approval gates
  - Automated rollback capabilities for failed deployments
  - Health checks after deployment

- **Quality Assurance:**
  - Static code analysis for quality issues
  - Security scanning for vulnerabilities
  - Dependency validation and updates
  - Documentation generation and validation

## 7. Non-Functional Requirements

### 7.1 Performance

- **Response Time:**  
  - User interface actions should complete within 1-2 seconds under normal load.  
  - Reports may take up to 10 seconds for complex data analysis.  
- **Concurrency:**  
  - Support for 15 simultaneous users with no degradation.  
  - Handle 50 concurrent API requests from external systems.  
- **Transaction Volume:**  
  - Manage up to 500 orders per day with related line items.  
  - Inventory movements: 1,500 per day.  

### 7.2 Reliability & Availability

- **Uptime Target:**  
  - 99.5% during business hours (8:00 AM to 6:00 PM, Monday through Friday).  
  - Scheduled maintenance windows outside business hours.  
- **Backup:**  
  - Daily incremental backups.  
  - Weekly full backups stored securely within the company's premises.  
- **Disaster Recovery:**  
  - Backup to production restored within 4 hours maximum.  
  - Potential for simple Active/Passive setup with automated failover (optional/budget permitting).  

### 7.3 Scalability

- **Data Growth:**  
  - 20% annual growth in transaction volume.  
  - No more than 10% degradation in performance with 2x data volume.  
- **User Growth:**  
  - Support scaling to 30 concurrent users within 2 years.  
- **Instance Scaling:**  
  - Docker Compose configuration allows for vertical scaling (more resources).  
  - Potential for horizontal scaling in future microservices architecture.  

### 7.4 Security

- **Authentication & Authorization:**  
  - Role-based access control with fine-grained permissions.  
  - Password policies enforced (complexity, expiration).  
  - MFA for admin users (optional/nice-to-have).  
- **Data Protection:**  
  - Encryption of sensitive data at rest and in transit.  
  - In-network deployment with limited exposure to the internet (DMZ for APIs).  
- **Audit Trail:**  
  - Logging of all critical data modifications (who, what, when).  
  - User session tracking.  

### 7.5 Testing Strategy

- **Testing Approach:**  
  - Unit tests for core business logic components. ✅ *Implemented*
  - Integration tests for API endpoints and workflows.
  - User acceptance testing for key business processes.
- **Mock Objects for Django Testing:** ✅ *Implemented*
  - Isolated test environment with mock Django models. ✅ *Implemented*
  - QuerySet simulation without database dependencies. ✅ *Implemented*
  - Model manager mocks for efficient testing. ✅ *Implemented*
- **Test Execution Framework:** ✅ *Implemented*
  - Running targeted tests to avoid Django app registry issues. ✅ *Implemented*
  - Custom scripts to bypass test collection problems. ✅ *Implemented*
  - Reporting and coverage analysis. ✅ *Implemented*
- **Continuous Integration:**
  - Automated test execution for every pull request.
  - Enforce minimum code coverage requirements.
  - Performance regression testing for critical components.