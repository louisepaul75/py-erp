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
  - Prioritize image display based on type and attributes (front=true flag). ✅ *Implemented*
  - Enhanced product matching logic to handle variant codes and different SKU formats. ✅ *Implemented*
- **Image Management:**
  - Display product images in the ERP interface with proper prioritization. ✅ *Implemented*
  - Allow users to view all available images for a product. ✅ *Implemented*
  - Enable selection of primary product image for display in various contexts. ✅ *Implemented*
  - Support batch operations for image management across multiple products. *Planned*
  - Strict image prioritization hierarchy (Produktfoto with front=True > any Produktfoto > images with front=True). ✅ *Implemented*
- **Caching & Performance:**
  - Implement caching strategy for frequently accessed images to improve performance. ✅ *Implemented*
  - Support for image thumbnails generation and resizing for different UI contexts. ✅ *Implemented*
  - Asynchronous loading of images to prevent UI performance degradation. *Planned*
- **Synchronization:**
  - Regular synchronization with the image database to ensure up-to-date images. ✅ *Implemented*
  - Track image changes and updates for audit purposes. ✅ *Implemented*
  - Handle conflict resolution for image changes. ✅ *Implemented*
- **Format Optimization:** ✅ *Implemented*
  - Prioritize web-friendly formats (PNG, JPEG) over design formats (PSD, etc.). ✅ *Verified*
  - Select highest quality available image based on resolution and format. ✅ *Verified*
  - Support appropriate image formats for different use cases (thumbnails, product detail, etc.). ✅ *Verified*
- **Parent-Variant Product Handling:** ✅ *Implemented*
  - Smart article number selection based on product hierarchy. ✅ *Implemented*
  - Determine appropriate article number for image search based on product type (parent/variant). ✅ *Implemented*
  - For parent products: Use parent's SKU. ✅ *Implemented*
  - For variants with parent: Use parent's SKU for consistent imagery. ✅ *Implemented*
  - For variants without parent: Use base_sku if available, otherwise use variant's SKU. ✅ *Implemented*
- **Fallback Logic:** ✅ *Implemented*
  - Implement robust fallback strategy for image retrieval. ✅ *Implemented*
  - First try with the appropriate article number based on product type. ✅ *Implemented*
  - If no images found, try with the product's own SKU. ✅ *Implemented*
  - If still no images and it's a variant, try with base_sku. ✅ *Implemented*
  - If still no images and it has a parent, try with parent's SKU. ✅ *Implemented*
  - Detailed logging of fallback attempts for troubleshooting. ✅ *Implemented*

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
  - Image types include: Produktfoto, Markt-Messe-Shop, Szene, Illustration, etc. ✅ *Verified*
  - Resolution options range from thumbnails (200×200) to full size (4032×3024) ✅ *Verified*
- **Image Prioritization Logic:**
  - Products with front=true and Produktfoto type have highest priority ✅ *Implemented*
  - File formats are prioritized: PNG > JPEG > original format ✅ *Implemented*
  - Images can be associated with multiple products ✅ *Verified*
- **Product-Image Matching:**
  - Parent products use their own SKU for image matching ✅ *Implemented*
  - Variant products primarily use parent SKU for consistent imagery ✅ *Implemented*
  - Fallback mechanisms ensure maximum image coverage ✅ *Implemented*
  - Intelligent article number selection based on product hierarchy ✅ *Implemented*
  - Proper handling of article number formats with and without variant codes ✅ *Implemented*

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
    - Parent product SKUs are derived from the `Nummer` column in Artikel_Familie ✅
  - **Variant Product Import**: Verified with dry-run from Artikel_Variante ✅
    - Primary SKU for variants now uses the `Nummer` column from Artikel_Variante ✅
    - Legacy SKU (`alteNummer`) stored in dedicated `legacy_sku` field for reference ✅
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
  - **SKU Handling Strategy:** ✅ *Implemented*
    - **Parent Products**: Use `Nummer` from Artikel_Familie as the primary SKU ✅
    - **Variant Products**: Use `Nummer` from Artikel_Variante as the primary SKU ✅
    - Store `alteNummer` from Artikel_Variante in the `legacy_sku` field for reference ✅
    - Fallback to `alteNummer` if `Nummer` is not available for variants ✅
    - Extract base SKU and variant code by splitting the legacy SKU at the last hyphen ✅
      - Base SKU: Everything before the last hyphen (e.g., "KS-17" from "KS-17-BE") ✅
      - Variant code: Everything after the last hyphen (e.g., "BE" from "KS-17-BE") ✅
      - For SKUs without hyphens, the entire SKU becomes the base SKU with an empty variant code ✅
    - Maintain backward compatibility with legacy systems through `legacy_sku` field ✅

- **Progress Summary:**
  - ✅ Parent product import completed successfully (1,564 products created)
  - ✅ Parent-child relationships updated successfully (3,726 relationships established)
  - ✅ Variant product import completed successfully
  - ✅ SKU handling strategy updated to use `Nummer` as primary identifier
  - ✅ Added `legacy_sku` field to store `alteNummer` for reference
  - ✅ Implemented and tested base SKU and variant code extraction by splitting at the last hyphen
  - ✅ Full variant product import completed (86.27% of variants migrated)
  - ⬜ Product categorization enhancement pending
  - ✅ Split product model structure implemented with `BaseProduct`, `ParentProduct`, and `VariantProduct`
  - ✅ Migration command `migrate_to_split_models` implemented and tested
  - **NEW**: Identified SKU mapping issue in parent products (SKU and legacy_id fields were swapped).
  - **NEW**: Created `fix_parent_sku_mapping` command to correct the SKU and legacy_id field values.
  - **NEW**: Created `fix_variant_parent_relationships` command to update variant-parent relationships.
  - **NEW**: Executed the `wipe_and_reload_variants` command successfully, creating 4,319 variant products.
  - **NEW**: Successfully linked 4,228 variants (97.89%) to their parent products via the `fix_variant_parent_relationships` command.
  - **NEW**: Identified 91 variants (2.11%) without corresponding parent products that will need further investigation.
  - **NEW**: Implemented legacy data tracking with new fields to store original `__KEY`, `UID`, and `FAMILIE_` values.
  - **NEW**: Verified correct matching and linking between variants and parents using the `legacy_familie` and parent `legacy_id` fields.

- **Next Steps for Product Data Migration:**
  - ✅ Variant import script tested and executed in production
  - ✅ Base SKU and variant code extraction logic verified and implemented
  - ✅ Execute full import with all variants
  - ✅ Fix variant-parent relationships (97.89% successfully linked)
  - ⬜ Investigate and create placeholder parents for the 91 variants (2.11%) with missing parents
  - ⬜ Enhance product categorization based on Familie_ field and legacy categories
  - ⬜ Import additional product attributes (dimensions, weights, tags)
  - ⬜ Implement full-text search indexing for improved product discovery
  - ⬜ Add incremental sync capability for ongoing updates from legacy system
  - ⬜ Create data quality reports to identify potential issues in imported data
  - ✅ Update model to include legacy fields for tracking original keys and IDs from the source system
  - ⬜ Address variants with missing parent products with a command to create placeholder parents
  - ⬜ Enhance product categorization and attribute assignments

### 4.6.2 Variant-Parent Relationship Verification

- **Relationship Validation Assessment:** ✅ *Implemented*
  - **Variant-Parent Linking Summary:**
    - Total variant products in system: 4,319 ✅
    - Variants with parent relationships: 4,228 (97.89%) ✅
    - Variants without parent relationships: 91 (2.11%) ✅
    - Relationship linking via `legacy_familie` in variants to `legacy_id` in parents ✅
  
  - **Relationship Quality Verification:** ✅ *Implemented*
    - Verified consistent linking between variants and parents via `legacy_familie` field ✅
    - Example of correct relationship: Variant SKU 807130 linked to Parent SKU 912859 ✅
    - Confirmed matching values between variant's `legacy_familie` and parent's `legacy_id` ✅
    - Successfully established parent-child product hierarchy for 97.89% of variants ✅
  
  - **Missing Relationship Analysis:** ✅ *Implemented*
    - Identified 91 variants without parent relationships ✅
    - Confirmed no matching parent products exist with corresponding `legacy_id` values ✅
    - Missing parent relationships appear to be genuine data gaps rather than import errors ✅
    - Sample variant without parent: SKU 206627, Familie: 692331CEA5947D448BACF105BEE181B8 ✅
  
  - **Legacy Field Tracking:** ✅ *Implemented*
    - Added `legacy_key` field to store original `__KEY` values from source system ✅
    - Added `legacy_uid_original` field to store original `UID` values ✅
    - Added `legacy_familie` field to store original `FAMILIE_` values for relationship linking ✅
    - Successfully populated these fields during variant product import ✅
    - Successfully used `legacy_familie` field to establish parent-child relationships ✅

- **Relationship Improvement Plan:**
  - **Short-term Actions:** *High Priority*
    - Create command to generate placeholder parent products for orphaned variants (91 products)
    - Set placeholder flag on these generated parent products for future data quality management
    - Re-run relationship linking command after placeholder creation
  
  - **Medium-term Actions:** *Medium Priority*
    - Develop data quality report to identify incomplete or inconsistent product relationships
    - Implement consistency validation to ensure variants properly inherit attributes from parents
    - Create UI indicators for placeholder parent products that need manual review
  
  - **Long-term Actions:** *Low Priority*
    - Integrate with legacy system to identify matching parents if they are created later
    - Develop automated rules for inferring parent attributes based on variant patterns
    - Establish ongoing data quality checks for product relationships

- **Implementation Results:** ✅ *Implemented*
  - **Placeholder Parent Creation:** ✅ *Implemented*
    - Successfully created 47 placeholder parent products for orphaned variants ✅
    - Added `is_placeholder` flag to `ParentProduct` model to mark generated placeholders ✅
    - Implemented naming convention with "PLACEHOLDER-" prefix for easy identification ✅
  
  - **Variant-Parent Linking:** ✅ *Implemented*
    - Successfully linked 44 remaining variants to existing parent products ✅
    - Created `link_variants_to_existing_parents` command to handle duplicate legacy_id cases ✅
    - Achieved 100% parent-child relationship coverage for all 4,319 variants ✅
  
  - **Verification Results:** ✅ *Implemented*
    - Confirmed all variants now have parent relationships ✅
    - Verified correct matching between variant's `legacy_familie` and parent's `legacy_id` ✅
    - Created comprehensive reporting tools to analyze relationship quality ✅
    - Documented the process and results in the PRD ✅

### 4.6.3 Database Migration from SQLite to PostgreSQL

- **Migration Objectives:** ✅ *Implemented*
  - Transition from SQLite to PostgreSQL for improved performance and scalability ✅
  - Support multi-user concurrent access for production environment ✅
  - Maintain compatibility with existing application code ✅
  - Ensure proper data integrity during migration ✅

- **Implementation Strategy:** ✅ *Implemented*
  - **Configuration Updates**: Successfully modified database settings ✅
    - Updated development settings to use PostgreSQL configuration ✅
    - Created dedicated testing settings with PostgreSQL configuration ✅
    - Implemented environment variable-based connection parameters ✅
  
  - **Environment Configuration**: ✅ *Implemented*
    - Created `.env` file for storing PostgreSQL connection parameters ✅
    - Configured connection to PostgreSQL server ✅
    - Set up appropriate database credentials and connection details ✅
    - Implemented fallback values for environment variables ✅
  
  - **Testing & Validation**: ✅ *Implemented*
    - Verified database connection through Django's check commands ✅
    - Successfully ran basic tests with PostgreSQL configuration ✅
    - Confirmed proper schema creation and data access ✅
    - Created comprehensive PostgreSQL setup documentation ✅

- **Documentation Updates:** ✅ *Implemented*
  - Updated README.md with PostgreSQL setup instructions ✅
  - Created PostgreSQL-specific setup guide for new developers ✅
  - Updated user stories to reflect completed migration ✅
  - Documented environment variable requirements ✅

- **Progress Summary:**
  - ✅ Successfully migrated from SQLite to PostgreSQL
  - ✅ Configured environment for PostgreSQL connections
  - ✅ Verified database functionality with tests
  - ✅ Updated all relevant documentation

### 4.7 Security & Authentication

#### 4.7.1 User Authentication Framework

- **Authentication Methods:**
  - **Primary Authentication:** Form-based authentication with username/password for staff users ✅ *Implemented*
  - **API Authentication:** JWT tokens for integration with external systems ✅ *Implemented*
  - **Vue.js Frontend Authentication:** JWT-based authentication with automatic token refresh ✅ *Implemented*
    - Comprehensive implementation with login/logout, profile management, and protected routes ✅ *Implemented*
    - Technical documentation available in docs/vue_auth_implementation.md ✅ *Implemented*
  - **SSO Integration:** Support for LDAP/Active Directory integration (future phase)
  - **Multi-Factor Authentication (MFA):** Optional two-factor authentication for sensitive roles
  - **Password Management:**
    - Secure password hashing with Django's built-in mechanisms ✅ *Implemented*
    - Password complexity requirements enforced via validators ✅ *Implemented*
    - Password expiration and history policies
    - Self-service password reset functionality ✅ *Implemented*

- **Session Management:**
  - Configurable session timeout (default 24 hours for standard users)
  - Reduced session timeout (4 hours) for administrative users
  - Session invalidation upon password change
  - Concurrent session limitations for sensitive roles
  - Remember-me functionality for non-sensitive interfaces

#### 4.7.2 User & Role Management

- **User Model Structure:**
  - Extended Django User model with additional fields for ERP-specific requirements
  - User profile with contact information, preferences, and system settings
  - User status tracking (active, inactive, suspended, pending approval)
  - Department and site location associations
  - Employment information (position, supervisor, hire date)

- **User Types:**
  - **Internal Users:** Staff members directly employed by the organization
  - **External Users:** Contractors, temporary workers, consultants
  - **System Users:** Service accounts for automated processes and integrations
  - **API Users:** Limited accounts for external system connections

- **User Lifecycle Management:**
  - User registration with approval workflow
  - Automated account provisioning based on templates
  - Account suspension and deactivation workflows
  - Compliance with data retention policies
  - User offboarding checklists and automation

- **Role-Based Access Control (RBAC):**
  - **Core Roles:**
    - **Viewer:** Read-only access to non-sensitive data
    - **Operator:** Basic operational capabilities within assigned modules
    - **Manager:** Enhanced operational capabilities and limited administrative functions
    - **Administrator:** Full system administration within defined domains
    - **System Administrator:** Complete system access and configuration
  
  - **Functional Roles:**
    - **Sales Representative:** Manage customers, quotes, orders
    - **Sales Manager:** Oversee sales operations, approve special pricing
    - **Production Planner:** Create and manage production orders
    - **Production Manager:** Manage production capacity and resources
    - **Warehouse Clerk:** Handle inventory movements and stock management
    - **Warehouse Manager:** Oversee warehouse operations and transfers
    - **Purchase Officer:** Create and manage purchase orders
    - **Finance User:** View and export invoice data, track payments
    - **Marketing User:** Access product data for marketing materials
    - **Quality Assurance:** Monitor and record quality control processes
    - **Customer Service:** Handle customer inquiries and returns
  
  - **Role Assignment:**
    - Users can have multiple roles
    - Role inheritance hierarchy
    - Role assignment approval workflow
    - Temporary role assignments with expiration
    - Role-based UI customization

#### 4.7.3 Permission Management

- **Permission Granularity:**
  - **Model-Level Permissions:** Create, read, update, delete
  - **Field-Level Permissions:** Sensitive field access control
  - **Function-Level Permissions:** Access to specific actions and operations
  - **Data-Level Permissions:** Row-level security based on department, location, etc.
  - **Report-Level Permissions:** Access to specific reports and analysis tools

- **Permission Categories:**
  - **Products & BOM:**
    - View products
    - Create/modify products
    - Manage product pricing
    - View BOM structures
    - Create/modify BOM
    - Archive/delete products
  - **Sales:**
    - View customers
    - Create/modify customers
    - Create quotes
    - Convert quotes to orders
    - Apply discounts (tiered by discount percentage)
    - Cancel/modify orders
    - Issue credits
  - **Production:**
    - View production orders
    - Create production orders
    - Modify production schedules
    - Report production completion
    - Manage production resources
  - **Inventory:**
    - View inventory levels
    - Create stock movements
    - Adjust inventory
    - Manage multiple warehouses
    - Transfer between locations
  - **System Administration:**
    - User management
    - Role/permission management
    - System configuration
    - Data import/export
    - Integration management

- **Permission Assignment:**
  - Predefined permission sets for common roles
  - Custom permission configurations for specialized roles
  - Permission request and approval workflow
  - Periodic permission review and certification

#### 4.7.4 Security Controls & Compliance

- **Access Control:**
  - IP-based access restrictions for sensitive operations
  - Device registration for multi-factor authentication
  - Login attempt monitoring and lockout policies
  - Administrative action approval workflows

- **Audit & Logging:**
  - Comprehensive audit trails for all security-related events
  - User session recording (login/logout times, IP addresses)
  - Critical data modification logging (before/after values)
  - Privileged action monitoring and alerting
  - Log integrity protection and retention

- **Segregation of Duties:**
  - Role-based segregation to prevent conflicts of interest
  - Transaction approval workflows for sensitive operations
  - Dual control requirements for critical functions
  - Automated detection of segregation violations

- **Data Protection:**
  - Field-level encryption for sensitive data
  - Masked display of sensitive information
  - Export controls and data loss prevention
  - Data minimization in API responses

#### 4.7.5 Integration Authentication

- **API Security:**
  - OAuth2/JWT token-based authentication for all APIs ✅ *Partially Implemented*
  - API key management for service accounts
  - Scoped API tokens with limited permissions
  - Rate limiting and abuse prevention
  - API audit logging

- **External System Integration:**
  - Secure credential storage for external connections
  - OAuth-based authentication with integrated systems
  - Mutual TLS for secure server-to-server communication
  - Scheduled credential rotation

#### 4.7.6 User Interface Security

- **UI Security Controls:**
  - Dynamic menu rendering based on user permissions
  - Function-level UI element visibility
  - Form field access control
  - Context-aware security indicators
  - Session timeout notifications
  - Concurrent session alerts

- **Security Notifications:**
  - User-facing security alerts
  - Administrative security dashboards
  - Automated security incident reporting
  - Compliance status monitoring

#### 4.7.7 Implementation Phases

- **Phase 1 (MVP):**
  - Basic user authentication with Django's built-in system ✅ *Implemented*
  - Core role definitions with Django permissions ✅ *Partially Implemented*
  - JWT authentication for API access ✅ *Implemented*
  - Basic audit logging for critical actions ✅ *Implemented*

- **Phase 2 (Enhanced):**
  - Extended user profile with additional fields
  - Complete role-based access control implementation
  - Field-level permission controls
  - Enhanced audit logging with UI for review
  - User and role management interfaces
  - Django framework upgrade to 5.1.6 ✅ *Implemented*

- **Phase 3 (Advanced):**
  - Multi-factor authentication
  - Advanced segregation of duties
  - Automated compliance reporting
  - Integration with LDAP/Active Directory
  - Security analytics and anomaly detection

#### 4.7.8 Technical Architecture

The user and roles system will be built on Django's authentication framework with strategic extensions for ERP-specific needs:

- **Core Components:**
  - **Django Framework:** Now using Django 5.1, with improved performance and security features
  - **Custom User Model:** Extend Django's AbstractUser to include additional fields
    ```python
    # Example structure (not actual implementation)
    class User(AbstractUser):
        status = models.CharField(choices=USER_STATUS_CHOICES, default='active')
        department = models.ForeignKey('Department', null=True, on_delete=models.SET_NULL)
        employee_id = models.CharField(max_length=50, blank=True)
        phone = models.CharField(max_length=20, blank=True)
        # Additional fields as needed
    ```
  
  - **Profile Model:** One-to-one relationship with User for extended attributes
    ```python
    # Example structure (not actual implementation)
    class UserProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
        position = models.CharField(max_length=100, blank=True)
        supervisor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='supervised_users')
        hire_date = models.DateField(null=True, blank=True)
        preferences = models.JSONField(default=dict)
        # Additional profile fields
    ```
  
  - **Role Implementation:**
    - Leverage Django's Group model for basic roles
    - Create a Role model that extends Group for advanced features
    ```python
    # Example structure (not actual implementation)
    class Role(models.Model):
        group = models.OneToOneField(Group, on_delete=models.CASCADE)
        description = models.TextField(blank=True)
        is_system_role = models.BooleanField(default=False)
        parent_role = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
        # Additional role metadata
    ```
  
  - **Role Assignment:**
    - Use a through model for user-role assignments with time limits
    ```python
    # Example structure (not actual implementation)
    class UserRole(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        role = models.ForeignKey(Role, on_delete=models.CASCADE)
        assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_assignments')
        assigned_at = models.DateTimeField(auto_now_add=True)
        expires_at = models.DateTimeField(null=True, blank=True)
        is_active = models.BooleanField(default=True)
        # Additional assignment metadata
    ```
  
  - **Permission Extensions:**
    - Create models for function-level and object-level permissions
    ```python
    # Example structure (not actual implementation)
    class FunctionPermission(models.Model):
        name = models.CharField(max_length=100, unique=True)
        code = models.CharField(max_length=100, unique=True)
        description = models.TextField(blank=True)
        roles = models.ManyToManyField(Role, related_name='function_permissions')
        
    class ObjectPermission(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey('content_type', 'object_id')
        can_view = models.BooleanField(default=False)
        can_edit = models.BooleanField(default=False)
        can_delete = models.BooleanField(default=False)
        # Additional permission flags
    ```

- **Authentication Flow:**
  1. User submits credentials via login form or API
  2. Django authenticates against the User model
  3. Optional MFA verification step (Phase 3)
  4. Session creation with role and permission caching
  5. Middleware loads user permissions for request processing

- **Authorization Process:**
  1. Permission checking via decorators on views/API endpoints
  2. Template-level permission checks for UI elements
  3. Object-level permission verification for data access
  4. Function-level permission validation for business operations

- **Audit Logging Architecture:**
  - Use Django signals to capture model changes
  - Central AuditLog model for all security events
  - Specialized logging for authentication events
  - Integration with Django logging framework

  **Audit Logging Implementation Details:**
  - Central `AuditLog` model created in the core app
  - Comprehensive event tracking for security-related actions:
    - Authentication events (login, logout, failed logins)
    - User management (creation, updates, deletion)
    - Permission changes 
    - Critical data access and modifications
  - Automatic capture of contextual data:
    - User identification (with fallback username if user is deleted)
    - IP address and user agent information
    - Timestamp and unique event ID
    - Related object references via ContentType framework
  - Integration with Django signals:
    - Authentication signals (login, logout, login_failed)
    - User model signals (post_save)
  - Service layer (`AuditService`) for consistent logging across the application
  - Admin interface for security review with filtering and search capabilities
  - Non-modifiable logs to maintain audit integrity

- **Security Considerations:**
  - Password hashing with Django's PBKDF2 algorithm
  - CSRF protection for all form submissions
  - HTTP-only cookies for session management
  - Session timeout configuration
  - XSS prevention in templates

- **Integration Points:**
  - Role-based menu rendering in base templates
  - Permission checking in view decorators
  - Object permission filtering in querysets
  - Session-based permission caching for performance

This architecture provides a solid foundation that can be implemented incrementally according to the phased approach outlined in section 4.7.7.

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
  - Maintain separate PostgreSQL databases for development/testing and production. ✅
  - Configure environment-specific settings that consistently select the correct database. ✅
  - Development environments always connect to testing database (pyerp_testing). ✅
  - Production environments always connect to live database (pyerp_production). ✅
  - Database connection settings persist across Git operations. ✅
- **Database Migration from SQLite to PostgreSQL:** ✅ *Implemented*
  - Updated development settings to use PostgreSQL instead of SQLite for consistency with production. ✅
  - Created .env file with PostgreSQL connection parameters for local development. ✅
  - Successfully created database schema by running migrations. ✅
  - Updated documentation to reflect PostgreSQL-only development workflow. ✅
  - Created comprehensive PostgreSQL setup guide in docs/development/postgresql_setup.md. ✅
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
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
            'USER': os.environ.get('DB_USER', 'postgres'),  # Default fallback value
            'PASSWORD': os.environ.get('DB_PASSWORD'),   # Should be provided in .env
            'HOST': os.environ.get('DB_HOST'),           # Should be provided in .env
            'PORT': os.environ.get('DB_PORT', '5432'),   # Default PostgreSQL port
        }
    }
    ```
  - Production Environment:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'pyerp_production'),
            'USER': os.environ.get('DB_USER'),           # Should be provided in .env
            'PASSWORD': os.environ.get('DB_PASSWORD'),   # Should be provided in .env
            'HOST': os.environ.get('DB_HOST'),           # Should be provided in .env
            'PORT': os.environ.get('DB_PORT', '5432'),   # Default PostgreSQL port
        }
    }
    ```
  - Alternative using DATABASE_URL (implemented but commented out in code):
    ```python
    import dj_database_url
    
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost:5432/dbname'),
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
    - Implemented and tested base SKU and variant code extraction logic ✅
    - Enhance product categorization with full hierarchy (Planned)
    - Map Artikel_Familie data to product categories (Planned)
    - Extract and import additional product metadata (Tags, Properties) (Planned)
  - **Testing & Validation Improvements:** *In Progress*
    - ✅ Fix identified bugs in validation framework (RequiredValidator parameter naming)
    - Implement test coverage improvement plan Phase 1 (Core Framework)
    - Create tests for core views, forms, and validators
    - Increase test coverage for core modules to 30%
    - Implement tests for product import and management commands
  - **Product Image Integration:** ✅ *Implemented*
    - Connect to external image database via API ✅ *Implemented*
    - Implement secure authentication to the image API ✅ *Implemented*
    - Create caching mechanism for frequently accessed images ✅ *Implemented*
    - Implement image prioritization and display in product views ✅ *Implemented*
    - Add smart article number selection based on product hierarchy ✅ *Implemented*
    - Create robust fallback logic for image retrieval ✅ *Implemented*
    - Enhance ProductListView to preload images for both parent and variant products ✅ *Implemented*
    - Implement custom template filter for accessing dictionary items by key ✅ *Implemented*
    - Add detailed logging for image retrieval process ✅ *Implemented*
    - Create database models for storing product images locally ✅ *Implemented*
    - Implement image synchronization command with configurable parameters ✅ *Implemented*
    - Create logging system for tracking synchronization history ✅ *Implemented*
    - Add support for filtering and limiting synchronization scope ✅ *Implemented*
    - Develop image management capabilities for product administrators (Planned)
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
  - **WebSocket & Real-time Updates - Phase 1:**
    - Implement Django Channels infrastructure with Redis backend
    - Create core WebSocket authentication and connection handling
    - Develop the central notification system framework
    - Build notification preferences management UI
    - Implement real-time inventory level updates for critical products
    - Add WebSocket testing framework and basic tests

- **Phase 3+:**  
  - Expand accounting integration, advanced analytics, further automation.  
  - **Testing & Validation Maturity:**
    - Implement test coverage improvement plan Phase 3 (Integration Points)
    - Add tests for legacy sync modules and management commands 
    - Create end-to-end tests for key user journeys
    - Implement continuous performance monitoring
    - Add automated regression testing
    - Maintain test coverage above 80% across all modules
  - **WebSocket & Real-time Updates - Phase 2:**
    - Extend real-time features to order processing workflows
    - Implement live production status tracking
    - Add real-time dashboard updates for KPIs and metrics
    - Develop collaborative editing features with conflict prevention
    - Create comprehensive WebSocket monitoring and diagnostics
    - Scale WebSocket architecture for high-volume events

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

### 4.17 WebSockets & Real-time Updates Integration

- **Real-time Communication Framework:**
  - Integration of Django Channels for WebSocket support
  - Asynchronous event handling for scalable real-time operations
  - Redis as the channel layer backend for production
  - In-memory channel layer for development environments
  - Secure WebSocket connections with authentication

- **Key Real-time Features:**
  - **Inventory Monitoring:**
    - Real-time stock level updates across multiple warehouses
    - Instant alerts for low stock or stockout conditions
    - Live inventory adjustment notifications
  - **Order Processing:**
    - Immediate order status updates for sales team
    - Real-time notifications for new orders from all channels (POS, eCommerce)
    - Live updates for order modifications and cancellations
  - **Production Workflow:**
    - Real-time production order status tracking
    - Instant notification of production milestone completions
    - Live updates on machine/workstation status
  - **Collaborative Features:**
    - Real-time presence indication for users viewing the same records
    - Live updates when multiple users edit related data
    - Prevention of conflicting concurrent edits
  - **Dashboard & Analytics:**
    - Live KPI updates on management dashboards
    - Real-time sales metrics and trend visualization
    - Dynamic production efficiency indicators
  - **Notification System:**
    - Centralized real-time notification hub for users
    - Customizable alert preferences by role and importance
    - Desktop notifications for critical events

- **Technical Implementation Strategy:**
  - **Consumer Architecture:**
    - Modular WebSocket consumers organized by business domain
    - Consistent authentication and authorization patterns
    - Standardized message format for all real-time communications
  - **Event Broadcasting:**
    - Centralized event dispatch mechanism
    - Targeted broadcast to specific users, groups, or channels
    - Event batching for high-frequency updates to prevent UI flooding
  - **Frontend Integration:**
    - Standardized JavaScript client for WebSocket connections
    - Reconnection logic with exponential backoff
    - Consistent event handling patterns across the application
  - **Scalability Considerations:**
    - Proper channel naming conventions to prevent memory leaks
    - Efficient group management for broadcasting
    - Connection monitoring and limiting mechanisms

- **Testing & Monitoring:**
  - Specialized testing framework for WebSocket consumers
  - Simulation tools for high-volume real-time events
  - Monitoring of WebSocket connection health and message throughput
  - Performance testing under various loads

- **Implementation Phases:**
  - **Phase 1:** Core WebSocket infrastructure and notification system
  - **Phase 2:** Inventory and order update features
  - **Phase 3:** Production tracking and dashboard integration
  - **Phase 4:** Collaborative features and advanced notifications

### 4.18 Internationalization & Localization (i18n/l10n) Framework

#### 4.18.1 Implementation Status & Progress (March 2024)

- **Current Implementation Status:**
  - **✅ Basic Framework Setup:**
    - Successfully integrated Django's internationalization system with proper settings configuration
    - Configured `LANGUAGE_CODE='de'` as the default language
    - Set up German and English as supported languages
    - Created proper locale directories structure (`pyerp/locale/de/LC_MESSAGES/` and `pyerp/locale/en/LC_MESSAGES/`)
    - Created and compiled translation files (.po and .mo) for both German and English
  - **✅ UI Language Elements:**
    - Added a functional language switcher in the application header
    - Implemented language dropdown menu with language names in their native form
    - Added "i18n" context to all translatable UI elements using Django's `{% translate %}` tags
    - Applied URL-based language switching using Django's i18n URL patterns system
  - **🚧 URL Configuration:**
    - Reorganized URL routing to separate non-internationalized URLs (admin, API) from internationalized ones
    - Set up URL patterns with language prefixes (e.g., `/en/products/`, `/de/products/`)
    - Implemented proper URL structure for switching between languages

- **Current Challenges:**
  - **❌ 404 Errors on Language Switching:** Users currently experience 404 errors when attempting to switch languages
  - Root cause appears to be in the URL dispatcher configuration or middleware processing
  - Language prefix URLs (e.g., `/de/products/`) are not being properly matched to view functions
  - Debug information confirms the URL language prefix is being correctly added but route matching fails
  - Conflict between language code in cookie/session and URL path may be contributing to the issue

- **Next Steps:**
  - **Fix URL Routing:**
    - Review URL dispatcher and ensure proper middleware order for Django's language handling
    - Validate that internationalized URLs are being processed correctly by Django's i18n system
    - Ensure appropriate middleware ordering (`LocaleMiddleware` after session middleware but before common middleware)
  - **Alternative Approaches to Consider:**
    - Possible reconfiguration of `i18n_patterns()` to better handle URLs
    - Consider selectively enabling i18n routing for specific URL patterns rather than all app URLs
    - Evaluate URL routing with debugger to find exact point where matching fails
  - **Debugging Strategy:**
    - Add verbose debug logging in middleware handling
    - Test with simplified URL structure to isolate the issue
    - Review Django version compatibility with our implementation approach

#### 4.18.2 Multilingual UI Design & Architecture

- **Multilingual User Interface Strategy:**
  - **Supported Languages:**
    - **Phase 1:** German (primary), English (secondary)
    - **Phase 2:** Additional languages based on business expansion (French, Spanish, etc.)
    - Default language detection based on browser settings with manual override
  - **UI Language Elements:**
    - Complete translation of all interface elements, messages, and notifications
    - Language selection in user preferences and session-based settings
    - Visual language switcher in the application header
    - Language-specific login pages
    - Support for multi-language error messages and form validations
  - **Right-to-Left (RTL) Support:**
    - CSS framework with RTL capabilities for future language expansion
    - Flexible layout components that adapt to text direction
    - Proper handling of directional elements (arrows, icons, etc.)

- **Content Translation Strategy:**
  - **Static Content:**
    - Translation via Django's built-in gettext framework
    - Message extraction and compilation workflow
    - Language file management and organization by module
  - **Dynamic Content:**
    - Model-level translation for product descriptions, categories, etc.
    - Translation fields in database models (e.g., `name_de`, `name_en`, etc.)
    - API support for content translation and language-specific data
    - Translation fallback mechanism (use primary language if translation missing)
  
- **Date, Time, and Number Formatting:**
  - Locale-specific date and time formats
  - Number formatting with appropriate decimal and thousand separators
  - Currency display with proper symbols and formatting
  - Unit conversion where applicable (metric/imperial)
  - Calendar localization for date pickers and scheduling interfaces

- **Translation Management Workflow:**
  - Extraction of translatable strings using Django's `makemessages` command
  - Translation files (.po) organization by app and language
  - Translation compilation process into binary (.mo) files
  - Version control integration for translation files
  - Translator guidelines and context documentation
  - Translation quality assurance process

- **Technical Implementation:**
  - **URL-based Language Switching:**
    - Integration of Django's language prefix URL pattern
    - URL format: `/{language_code}/path/to/view/`
    - Language persistence via session and/or user preferences
    - Automatic language detection with manual override
  - **Middleware Configuration:**
    - Enable Django's `LocaleMiddleware` for language detection and switching
    - Custom middleware for language-specific business logic if needed
    - Session-based language persistence
  - **Template Enhancements:**
    - Consistent use of translation tags in all templates
    - Language-specific template overrides when needed
    - Block-level translation for complex content
    - Translation context usage for ambiguous terms
  - **JavaScript Internationalization:**
    - Client-side translation with Django's JavaScript catalog
    - AJAX handling for language-specific responses
    - Dynamic content loading with proper language context
    - Date and number formatting in JavaScript

- **Translation Resources:**
  - **Translation Management System:**
    - Initially Git-based workflow with .po files
    - Potential integration with translation management tools in future phases
    - Process for external translator collaboration
  - **Translation Memory:**
    - Reuse of previously translated strings
    - Terminology consistency across the application
    - Context documentation for translators
  - **Quality Assurance:**
    - Translation validation tools
    - Visual inspection in multiple languages
    - Automated tests for language switching and display

- **Implementation Phases:**
  - **Phase 1 (2 months):** *In Progress*
    - ✅ Base framework setup and configuration
    - ✅ German and English language support
    - ✅ Static UI element translation
    - 🚧 URL-based language switching (experiencing 404 errors)
    - 🚧 Language selection in user preferences
  - **Phase 2 (2 months):**
    - Dynamic content translation in product module
    - Translation of reporting and dashboard interfaces
    - Client-side JavaScript translation
    - Expanded language files to cover all modules
    - Language-specific import/export formats
  - **Phase 3 (ongoing):**
    - Support for additional languages as needed
    - Translation memory and terminology management
    - Advanced translation workflow integration
    - RTL language support if required

- **Integration Points:**
  - **Product Management:**
    - Multilingual product descriptions, names, and attributes
    - Language-specific product display in catalogs and detail views
    - Translation inheritance from parent to variant products
  - **Sales & Marketing:**
    - Multilingual sales documents (quotes, invoices)
    - Language-specific pricing information
    - Customer communications in preferred language
  - **Reporting & Analytics:**
    - Language-specific report generation
    - Localized data visualization
    - Multilingual dashboard interfaces
  - **User Administration:**
    - Language preference in user profiles
    - Role-based language defaults
    - Language-specific permissions if needed

- **Testing & Quality Assurance:**
  - **Localization Testing:**
    - Interface verification in all supported languages
    - Layout testing for text expansion/contraction
    - Character encoding and special character handling
    - Date, time, and number format validation
  - **Automated Tests:**
    - Language switching tests
    - Translation coverage verification
    - Missing translation detection
    - Visual regression testing for all languages
  - **Performance Testing:**
    - Language switching performance
    - Translation loading and caching efficiency
    - Impact of multiple language support on system resources

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

## 8. User Stories

### 8.1 User and Roles Management

#### 8.1.1 User Management

1. **User Registration**
   ```
   As an administrator,
   I want to create new user accounts with basic profile information,
   So that staff members can access the system with appropriate permissions.
   ```
   - Acceptance Criteria:
     - Administrators can create users with username, password, name, email, department
     - System enforces password complexity requirements
     - New users receive email with account information and temporary password
     - Administrators can specify initial roles during user creation
     - User status is set to "Pending Activation" until first login

2. **User Self-Registration**
   ```
   As a new staff member,
   I want to self-register for an account,
   So that I can request access to the ERP system.
   ```
   - Acceptance Criteria:
     - Registration form captures basic user information
     - Registration requires email verification
     - New accounts require administrator approval
     - System notifies administrators of pending registrations
     - Users receive notification when account is approved

3. **User Profile Management**
   ```
   As a user,
   I want to manage my profile information,
   So that my contact details and preferences are up-to-date.
   ```
   - Acceptance Criteria:
     - Users can update name, email, phone, and other contact details
     - Users can set UI preferences and language settings
     - Users can upload a profile photo
     - Changes to critical fields require re-authentication
     - Profile history is maintained for audit purposes

4. **Password Management**
   ```
   As a user,
   I want to manage my password securely,
   So that I can maintain access to my account while ensuring security.
   ```
   - Acceptance Criteria:
     - Users can change their password after authentication
     - System enforces password complexity rules
     - System prevents reuse of recent passwords
     - Password reset process uses secure email verification
     - Temporary passwords expire after first use or 24 hours

5. **User Deactivation**
   ```
   As an administrator,
   I want to deactivate user accounts,
   So that former employees cannot access the system.
   ```
   - Acceptance Criteria:
     - Administrators can deactivate accounts immediately
     - Deactivation terminates all active sessions
     - Deactivated users cannot log in
     - System maintains deactivated user records for audit purposes
     - Deactivation includes a reason and is logged for compliance

#### 8.1.2 Role Management

6. **Role Creation**
   ```
   As a system administrator,
   I want to create and define roles with specific permissions,
   So that I can assign standardized access levels to users.
   ```
   - Acceptance Criteria:
     - Create roles with unique names and descriptions
     - Define permission sets for each role
     - Set role hierarchy and inheritance
     - Include optional time restrictions for temporary roles
     - Provide role templates for common job functions

7. **Role Assignment**
   ```
   As an administrator,
   I want to assign roles to users,
   So that they have appropriate access based on their job responsibilities.
   ```
   - Acceptance Criteria:
     - Assign multiple roles to a single user
     - Set expiration dates for temporary role assignments
     - Require approval workflow for sensitive role assignments
     - Notify users when roles are assigned or changed
     - Maintain history of role assignments for audit

8. **Role-Based Access**
   ```
   As a department manager,
   I want access limited to data relevant to my department,
   So that I can focus on my area of responsibility while maintaining data privacy.
   ```
   - Acceptance Criteria:
     - Sales managers only see sales-related data
     - Production managers only see production-related data
     - Warehouse staff only see inventory-related data
     - Cross-functional roles provide limited access to multiple areas
     - System enforces data boundaries based on role

9. **Permission Review**
   ```
   As a compliance officer,
   I want to review user permissions and role assignments,
   So that I can ensure proper access controls are maintained.
   ```
   - Acceptance Criteria:
     - Generate reports of all users with specific roles
     - View comprehensive permission sets for any user
     - Identify users with conflicting role assignments
     - Schedule automated permission reviews
     - Flag potential segregation of duties violations

10. **Temporary Access Management**
    ```
    As a manager,
    I want to grant temporary elevated access to team members,
    So they can handle exceptional situations or cover for absent colleagues.
    ```
    - Acceptance Criteria:
      - Grant time-limited role assignments
      - Specify exact start and end dates/times
      - System automatically revokes access when expired
      - Require approval for extending temporary access
      - Log all actions performed under temporary access

#### 8.1.3 Authentication and Security

11. **Multi-Factor Authentication**
    ```
    As a security-conscious user,
    I want to enable multi-factor authentication for my account,
    So that my account remains secure even if my password is compromised.
    ```
    - Acceptance Criteria:
      - Support for email/SMS verification codes
      - Option for authenticator app integration
      - Remember trusted devices functionality
      - Bypass options for internal network access
      - Recovery process for lost MFA devices

12. **Session Management**
    ```
    As a user,
    I want to view and manage my active sessions,
    So that I can ensure no unauthorized access is occurring.
    ```
    - Acceptance Criteria:
      - List all active sessions with device/location information
      - Allow termination of individual sessions
      - Terminate all sessions except current one
      - Automatically expire inactive sessions
      - Alert on suspicious concurrent sessions

13. **Access Audit Trail**
    ```
    As a security administrator,
    I want to review comprehensive access logs,
    So that I can investigate security incidents and ensure compliance.
    ```
    - Acceptance Criteria:
      - Log all authentication attempts (successful and failed)
      - Record session details (IP, device, duration)
      - Track permission changes and role assignments
      - Filter and search audit logs by various criteria
      - Export audit logs for external analysis

14. **Secure API Access**
    ```
    As an integration developer,
    I want to obtain and manage API access tokens,
    So that external systems can securely interact with the ERP.
    ```
    - Acceptance Criteria:
      - Generate API tokens with specific permission scopes
      - Set expiration and usage limits for tokens
      - Revoke tokens immediately when needed
      - View token usage history and access patterns
      - Receive notifications for unusual API usage

15. **Login Monitoring**
    ```
    As a security administrator,
    I want to monitor login attempts,
    So that I can detect and respond to unauthorized access attempts.
    ```
    - Acceptance Criteria:
      - Track failed login attempts by username and IP
      - Implement account lockout after multiple failures
      - Alert on unusual login patterns or locations
      - Provide real-time monitoring dashboard
      - Generate periodic security reports

#### 8.1.4 User Experience

16. **Role-Based Interface**
    ```
    As a user,
    I want the UI to be tailored to my role,
    So that I only see relevant functionality and am not overwhelmed by options.
    ```
    - Acceptance Criteria:
      - Menu items filtered based on user permissions
      - Role-specific dashboards and home pages
      - Hide UI elements for unauthorized functions
      - Consistent presentation of access restrictions
      - Provide clear indicators of current access level

17. **Permission Request**
    ```
    As a user,
    I want to request additional permissions or roles,
    So that I can access functionality needed for my job.
    ```
    - Acceptance Criteria:
      - Submit request with business justification
      - Route requests to appropriate approvers
      - Track request status and history
      - Receive notification upon approval/denial
      - Implement temporary access if urgently needed

18. **User Directory**
    ```
    As a user,
    I want to view a directory of system users and their roles,
    So that I can find the right person to contact for specific functions.
    ```
    - Acceptance Criteria:
      - List users with basic contact information
      - Filter users by department, role, or location
      - Show user status (active, away, inactive)
      - Respect privacy settings and information visibility
      - Provide search functionality

19. **Permission Explanation**
    ```
    As a user,
    I want to understand why I can't access certain functionality,
    So that I can request appropriate permissions if needed.
    ```
    - Acceptance Criteria:
      - Show informative messages when access is denied
      - Explain which permission or role is required
      - Provide option to request access directly from error message
      - Log access denial events for pattern analysis
      - Maintain consistent messaging across the application

20. **User Onboarding**
    ```
    As a new user,
    I want a guided introduction to my available features,
    So that I can quickly become productive with the system.
    ```
    - Acceptance Criteria:
      - Role-specific welcome screens and tutorials
      - Interactive guide to available functions
      - Highlight key features based on assigned roles
      - Optional training modules for complex functionality
      - Check-in notifications after initial period

#### 8.1.5 Implementation Tasks and Prioritization

The following implementation plan outlines the tasks and their priorities for building the user and roles system:

**Phase 1 (MVP) - High Priority**
1. Create a dedicated `users` Django app
2. Implement extended User model with profile fields
   - Department/location fields
   - Status field (active, inactive, pending)
   - Contact information
3. Create basic user management views
   - User creation form
   - User list view with filtering
   - User detail/edit view
4. Implement core roles using Django's Group model
   - Define initial set of functional roles
   - Create permissions for core modules
   - Map views and actions to permissions
5. Build role management interface
   - Role creation and editing
   - Permission assignment to roles
   - User-role assignment
6. Enhance authentication features
   - Customized login/logout views
   - Password reset functionality
   - Account activation workflow
7. Implement basic audit logging
   - Authentication event logging
   - Critical model change tracking
   - User action history

**Phase 2 (Enhanced) - Medium Priority**
1. Add advanced role features
   - Role hierarchy and inheritance
   - Time-limited role assignments
   - Department-based access control
2. Implement permission request workflow
   - Request form with justification
   - Approval routing
   - Email notifications
3. Build user self-service features
   - Profile management
   - Password change with history
   - Session management
4. Enhance security controls
   - Failed login monitoring
   - Account lockout mechanism
   - IP-based access restrictions
5. Create administration dashboards
   - User activity monitoring
   - Permission audit reports
   - Security event visualization
6. Implement dynamic UI adaptation
   - Permission-based menu filtering
   - Role-specific dashboards
   - Access-denied handling

**Phase 3 (Advanced) - Low Priority**
1. Add multi-factor authentication
   - Email/SMS verification
   - Authenticator app integration
   - Trusted device management
2. Implement advanced audit features
   - Comprehensive audit trail
   - Data access logging
   - Audit report generation
3. Segregation of duties enforcement
   - Conflict detection
   - Approval workflows for conflicting actions
   - Compliance reporting
4. LDAP/Active Directory integration
   - User synchronization
   - Group mapping
   - Single sign-on
5. Advanced API authentication
   - Scoped API tokens
   - Usage analytics
   - Rate limiting and security features

**Development Approach**
- Leverage Django's built-in authentication system as the foundation
- Use Django's permission and group models, extending as needed
- Create a custom middleware for advanced permission checking
- Implement a decorator-based approach for function-level permissions
- Build on Django Rest Framework for API authentication needs
- Use signals for audit logging to minimize code duplication

### 4.8 Legacy API Integration

#### 4.8.1 Overview

The system currently uses an external Python package (WSZ_api) to interact with the legacy 4D-based ERP system. This package is imported from an external location and has several drawbacks:

- External dependency on code not included in the project repository
- Hardcoded file paths that are environment-specific
- Session management issues
- Limited error handling and logging
- No test coverage

This section outlines the plan to replace the WSZ_api with a properly implemented internal module.

#### 4.8.2 Current Architecture

The external WSZ_api package provides the following key functionalities:

- **Authentication and session management:** 
  - Obtains and stores session cookies in a configuration file
  - Validates and refreshes sessions when needed
  - Maintains configuration for test and live environments

- **Data retrieval:**
  - Fetches data from tables via the legacy 4D REST API
  - Handles pagination and data transformation

- **Data updates:**
  - Pushes field updates to specific records in the legacy system

The current implementation has these main components:
- `auth.py`: Handles session management, cookie storage and retrieval
- `getTable.py`: Fetches data from tables

#### 4.8.3 Key Findings on Legacy API Behavior

Through extensive development and debugging of our replacement direct API integration, we have gained significant insights into how the legacy 4D API operates:

1. **Session Management Complexity**:
   - The API uses the `WASID4D` cookie as the primary session identifier
   - A secondary cookie `4DSID_WSZ-DB` is sometimes used in responses
   - The server enforces a maximum number of concurrent sessions per user/IP
   - Exceeding session limits results in 402 errors with "Maximum number of sessions reached" message
   - Attempting to implement explicit logout functionality causes issues with session management
   - Cookie duplication (multiple `WASID4D` cookies) causes authentication failures

2. **Response Format Variations**:
   - The API can return data in three different formats:
     - Standard OData format with a `value` array
     - 4D-specific format with `__ENTITIES` array and `__COUNT` field for pagination
     - Direct array of records in some cases
   - Integration code must handle all these response formats

3. **Error Handling Requirements**:
   - Session errors require automatic retry with fresh authentication
   - Robust logging is essential for troubleshooting session-related issues
   - Connection errors should be handled with appropriate backoff strategies

#### 4.8.4 Best Practices for Legacy API Integration

Based on our findings, the following best practices should be followed:

1. **Session Management Strategy**:
   - Maintain a single persistent session across script executions
   - Clear all existing cookies before setting the current session cookie
   - Use exactly one `WASID4D` cookie per request
   - Validate sessions before use and reestablish when necessary
   - Do not attempt to explicitly log out; instead, reuse sessions until they expire naturally

2. **Robust Pagination Implementation**:
   - Always use pagination for large data sets (using `$top` and `$skip` parameters)
   - Handle end-of-data detection reliably (fewer records than requested)
   - Use the `__COUNT` field when available to optimize pagination

3. **Response Processing**:
   - Implement defensive code to handle all possible response formats
   - Verify response structure before attempting to extract data
   - Log response structure for debugging purposes

These findings have been documented in detail in [docs/legacy_erp/api/direct_api_integration.md](../docs/legacy_erp/api/direct_api_integration.md) and implemented in our internal `direct_api` module, which now serves as a reference implementation for all legacy system integrations.

### 4.6.4 Legacy ERP Direct API Integration

#### Current Status: ⚠️ *Critical Issues*

- **Direct API Implementation Assessment:**
  - **Session Management Issues:** ❌ *Not Working*
    - The current `direct_api` implementation fails to maintain a single session
    - The implementation is incorrectly creating multiple new sessions when only ONE session should ever exist
    - Each script execution/API call creates a new session instead of reusing the existing one
    - This leads to rapid session proliferation and depletion of available server sessions
    - The 402 error (Too Many Sessions) should never even be encountered if session management worked properly
    - The system becomes completely clogged with sessions, making it unusable
  
  - **Comparison with Working Implementation:**
    - The original `getTable.py` script works correctly by maintaining exactly one session
    - The `direct_api` reimplementation (`getTable_direct_api.py`) fundamentally fails to maintain session discipline
    - The original implementation never hits 402 errors because it properly reuses the same session
  
  - **Technical Analysis:**
    - Despite code appearing to implement session management, it fails to maintain a single persistent session
    - Each component/call path appears to be creating its own session rather than sharing a global one
    - Cookie/session handling mechanism is incorrectly implementing the "exactly one session" requirement
    - Global session objects are not being properly shared/accessed between components
    - Debug mode confirms that new sessions are created for each operation

- **Impact:**
  - Direct API module cannot be used in production
  - Testing on live systems causes server overload with sessions
  - Risk of session depletion affecting other critical systems
  - Blocking issue for any functionality depending on direct API access

- **Remediation Plan:**
  - *High Priority*
    - Revert to using original `getTable.py` script for immediate needs
    - Conduct comprehensive review to identify all session creation code paths
    - Redesign session management to ensure exactly ONE session is maintained globally
    - Implement proper singleton pattern for session management
    - Add detailed session tracking logs to identify all session creation points
  
  - *Medium Priority*
    - Refactor authentication module to use true singleton session instance
    - Verify all API call paths use the same session object
    - Create automated tests specifically for session reuse verification
  
  - *Low Priority*
    - Update documentation to emphasize the "single session" requirement
    - Create monitoring tools for session tracking
    - Add explicit warnings in code where new sessions might be created

- **Lessons Learned:**
  - Critical importance of true singleton session management when working with legacy APIs
  - Need for comprehensive testing of session creation/reuse logic
  - Importance of validating API client behavior with minimal test cases before scaling
  - Value of preserving working implementations for reference

#### Implementation Dependencies

The following modules depend on proper direct API functionality:
- Data migration from legacy system
- Live data synchronization
- Inventory updates
- Product data enrichment

Until the direct API issues are resolved, alternative approaches using the original scripts will be maintained.

### 4.1.2 Legacy API Integration and Filtering

- **Legacy ERP API Connection:**
  - Establish reliable connections to the legacy 4D-based ERP system via REST API. ✅ *Implemented*
  - Implement robust session management to prevent session duplication and server overload. ✅ *Implemented*
  - Support for multiple environments (test, live) with configurable endpoints. ✅ *Implemented*
  - Secure credential management for API authentication. ✅ *Implemented*

- **Data Retrieval and Filtering:**
  - Support for OData-compatible filtering syntax for querying legacy data. ✅ *Implemented*
  - Implement filter types including:
    - Equality filters (e.g., `Artikel_Nr = '115413'`) ✅ *Verified*
    - Text search with LIKE operator (e.g., `Bezeichnung LIKE '%Test%'`) ✅ *Verified*
    - Numeric comparisons (e.g., `Preis > 10`) ✅ *Verified*
    - Boolean filters (e.g., `aktiv = true`) ✅ *Verified*
    - Date filters (e.g., `CREATIONDATE >= '2023-01-01'`) ✅ *Verified*
    - Combined filters with AND/OR operators ✅ *Verified*
  - Graceful fallback when filters are not supported by specific tables. ✅ *Implemented*
  - Automatic retry without filters when filter-related errors occur. ✅ *Implemented*

- **Pagination and Performance:**
  - Support for paginated data retrieval to handle large datasets efficiently. ✅ *Implemented*
  - Configurable page size and skip parameters. ✅ *Implemented*
  - Option to fetch all records with automatic pagination handling. ✅ *Implemented*

- **Error Handling and Logging:**
  - Comprehensive error handling for connection, authentication, and data retrieval issues. ✅ *Implemented*
  - Detailed logging of API interactions for troubleshooting. ✅ *Implemented*
  - Specific handling for filter-related errors with appropriate fallback strategies. ✅ *Implemented*

- **Table Discovery:**
  - Ability to list available tables in the legacy system. ✅ *Implemented*
  - Support for exploring table structure and available fields. *Planned*
  - Documentation of common tables and their filtering capabilities. *In Progress*

### 4.9 External API Access

#### 4.9.1 Overview

The pyERP system will provide a comprehensive REST API to allow external applications to securely access and manipulate data. This API will enable third-party integrations, custom client applications, and automation tools to interact with the ERP system programmatically.

#### 4.9.2 Key Requirements

- **Authentication and Security:**
  - OAuth2/JWT token-based authentication for all API endpoints
  - Granular permission control with scoped API tokens
  - Rate limiting to prevent abuse
  - Comprehensive audit logging of all API access

- **API Design and Documentation:**
  - RESTful API design following industry best practices
  - OpenAPI/Swagger documentation for all endpoints
  - Versioned API to ensure backward compatibility
  - Consistent error handling and response formats

- **Data Access:**
  - Read access to core business entities (products, orders, inventory, etc.)
  - Write operations with proper validation and business rule enforcement
  - Bulk operations for efficient data transfer
  - Filtering, sorting, and pagination for all list endpoints

- **Performance and Reliability:**
  - Optimized query performance for API endpoints
  - Caching strategies for frequently accessed data
  - Graceful error handling with informative messages
  - Monitoring and alerting for API performance issues

#### 4.9.3 Implementation Approach

The external API will be built on top of Django REST Framework, leveraging its serialization, authentication, and viewset capabilities. The API will be organized into logical resource groups corresponding to the main business domains:

1. **Products API:**
   - Product catalog access
   - Product variants and attributes
   - Product images and media
   - Bill of Materials (BOM) data

2. **Sales API:**
   - Customer information
   - Quote and order management
   - Invoice and payment data
   - Sales reporting

3. **Inventory API:**
   - Stock levels and availability
   - Warehouse and location data
   - Stock movements and transfers
   - Inventory adjustments

4. **Production API:**
   - Manufacturing orders
   - Production schedules
   - Resource allocation
   - Production reporting

#### 4.9.4 API Management

The API will include management features to ensure security, reliability, and usability:

- **Developer Portal:**
  - Self-service API key generation
  - Interactive API documentation
  - Usage statistics and monitoring
  - Sample code and integration guides

- **Administration:**
  - API key management and revocation
  - Usage quotas and rate limits
  - Access control and permissions
  - Audit logging and security monitoring

#### 4.9.5 Integration Scenarios

The API will support various integration scenarios, including:

1. **E-commerce Integration:**
   - Product catalog synchronization
   - Order creation and fulfillment
   - Inventory availability checks
   - Customer data synchronization

2. **Mobile Applications:**
   - Field sales applications
   - Warehouse management apps
   - Executive dashboards
   - Customer self-service portals

3. **Business Intelligence:**
   - Data extraction for reporting
   - Real-time dashboards
   - Historical data analysis
   - KPI monitoring

4. **Automation and Workflow:**
   - Automated order processing
   - Integration with external systems
   - Scheduled data synchronization
   - Event-driven processes

## Project Updates

### Testing and Quality Assurance Progress (March 2024)

As part of our ongoing effort to improve code quality and reliability, we've made significant progress in enhancing test coverage for critical components:

- Increased test coverage for the product validation module from 9% to 59%
- Implemented new testing approaches for dealing with circular import dependencies
- Developed strategies for testing Django translation-enabled code
- Created comprehensive test suites for product model validation logic

These improvements align with our quality assurance strategy and support our goal of maintaining high code quality while enabling fast, reliable development of new features.

### 4.7 System Monitoring & Administration

- **Status Dashboard:** ✅ *Implemented*
  - Create an admin view dashboard for monitoring critical system connections and components. ✅ *Implemented*
  - Real-time status indicators for database connection health. ✅ *Implemented*
  - Connection status monitoring for legacy ERP system integration. ✅ *Implemented*
  - Status monitoring for pictures API connection. ✅ *Implemented*
  - Expandable framework to add monitoring for other critical system components. ✅ *Implemented*
  - Historical uptime logging and basic analytics. ✅ *Implemented*
  
- **Alerting & Notifications:** ✅ *Implemented*
  - Visual indicators for connection issues within the admin interface. ✅ *Implemented*
  - Optional email notifications for system administrators on connection failures. *Planned*
  - Error logging with detailed diagnostics for troubleshooting. ✅ *Implemented*
  
- **Health Checks:** ✅ *Implemented*
  - Periodic automated health checks for all monitored systems. ✅ *Implemented*
  - Manual refresh option for on-demand status updates. ✅ *Implemented*
  - Performance metrics for key integrations (response times, error rates). ✅ *Implemented*
  
- **Administration Actions:** ✅ *Partially Implemented*
  - Quick access to restart/reset problematic connections. *Planned*
  - Ability to configure monitoring thresholds and alert preferences. *Planned*
  - Detailed logs for all connection events and issues. ✅ *Implemented*

#### 4.7.1 Monitoring Implementation ✅ *Implemented*

- **Technology Stack:**
  - Django app-based implementation with custom admin views ✅ *Implemented*
  - Database-backed health check result storage for historical tracking ✅ *Implemented*
  - Responsive UI with real-time status updates via AJAX ✅ *Implemented*
  
- **Component Monitoring:**
  - **Database Connection:** Direct testing of database connectivity with error detection ✅ *Implemented*
  - **Legacy ERP API:** Connection and authentication verification with the 4D-based system ✅ *Implemented*
  - **Pictures API:** Endpoint availability and authentication testing ✅ *Implemented*
  
- **Access Methods:**
  - Admin interface dashboard for visual monitoring ✅ *Implemented*
  - REST API endpoint for external monitoring tools integration ✅ *Implemented*
  - Management command for CLI and cron job execution ✅ *Implemented*
  - JSON output support for programmatic processing ✅ *Implemented*
  
- **Auto-Refresh Functionality:**
  - Configurable refresh period (default: 5 minutes) ✅ *Implemented*
  - On-demand manual refresh with visual feedback ✅ *Implemented*
  - Asyncronous updates to prevent UI blocking ✅ *Implemented*
  
- **Extensibility:** ✅ *Implemented*
  - Modular design allowing for easy addition of new components to monitor ✅ *Implemented*
  - Standardized health check interface for consistent implementation ✅ *Implemented*
  - Pluggable notification system for future extension ✅ *Implemented*

#### 4.7.2 Frontend Modernization with Vue.js *In Progress*

- **Technology Stack Updates:**
  - Vue.js 3.5 with Composition API for frontend components ✅ *Implemented*
  - Vite for build tooling and development server ✅ *Implemented*
  - TypeScript for enhanced type safety and developer experience ✅ *Implemented*
  - Tailwind CSS for consistent styling and rapid development *Planned*
  
- **Integration Strategy:**
  - **Phase 1: Initial Setup and Infrastructure** ✅ *Implemented*
    - Setup Vue.js project structure within Django ✅ *Implemented*
    - Configure build pipeline and asset management ✅ *Implemented*
    - Establish API endpoints for Vue.js components ✅ *Implemented*
    - Create development environment with hot-reload ✅ *Implemented*
    
  - **Phase 2: Component Migration** ✅ *In Progress*
    - Identify and prioritize components for migration ✅ *Implemented*
    - Create reusable Vue.js component library ✅ *Partially Implemented*
    - Implement Vue Router for navigation between views ✅ *Implemented*
    - Implement API service with Axios for backend communication ✅ *Implemented*
    - Migrate Product module views to Vue.js components ✅ *Implemented*
    - Migrate Sales module views to Vue.js components ✅ *In Progress*
    - Implement state management with Pinia *Planned*
    - Develop component testing strategy *Planned*
    
  - **Phase 3: Feature Implementation** *Planned*
    - Real-time updates using WebSocket integration
    - Enhanced UI/UX with modern component design
    - Client-side caching and performance optimization
    - Offline support for critical features
    
- **Key Features:**
  - **Component Architecture:**
    - Modular, reusable components ✅ *Implemented*
    - Shared component library ✅ *Partially Implemented*
    - Type-safe component props and events ✅ *Implemented*
    
  - **State Management:**
    - Centralized state with Pinia ✅ *Implemented*
    - Real-time state synchronization *Planned*
    - Optimistic UI updates *Planned*
    
  - **Performance Optimizations:**
    - Code splitting and lazy loading ✅ *Implemented*
    - Asset optimization and caching *Planned*
    - Server-side rendering where beneficial *Planned*
    
  - **Developer Experience:**
    - Hot module replacement ✅ *Implemented*
    - TypeScript integration ✅ *Implemented*
    - Component development environment ✅ *Implemented*
    - Comprehensive testing utilities *Planned*

- **Migration Approach:**
  - Gradual migration of existing features ✅ *In Progress*
  - Parallel operation of Django templates and Vue.js ✅ *Implemented*
  - Comprehensive documentation of authentication implementation ✅ *Implemented*
  - Technical documentation in docs/vue_auth_implementation.md ✅ *Implemented*
  - Feature flags for controlled rollout *Planned*
  - Comprehensive testing strategy for each migrated component *Planned*

- **Migrated Components:**
  - **Authentication Module:** ✅ *Implemented*
    - JWT-based authentication with Django backend ✅ *Implemented*
    - Login and logout functionality ✅ *Implemented*
    - User profile management ✅ *Implemented*
    - Password change functionality ✅ *Implemented*
    - Protected routes with navigation guards ✅ *Implemented*
    - Automatic token refresh ✅ *Implemented*
    - Centralized auth state management with Pinia ✅ *Implemented*
    - Technical documentation in docs/vue_auth_implementation.md ✅ *Implemented*

  - **Product Module:** ✅ *Implemented*
    - Product List view with search and filtering ✅ *Implemented*
    - Product Detail view with image gallery ✅ *Implemented*
    - Variant Detail view with pricing and inventory information ✅ *Implemented*
    - Category List view for product categorization ✅ *Implemented*
    - Responsive layouts with improved UX ✅ *Implemented*
    - Loading states and error handling ✅ *Implemented*
  
  - **Sales Module:** ✅ *In Progress*
    - Sales Order List view with search, filtering, and pagination ✅ *Implemented*
    - Sales Order Detail view with comprehensive order information ✅ *Implemented*
    - Status indicators with color coding for different order states ✅ *Implemented*
    - TypeScript interfaces for sales-related data structures ✅ *Implemented*
    - Order editing and creation interface *Planned*
    - Customer management interface *Planned*
    - Invoice generation and printing functionality *Planned*

### 4.7 Vue.js Frontend Integration

- **Vue.js 3.5 Integration:** 
  - Modern frontend framework integration with Django backend. ✅ *Implemented*
  - Project structure setup with Vue.js best practices. ✅ *Implemented*
  - TypeScript integration for type safety and improved developer experience. ✅ *Implemented*
  - Development environment with Vite for fast hot module replacement. ✅ *Implemented*
  - Docker container configuration for Vue.js development server. ✅ *Implemented*
  - Basic integration with Django templates via the `vue_base.html` template. ✅ *Implemented*
- **Development Infrastructure:**
  - Docker container setup for Vue.js development. ✅ *Implemented*
  - Configuration of Docker services in docker-compose.yml. ✅ *Implemented*
  - Supervisord integration for managing Vue.js development server. ✅ *Implemented*
  - Environment-specific configurations (development vs. production). ✅ *Implemented*
- **Core Application Setup:**
  - Basic Vue.js application with App.vue and sample component. ✅ *Implemented*
  - Integration of Tailwind CSS for styling. ✅ *Configured*
  - Entry point (index.html) and application mounting. ✅ *Implemented*
  - TypeScript configuration for Vue.js components. ✅ *Implemented*
- **Authentication & Security:**
  - JWT-based authentication with Django backend. ✅ *Implemented*
  - Secure token storage and management. ✅ *Implemented*
  - Automatic token refresh for seamless user experience. ✅ *Implemented*
  - Protected routes with navigation guards. ✅ *Implemented*
  - Role-based access control (admin vs. regular users). ✅ *Implemented*
  - User profile management with form validation. ✅ *Implemented*
  - Password change functionality. ✅ *Implemented*
  - Centralized authentication state with Pinia. ✅ *Implemented*
  - Comprehensive technical documentation. ✅ *Implemented*
- **State Management:**
  - Pinia store implementation for authentication. ✅ *Implemented*
  - TypeScript interfaces for type-safe state. ✅ *Implemented*
  - Modular store design for scalability. ✅ *Implemented*
  - Computed properties for derived state. ✅ *Implemented*
- **Module Migration Progress:**
  - Product module fully migrated to Vue.js components. ✅ *Implemented*
  - Sales module partially migrated with order listing and details. ✅ *In Progress*
  - TypeScript interfaces for data structures. ✅ *Implemented*
  - Responsive layouts and improved UX. ✅ *Implemented*
- **Upcoming Tasks:**
  - Complete Sales module migration with order editing and customer management. *Planned*
  - Component migration strategy implementation. *Planned*
  - Expand state management with Pinia to other modules. *Planned*
  - Testing infrastructure with Jest. *Planned*
  - API integration patterns for Django backend communication. *Planned*
  - Comprehensive UI component library. *Planned*
