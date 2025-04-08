# Product Requirements Document (PRD)

**Project:** Custom ERP System (Django Monolith)

## 1. Purpose

Our goal is to build an on-premise, highly customized ERP system to manage the end-to-end processes of a small-to-medium-size manufacturing business. This system is developed using the Django framework in a monolithic architecture, with modular Django apps representing major business domains. It replaces our legacy 4D-based ERP and streamlines sales, production, and warehouse operations for both B2B and B2C customers.

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
   - On-prem deployment with Docker
   - Support for 15 concurrent users; handle expansions as needed
5. **Security & Authentication**
   - Django's built-in RBAC (Role-Based Access Control)
   - Token-based external integrations (OAuth2/JWT)
   - Auditing & logging for critical records
   - JWT authentication between Vue.js frontend and Django backend

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

## 4. Key Features & Implementation Status

### 4.1 Product & BOM Management

#### 4.1.1 Product Model Implementation

- **Model Architecture:**
  - Split model approach with BaseProduct abstract class
  - Dedicated ParentProduct model for product families
  - VariantProduct model for specific product variants
  - Legacy Product model maintained for backwards compatibility
  - Robust relationships between parent and variant products

- **Product Image Integration:**
  - Connection to external Django application managing product images via API
  - Display product images with proper prioritization
  - Support for different image types and formats
  - Smart article number selection based on product hierarchy
  - Robust fallback strategy for image retrieval

#### 4.1.2 Data Synchronization Framework

- **Modular ETL Architecture:**
  - Base classes for extractors, transformers, and loaders
  - Standardized interface for extracting data from different legacy system tables
  - Configuration-driven sync operations via YAML
  - Support for incremental and full sync modes

### 4.2 Sales Management

- **Customer and Address Data Migration:**
  - Customer model mapped to Kunden table in legacy system
  - Address model with one-to-many relationship to customers
  - ETL components for data synchronization
  - Field validation and relationship management

### 4.3 Security & Authentication

- **User Authentication Framework:**
  - JWT-based authentication for Vue.js frontend
  - Password security with Django's built-in mechanisms
  - Password complexity requirements and reset functionality


### 4.5 Testing & Quality Assurance

- **Testing Framework:**
  - pytest as primary testing framework with Django plugins
  - Mock objects for external dependencies
  - Validation framework with unit tests
  - CI/CD integration with automated testing

### 4.6 System Monitoring & Administration

- **Status Dashboard:**
  - Admin view for monitoring critical system connections
  - Real-time status indicators for various system components
  - Historical uptime logging and basic analytics

### 4.7 Database Configuration

- **PostgreSQL Implementation:**
  - Migration from SQLite to PostgreSQL
  - Environment-specific database configurations
  - Secure credential management via environment variables

## 5. Infrastructure & Deployment

- **Docker-Based Environment:**
  - Consistent development environment via Docker Compose
  - Production-optimized Docker images
  - GitHub Container Registry integration

- **CI/CD Pipeline:**
  - GitHub Actions workflows with parallel job execution
  - Automated testing and quality checks
  - Deployment automation with environment-specific configurations

## 6. Project Roadmap

### Current Phase
- Product data model and management
- Integration with external image database
- Customer data migration and management
- Testing framework and validation system
- Database migration to PostgreSQL

### Next Phase
- Complete Sales module implementation
- Inventory/Warehouse management
- Order processing workflow
- Reporting and analytics
- Enhanced user management and permissions

### Future Phase
- Production planning and management
- Advanced scheduling features
- External system integrations (POS, eCommerce)
- Business intelligence and advanced reporting

## 7. Non-Functional Requirements

- **Performance:** User interface actions should complete within 1-2 seconds under normal load
- **Reliability:** 99.5% uptime during business hours with daily backups
- **Scalability:** Support for growing to 30 concurrent users within 2 years
- **Security:** Role-based access control and data protection measures
