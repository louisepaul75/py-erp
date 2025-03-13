# Story: PYERP-INVENTORY - Inventory and Warehouse Management Module

## Description
As an inventory manager
I want to track products across warehouse storage locations using a box and slot system
So that I can efficiently manage inventory, locate products, and optimize warehouse space

## Background
The current legacy ERP system has a basic inventory system (Stamm_Lagerorte table) with location data but lacks the flexibility and features needed for modern warehouse management. We need to create an improved inventory management system that:

1. Syncs with legacy data but enhances the data model
2. Organizes products into boxes with multiple slots
3. Places boxes in storage locations (unit/compartment/shelf)
4. Provides better tracking and management capabilities
5. Supports inventory reservations
6. Facilitates picking for orders

Legacy data in Stamm_Lagerorte includes: Country, city_building, sale (if products in this spot are sold), special spot, unit, compartment, shelf.

The current structure is somewhat messy, and we need to improve it while maintaining the ability to sync with the old system.

## Legacy Data Analysis
After examining the Stamm_Lagerorte table data (923 records) and analyzing the complete database schema, we have a clearer understanding of the legacy storage location structure:

### Database Schema Overview
The legacy inventory system consists of several interconnected tables:

1. **Artikel_Stamm** - Product/article master table
2. **Stamm_Lagerorte** - Storage location master table
3. **Artikel_Lagerorte** - Junction table linking products to storage locations
4. **Stamm_Lager_Schuetten** - Box/container master table
5. **Stamm_Lager_Schuetten_Slots** - Slots within boxes/containers
6. **Historie_Stamm_Lager_Schuetten** - History table for boxes
7. **Lager_Schuetten** - Current box inventory table
8. **Lager_Schuetten_Einheiten** - Units stored in boxes

This structure reveals a more complex box and slot system than initially understood, with dedicated tables for box types, slots, and their relationships. The system also includes history tracking for boxes and specific tables for managing box units.

### Key Fields in Stamm_Lagerorte
- **Location Hierarchy**:
  - `Land_LKZ`: Country code (e.g., "DE" for Germany)
  - `Ort_Gebaeude`: City/Building (e.g., "Hamburg-Markt", "Stammlager-Diessen")
  - `Regal`: Unit/Shelf number (numeric values like 1, 4, 26, etc.)
  - `Fach`: Compartment number (typically 1-3)
  - `Boden`: Shelf level (typically 1-5)
  - `Schuette`: Appears to be a chute or slot identifier (often null)
  - `Lagerort`: Formatted location string (e.g., "DE-Hamburg-Markt-R04-F02-B02")

- **Status Indicators**:
  - `Abverkauf`: Boolean indicating if products in this location are for sale
  - `Sonderlager`: Boolean indicating if it's a special storage location

- **Metadata**:
  - `ID_Lagerort`: Numeric ID for the storage location (primary key)
  - Creation and modification tracking fields (name, date, time)

- **Unused Fields**:
  - `X`, `Y`, `Z`: Coordinate fields (all zeros in current data)
  - `Packed`: Boolean field (all False in current data)
  - `Attribut`: Additional attributes (all None in current data)

### Data Mapping Strategy
For the new system, we map these legacy fields to our new data models as follows:

1. **StorageLocation Model**:
   - `legacy_id` ← `ID_Lagerort` (used as the primary identifier for synchronization)
   - `location_code` ← `Lagerort` (formatted location string)
   - `country` ← `Land_LKZ`
   - `city_building` ← `Ort_Gebaeude`
   - `unit` ← `Regal`
   - `compartment` ← `Fach`
   - `shelf` ← `Boden`
   - `sale` ← `Abverkauf`
   - `special_spot` ← `Sonderlager`
   - `name` ← Generated from components (combination of country, city_building, unit, compartment, shelf)

2. **Box and BoxSlot Models**:
   - These are not entirely new concepts but rather refinements of existing structures in the legacy system
   - The legacy system has dedicated tables for boxes (Stamm_Lager_Schuetten) and slots (Stamm_Lager_Schuetten_Slots)
   - Our new models will enhance these concepts with improved relationships and additional functionality
   - Boxes will be assigned to StorageLocations, similar to the legacy system
   - Each Box will contain multiple BoxSlots based on BoxType configuration, maintaining the existing slot concept
   - We'll incorporate data from the legacy Stamm_Lager_Schuetten and Stamm_Lager_Schuetten_Slots tables during synchronization

### BoxType Configuration Details
Based on our analysis of the legacy ERP parameters table, we have identified the following configuration options for BoxTypes:

1. **Box Types (Schüttentypen)**:
   After analyzing the data from the parameter table, we found 42 different box types with detailed specifications. The key attributes include:

   - **Dimensions**:
     - Length (Box_Länge): Ranges from 160mm to 792mm
     - Width (Box_Breite): Ranges from 85mm to 593mm
     - Height (Box_Höhe): Ranges from 80mm to 450mm

   - **Weight Properties**:
     - Empty Weight (Box_Gewicht): Ranges from 101g to 7800g
     - Divider Weight (Trenner_Gewicht): Mostly 0g, with one box having 250g

   - **Slot Configuration**:
     - Most boxes have a single slot
     - Some models (e.g., Schäfer LF 532) have 3 slots

   - **Manufacturers**:
     - Schäfer (most common)
     - Bito
     - Auer
     - Visus
     - Walther
     - Kennoset
     - Arca Systems

   - **Notable Box Types**:
     - Largest: "Lager grau XXL" (792 x 593 x 450 mm, 7800g)
     - Smallest: "Schäfer 2" series (160 x 105 x 80 mm, 101g)
     - Multi-slot: "Schäfer LF 532" series (3 slots)

2. **Box Colors (Schüttenfarben)**:
   From the box type data, we identified the following colors in use:
   - Blau (Blue) - 11 box types
   - Gelb (Yellow) - 5 box types
   - Grün (Green) - 5 box types
   - Rot (Red) - 4 box types
   - Grau (Gray) - 4 box types
   - Other/Unspecified - 13 box types

   Additional colors mentioned in the parameters but not found in the current box types:
   - Orange
   - Schwarz (Black)
   - Transparent
   - Weiß (White)

3. **Box Purposes (Schüttenzweck)**:
   - Lager (Storage)
   - Picken (Picking)
   - Transport
   - Werkstatt (Workshop)

### BoxType Data Mapping
Based on our analysis, we will map the legacy data to our BoxType model as follows:

- **name**: Derived from the Type field (e.g., "14/6-2H Blau", "EF6220 Grau")
- **colour**: Extracted from the Type name (e.g., "Blau", "Gelb", "Grün")
- **length**: Mapped directly from Box_Länge
- **width**: Mapped directly from Box_Breite
- **height**: Mapped directly from Box_Höhe
- **weight_empty**: Mapped directly from Box_Gewicht
- **default_slot_count**: Mapped directly from Slots
- **divider_weight**: Mapped directly from Trenner_Gewicht
- **purpose**: Will be assigned based on box characteristics or additional data
- **UUID**: Will be generated for new records (not present in legacy data)

These configuration options will be used to define the BoxType model, which will include attributes for type, color, purpose, dimensions, weight capacity, and slot configuration. The BoxType model will serve as a template for creating Box instances, which will be placed in StorageLocations and contain multiple BoxSlots for storing products.

### Box Data Structure Analysis
After examining the `Stamm_Lager_Schuetten` table data, we have identified the following structure:

1. **Core Fields**:
   - `ID`: Primary key for the box record (numeric)
   - `max_Anzahl_Slots`: Maximum number of slots in the box (typically 1 in current data)

2. **Box Information** (stored in the `data_` JSON field):
   - `Schuettentype`: References the box type (e.g., 'Schäfer-500x312')
   - `Anzahl_Schuetteneinheiten`: Number of box units
   - `Schuettenzweck`: Purpose of the box (e.g., 'Lager' for storage)

3. **Audit Information**:
   - Creation tracking:
     - `created_name`: User who created the record
     - `created_date`: Date of creation
     - `created_time`: Time of creation
   - Modification tracking:
     - `modified_name`: User who last modified the record
     - `modified_date`: Date of last modification
     - `modified_time`: Time of last modification
   - System timestamps:
     - `__TIMESTAMP`: Last modification timestamp
     - `__STAMP`: Version or sequence number

4. **Related Data** (stored as deferred references):
   - `Relation_93`: Links to `Lager_Schuetten` table for current box inventory
   - `viele_schuetten`: Links to child box records in a hierarchical structure

5. **Additional Fields**:
   - `Druckdatum`: Print date (format: DD!MM!YY)
   - `Druckzeit`: Print time

### Box Data Mapping Strategy
Based on the analysis, we will map these legacy fields to our new data models as follows:

1. **Box Model**:
   - `legacy_id` ← `ID` (used for synchronization)
   - `box_type` ← Foreign key to BoxType, determined by `data_.Schuettentype`
   - `purpose` ← `data_.Schuettenzweck` (moved from BoxType as per previous decision)
   - `unit_count` ← `data_.Anzahl_Schuetteneinheiten`
   - `max_slots` ← `max_Anzahl_Slots`
   - `last_labelprint_date` ← `Druckdatum` (direct field, format: DD!MM!YY)
   - `last_labelprint_time` ← `Druckzeit` (direct field)
   - `status` ← Current operational status of the box
   - `parent_box` ← Self-referential foreign key (based on viele_schuetten relationship)
   - Standard audit fields will be maintained by Django

2. **BoxSlot Model**:
   - Despite the legacy system typically using single slots (`max_Anzahl_Slots=1`), our new system will support multiple slots per box
   - Slot numbers will be generated based on the BoxType configuration
   - Legacy slot data will be mapped to slot number 1 in cases where `max_Anzahl_Slots=1`

3. **Inventory Tracking**:
   - The `Relation_93` reference to `Lager_Schuetten` will be used to synchronize current inventory data
   - This will be mapped to our ProductStorage model for tracking contents

4. **Box Hierarchy**:
   - The `viele_schuetten` relationship suggests a hierarchical structure in the legacy system
   - We will implement a self-referential relationship in our Box model to maintain this hierarchy
   - This will be useful for tracking box groupings or nested storage scenarios

### Implementation Notes for Box Synchronization:
1. The `data_` field contains crucial information in JSON format that must be parsed during synchronization
2. Box types must be synchronized before boxes to maintain referential integrity
3. The legacy system's single-slot approach will need to be expanded to support our multi-slot design
4. Box hierarchy relationships should be maintained through the synchronization process
5. Inventory data synchronization should be handled as a separate step after box synchronization

### Box Slot Data Structure Analysis
After examining the `Stamm_Lager_Schuetten_Slots` table data, we have identified the following structure:

1. **Primary Identifiers**:
   - `ID`: Numeric identifier for the slot record
   - `ID_Lager_Schuetten_Slots`: Unique identifier for the slot in the system
   - `Lfd_Nr`: Sequential number representing the slot number within a box (typically 1 in current data, suggesting most boxes have a single slot)

2. **Slot Information** (stored in the `data_` JSON field):
   - `Slot_Code`: A two-letter code for the slot (e.g., 'BP', 'ZB', 'FG', 'KI', 'GY')
   - `Einheiten_Nr`: Unit number within the slot (typically 1)
   - `Einheitenfabe`: Appears to be a color code or identifier (numeric value)

3. **Audit Information**:
   - Creation tracking:
     - `created_name`: User who created the record
     - `created_date`: Date of creation
     - `created_time`: Time of creation (numeric format)
   - Modification tracking:
     - `modified_name`: User who last modified the record
     - `modified_date`: Date of last modification
     - `modified_time`: Time of last modification
   - System timestamps:
     - `__TIMESTAMP`: Last modification timestamp
     - `__STAMP`: Version or sequence number

4. **Related Data**:
   - `viele_zu_eins`: Reference to the parent box in the `Stamm_Lager_Schuetten` table
   - `picking_data_`: Additional data for picking operations (typically null)
   - `Auftrags_Nr`: Order number (typically 0 when not associated with an order)

### Box Slot Data Mapping Strategy
Based on the analysis, we will map these legacy fields to our new data models as follows:

1. **BoxSlot Model**:
   - `legacy_id` ← `ID` (used for synchronization)
   - `legacy_slot_id` ← `ID_Lager_Schuetten_Slots` (unique identifier from legacy system)
   - `box` ← Foreign key to Box, determined by `ID_Lager_Schuetten_Slots` which matches the box ID in the `Stamm_Lager_Schuetten` table
   - `slot_number` ← `Lfd_Nr` (sequential number within the box)
   - `slot_code` ← `data_.Slot_Code` (two-letter code)
   - `unit_number` ← `data_.Einheiten_Nr` (unit number within the slot)
   - `color_code` ← `data_.Einheitenfabe` (color identifier)
   - `order_number` ← `Auftrags_Nr` (associated order, if any)
   - `status` ← Derived from data (occupied, reserved, empty)
   - Standard audit fields will be maintained by Django

2. **Implementation Notes for BoxSlot Synchronization**:
   - The `data_` field contains crucial information in JSON format that must be parsed during synchronization
   - Box records must be synchronized before box slots to maintain referential integrity
   - The `ID_Lager_Schuetten_Slots` field is the key to linking slots to their parent boxes, not the `viele_zu_eins` reference
   - The `viele_zu_eins` reference provides additional validation but the primary relationship is through `ID_Lager_Schuetten_Slots`
   - Slot codes should be preserved for compatibility with legacy system
   - The `Einheitenfabe` field may need mapping to human-readable color names
   - Status should be derived based on associated inventory data

3. **BoxSlot Enhancements**:
   - Add barcode generation for each slot based on slot code and box identifier
   - Implement status tracking (empty, occupied, reserved)
   - Create relationships to ProductStorage records for inventory tracking
   - Add validation to ensure slot numbers are unique within a box
   - Implement history tracking for slot status changes

This detailed understanding of the slot data structure will enable us to properly implement the BoxSlot model and its synchronization with the legacy system, ensuring all relevant data is preserved while enhancing the functionality for modern warehouse management needs.

## Progress Update
We have made significant progress on the inventory management system:

1. **Data Models**: Created all required models for the inventory system including StorageLocation, BoxType, Box, BoxSlot, ProductStorage, and InventoryMovement.

2. **Foreign Key References**: Updated the ProductStorage and InventoryMovement models to reference the VariantProduct model using the SKU field for product identification.

3. **Sync Infrastructure**: Implemented the inventory sync using the existing ETL pipeline:
   - Created transformer classes in the sync directory for all inventory components
   - Created a YAML configuration file for inventory sync
   - Implemented setup and sync management commands
   - Integrated inventory sync with the run_all_sync command

4. **Legacy Data Integration**: Set up the synchronization with the Stamm_Lagerorte table to import storage location data.
   - Successfully synchronized all 923 storage location records from the legacy system
   - Implemented validation to handle duplicate storage locations
   - Added proper error handling for data integrity issues

5. **Migrations**: Successfully applied migrations to establish the database schema.

6. **Data Validation**: Implemented validation rules to ensure data integrity:
   - Enforced unique constraints on storage location fields (Country, City building, Unit, Compartment, Shelf)
   - Added proper error handling for duplicate records during synchronization

7. **Command-line Interface**: Enhanced management commands for inventory operations:
   - Added component-specific sync commands (e.g., `sync_inventory --component storage_locations`)
   - Implemented debug mode for detailed logging during synchronization
   - Provided summary statistics for sync operations

8. **BoxType Configuration**: Identified and documented the standard box types, colors, and purposes from the legacy ERP parameters table, which will be used to configure the BoxType model.
   - Analyzed 42 different box types with detailed specifications
   - Mapped legacy attributes to the new BoxType model
   - Identified common manufacturers and their product lines

9. **BoxType Synchronization**: Implemented the BoxType transformer to synchronize box types from the legacy system:
   - Created BoxTypeTransformer class to handle data transformation
   - Added proper unit conversion for dimensions (mm to cm) and weights (g to kg)
   - Implemented rounding to ensure decimal values meet database constraints
   - Added detailed descriptions including manufacturer, dimensions, and weights
   - Successfully synchronized 49 box types from the legacy system

10. **Box Purpose Management**: Improved the box purpose management:
    - Moved the purpose field from BoxType to Box model to match legacy system design
    - Created BoxPurpose choices in the Box model with standard options (Storage, Picking, Transport, Workshop)
    - Updated BoxTransformer to determine purpose based on box type characteristics
    - Completely removed the purpose field from BoxType table to simplify the data model

11. **Decimal Precision Handling**: Enhanced the decimal field handling for BoxType dimensions and weights:
    - Updated BoxType model to use appropriate max_digits and decimal_places for all decimal fields
    - Implemented precise decimal conversion in the BoxTypeTransformer using Python's Decimal type
    - Ensured consistent formatting of decimal values to exactly 2 decimal places
    - Fixed validation issues related to decimal precision in the synchronization process

12. **Frontend Implementation**: Started implementing the Vue.js frontend components:
    - Created base warehouse management interface with tabbed navigation
    - Implemented i18n support for German and English languages
    - Added comprehensive translations for all inventory-related terms
    - Created BoxManagement component with the following features:
      - Data table display of box types with sorting and pagination
      - Detailed view dialog for examining box specifications
      - Formatted display of dimensions and weight capacity
      - Loading states and error handling
      - Responsive layout using Vuetify components
    - Set up inventory store using Pinia for state management:
      - Implemented actions for fetching box types and storage locations
      - Added loading states and error handling
      - Created TypeScript interfaces for type safety
    - Configured API service layer:
      - Set up authenticated API requests
      - Created type-safe service methods
      - Implemented proper error handling
      - Added request/response interceptors

13. **TypeScript Integration**: Enhanced type safety across the frontend:
    - Added TypeScript interfaces for all inventory-related data structures
    - Implemented proper type checking for component props and data
    - Created type-safe store actions and state management
    - Added proper typing for API service methods

14. **StorageLocation Synchronization Improvements**:
    - Fixed issues with the `StammLagerorteTransformer` class to properly set fields required for the unique constraint (country, city_building, unit, compartment, shelf)
    - Enhanced the transformer to handle numeric field conversions properly (for unit, compartment, shelf)
    - Added logic to handle duplicate combinations by appending suffixes to location_code and unit fields
    - Improved record validation by ensuring all required fields have at least empty string values
    - Generated descriptive names from location components when name is not provided
    - Successfully synchronized all 923 storage locations with proper field mapping
    - Added field mapping documentation to clarify the relationship between legacy and new fields
    - Fixed issues with field data types, ensuring proper string conversion for numeric fields

15. **Box Synchronization Implementation**:
    - Analyzed the box data structure in the legacy system and identified key fields:
      - Core fields like `ID` and `max_Anzahl_Slots`
      - Box information stored in the `data_` JSON field including `Schuettentype`, `Anzahl_Schuetteneinheiten`, and `Schuettenzweck`
      - Audit information for creation and modification tracking
      - Related data through deferred references (`Relation_93` and `viele_schuetten`)
    - Implemented initial version of BoxTransformer:
      - Added support for extracting data from the `data_` JSON field
      - Made storage locations optional to match legacy system behavior
      - Implemented proper logging for boxes without storage locations
      - Added support for box type references and purpose mapping
    - Current status:
      - Successfully processing 4,216 box records from legacy system
      - Properly handling boxes without storage locations (valid business case)
      - Maintaining informational logging for tracking boxes without locations
      - Identified issues with specific box types not being found (e.g., 'FKE6320 Blau')
      - Need to investigate discrepancies between legacy box type names and synchronized box types
      - Approximately 300 box records failing due to missing box type references
      - Successfully transformed 3,475 box records with proper box type assignments

16. **Performance Optimization**:
    - Fixed timeout issues in the boxes API endpoint:
      - Implemented server-side pagination for the boxes list endpoint
      - Added page and page_size query parameters
      - Optimized database queries using select_related
      - Added proper error handling and logging
    - Enhanced frontend data handling:
      - Updated Axios timeout from 10s to 30s for better reliability
      - Implemented client-side pagination in the BoxManagement component
      - Added pagination state management in the inventory store
      - Updated the inventory service to handle paginated responses
      - Improved error handling and user feedback

17. **BoxSlot Synchronization Implementation**:
    - Implemented the BoxSlotTransformer to handle slot data from Stamm_Lager_Schuetten_Slots:
      - Added support for extracting data from the `data_` JSON field
      - Implemented proper mapping of slot codes, unit numbers, and color codes
      - Created logic to link slots to their parent boxes using legacy IDs
      - Generated barcodes using the format "BoxCode.SlotCode" for each slot
      - Added validation to ensure all required fields are set
      - Implemented proper error handling for missing box references
    - Enhanced the BoxSlot model with additional fields:
      - Added `legacy_slot_id` to store the unique identifier from the legacy system
      - Added `color_code` to maintain color information from the legacy system
      - Updated the `__str__` method to use dot notation (Box.Slot) for consistency
    - Successfully synchronized box slots from the legacy system:
      - Processed over 4,500 box slot records
      - Properly linked slots to their parent boxes
      - Maintained slot codes and unit numbers from the legacy system
      - Handled duplicate slots with appropriate validation
      - Generated consistent barcodes for all slots

## Next Steps
1. **Fix Box Type Synchronization Issues**:
   - Analyze all unique box types in legacy data
   - Create mapping for variant box type names
   - Implement data cleaning and standardization
   - Add validation checks before box synchronization
   - Create report of unmatched box types

2. **Implement Product Storage Synchronization**:
   - Create ProductStorageTransformer for inventory data
   - Implement synchronization for box inventory data from Lager_Schuetten and Lager_Schuetten_Einheiten
   - Create history tracking based on Historie_Stamm_Lager_Schuetten table structure
   - Add validation for product and slot relationships
   - Implement proper error handling for missing products or slots

3. Create APIs for inventory operations
   - Storage location management endpoints
   - Box and slot operations
   - Product placement and removal
   - Inventory movements and reservations

4. Design UI components for inventory management
   - Storage location browsing/management
   - Box management with slot visualization
   - Product placement interface
   - Movement recording

5. Integrate with the sales module for order fulfillment
   - Implement picking list generation
   - Create order fulfillment workflow
   - Add inventory reservation system

6. Develop inventory movement tracking functionality
   - Implement movement history
   - Add audit trail for inventory changes
   - Create reporting tools for movement analysis

7. Add inventory reporting features
   - Stock level reports
   - Inventory valuation
   - Movement and turnover analysis

8. Test the complete workflow with real data
   - Create comprehensive test scenarios
   - Validate with real-world inventory data
   - Perform load testing with large datasets

9. Enhance frontend functionality
   - Add create/edit forms for box types
   - Implement box assignment to storage locations
   - Add filtering and search capabilities
   - Create interactive warehouse map visualization
   - Implement drag-and-drop box management

## Acceptance Criteria
1. Given I need to migrate data from the legacy system
   When I run the synchronization process
   Then the data from Stamm_Lagerorte should be properly imported into the new data structure

2. Given I am managing inventory
   When I need to place a product in storage
   Then I should be able to assign it to a box slot and track its location

3. Given I am managing storage locations
   When I view a storage location
   Then I should see all boxes stored there with their contents

4. Given I am searching for a product
   When I query the system
   Then I should be able to find all storage locations where the product is stored

5. Given I am managing boxes
   When I move a box to a new storage location
   Then all product slots in that box should be updated to reflect the new location

6. Given I am processing an order
   When I need to pick items
   Then I should be able to view a picking list showing location information

7. Given I am planning future orders
   When I need to allocate inventory
   Then I should be able to reserve products for specific purposes

8. Given I am tracking inventory
   When products move in or out of the warehouse
   Then the system should record these movements with appropriate reference information

## Technical Requirements
- [x] Create data models for:
  - StorageLocation (country, city_building, unit, compartment, shelf, sale, special_spot, etc.)
  - BoxType (dimensions, weight capacity, slot count, slot naming scheme)
  - Box (box type, code, storage location, status, purpose)
  - BoxSlot (box, slot code, barcode, occupied status)
  - ProductStorage (product, box slot, quantity, reservation status)
  - InventoryMovement (product, from/to slots, quantity, movement type)

- [x] Implement synchronization with legacy Stamm_Lagerorte data
  - [x] Create extractor for Stamm_Lagerorte table
  - [x] Develop transformer to map legacy fields to new model
  - [x] Build loader to handle updates and conflict resolution
  - [x] Integrate with existing ETL pipeline
  - [x] Implement validation for duplicate storage locations
  - [x] Add error handling and reporting for sync process
  - [x] Create component-specific sync commands

- [x] Implement synchronization with legacy box type data
  - [x] Create BoxTypeTransformer for parameter table data
  - [x] Map legacy box type attributes to BoxType model
  - [x] Handle unit conversions and data formatting
  - [x] Add validation for data integrity
  - [x] Move purpose field from BoxType to Box model
  - [x] Implement precise decimal handling for dimensions and weights
  - [x] Fix migration issues and ensure proper database schema

- [x] Implement synchronization with legacy box and slot data
  - [x] Create extractors for Stamm_Lager_Schuetten and Stamm_Lager_Schuetten_Slots tables
  - [x] Develop transformers to map legacy box and slot data to new models
  - [x] Parse the `data_` JSON field to extract slot codes and unit information
  - [x] Use `ID_Lager_Schuetten_Slots` to link slots to their parent boxes
  - [x] Validate relationships using the `viele_zu_eins` reference as a secondary check
  - [ ] Implement synchronization for box inventory data from Lager_Schuetten and Lager_Schuetten_Einheiten
  - [ ] Create history tracking based on Historie_Stamm_Lager_Schuetten table
  - [x] Add validation for box and slot relationships
  - [x] Integrate with existing ETL pipeline
  - [x] Add error handling and reporting for sync process
  - [x] Map slot codes to meaningful identifiers in the new system

- [ ] Create APIs for managing inventory:
  - Storage location management
  - Box and slot operations
  - Product placement and removal
  - Inventory movements and reservations
  - Picking list generation

- [ ] Design UI components for:
  - Storage location browsing/management
  - Box management with slot visualization
  - Product placement interface
  - Movement recording
  - Picking list view
  - Inventory reports

- [ ] Integration with other modules:
  - Products module for product information
  - Sales module for order fulfillment and picking
  - Production module for raw material consumption

## Test Scenarios
1. Data Synchronization - Storage Locations
   - Setup: Configure test environment with mock legacy data
   - Steps: Run synchronization process for storage locations
   - Expected: New data structure should be populated with legacy data
   - Status: ✅ Completed - Successfully synchronized 923 storage location records with correct field mappings and handling of unique constraints

2. Data Synchronization - Box Types
   - Setup: Configure access to legacy parameter table with box type data
   - Steps: Run BoxType synchronization process
   - Expected: BoxType records should be created with proper dimensions and weights
   - Status: ✅ Completed - Successfully synchronized 49 box types with proper decimal precision

3. Data Synchronization - Boxes and Slots
   - Setup: Configure access to legacy Stamm_Lager_Schuetten and Stamm_Lager_Schuetten_Slots tables
   - Steps: Run Box and BoxSlot synchronization process
   - Expected: Box and BoxSlot records should be created with proper relationships and data
   - Status: ✅ Completed - Successfully synchronized 3,475 boxes and over 3,800 box slots with proper relationships and data

4. Product Placement
   - Setup: Create test storage locations, boxes, and products
   - Steps: Assign products to box slots
   - Expected: Products should be correctly associated with slots and locations
   - Status: 🔄 Pending implementation

5. Box Movement
   - Setup: Create test storage locations, boxes with products
   - Steps: Move a box to a different storage location
   - Expected: All product slots should update to the new location
   - Status: 🔄 Pending implementation

6. Inventory Reservation
   - Setup: Create test products in storage
   - Steps: Reserve inventory for an order
   - Expected: Reserved inventory should be marked and not available for other orders
   - Status: 🔄 Pending implementation

7. Picking Process
   - Setup: Create test order with multiple products
   - Steps: Generate picking list and complete picking
   - Expected: Inventory should be updated and movements recorded
   - Status: 🔄 Pending implementation

## Dependencies
- [x] Access to legacy Stamm_Lagerorte table
- [ ] Access to legacy Stamm_Lager_Schuetten table
- [ ] Access to legacy Stamm_Lager_Schuetten_Slots table
- [ ] Access to legacy Lager_Schuetten and Lager_Schuetten_Einheiten tables
- [ ] Access to legacy Historie_Stamm_Lager_Schuetten table
- [x] Product module
- [x] User authentication and permissions module
- [x] ETL pipeline for data synchronization
- [ ] Sales module for order integration
- [ ] Production module for materials management
- [ ] UI components for inventory management

## Estimation
- Story Points: 21
- Time Estimate: 3 weeks 

### Product Storage Data Structure Analysis
After examining the data from the `Artikel_Lagerorte` and `Lager_Schuetten` tables, we have a clearer understanding of how product storage is structured in the legacy system:

1. **Artikel_Lagerorte** (Product-Location Junction Table):
   This table manages the relationship between products and storage locations, along with inventory quantities:
   
   - **Primary Identifiers**:
     - `UUID`: Primary unique identifier for the product-location relationship
     - `ID_Artikel_Stamm`: Reference to the product (e.g., 18.497, 16.939) in the Artikel_Stamm table
     - `UUID_Stamm_Lagerorte`: Reference to the storage location (e.g., 360D0071BF89274789928A825289663E)
   
   - **Inventory Data**:
     - `Bestand`: Quantity/inventory amount at this location (can be null if no stock)
   
   - **Audit Information**:
     - Creation tracking fields (created_name, created_date, created_time)
     - Modification tracking fields (modified_name, modified_date, modified_time)
   
   - **Relationships**:
     - `Relation_88`: Appears to be a reference to related data
     - `Relation_89`: Another reference to related data
     - `Relation_113_zurueck`: Reference to history or reverse relationship

2. **Lager_Schuetten** (Box Inventory Table):
   This table manages the specific box assignments for products, linking boxes to the product-location relationships:
   
   - **Primary Identifiers**:
     - `ID`: Primary key for the box record
     - `ID_Stamm_Lager_Schuetten`: Reference to the box definition (e.g., 626.692) in Stamm_Lager_Schuetten
     - `UUID_Artikel_Lagerorte`: Reference to the product-location junction (e.g., 67494EC839DF7A45B8433C48126FD8B)
   
   - **Box Inventory Data** (stored in the `data_` JSON field):
     - `"Schuetten_ID"`: Internal box identifier (e.g., "626692")
     - `"Artikel_Lagerort"`: Reference to the product-location UUID
     - `"Stamm_Lagerort"`: Reference to the storage location UUID (e.g., "360D0071BF89274789928A825289663E")
   
   - **Audit Information**:
     - Creation tracking fields (created_name, created_date, created_time)
     - Modification tracking fields (modified_name, modified_date, modified_time)
   
   - **Relationships**:
     - `Relation_113`: Reference to related data
     - `Relation_96_zurueck`: Reference to history or related box data
     - `Relation_95_zurueck`: Another reference to related box data

3. **Lager_Schuetten_Einheiten** (Box Units Table):
   This table manages the specific units stored in boxes, providing detailed inventory counts:
   
   - Works in conjunction with Lager_Schuetten to track individual units within boxes
   - Connects specific product references to physical box slots
   - Contains detailed quantity information at the unit level
   - Maintains history of product placements and removals

### Product Storage Data Relationships
Based on the analysis of the tables, we can identify the following key relationships:

1. **Product → Storage Location Relationship**:
   - Managed through `Artikel_Lagerorte` as a many-to-many relationship
   - Each product (ID_Artikel_Stamm) can be stored in multiple locations
   - Each location (UUID_Stamm_Lagerorte) can store multiple products
   - The `Bestand` field indicates the quantity of a product at a specific location

2. **Product-Location → Box Relationship**:
   - Managed through `Lager_Schuetten`
   - Each product-location junction (UUID_Artikel_Lagerorte) can be associated with a box
   - The box (ID_Stamm_Lager_Schuetten) serves as the physical container for the product
   - The data_ JSON field provides additional linking between boxes, products, and locations

3. **Box → Box Slot Relationship**:
   - Managed through `Stamm_Lager_Schuetten_Slots` and extended in `Lager_Schuetten_Einheiten`
   - Each box can have multiple slots
   - Each slot can hold a specific product unit
   - The relationship forms the most granular level of inventory tracking

### Product Storage Data Mapping Strategy
Based on the analysis, we will map these legacy tables to our new ProductStorage model as follows:

1. **ProductStorage Model**:
   - `product` ← Foreign key to Product, determined by ID_Artikel_Stamm in Artikel_Lagerorte
   - `box_slot` ← Foreign key to BoxSlot, connecting to the specific slot in a box
   - `quantity` ← Bestand from Artikel_Lagerorte, potentially refined by unit counts in Lager_Schuetten_Einheiten
   - `status` ← Derived from data (in_stock, reserved, allocated)
   - `reservation_reference` ← Reference to order or other process reserving the inventory
   - Standard audit fields will be maintained by Django

2. **Implementation Notes for ProductStorage Synchronization**:
   - Data from both Artikel_Lagerorte and Lager_Schuetten must be combined to create complete ProductStorage records
   - The UUID_Artikel_Lagerorte field is the key link between the two tables
   - Box and slot references must be resolved before creating ProductStorage records
   - Quantity information needs to be carefully managed, especially when distributed across multiple slots
   - Storage locations without box assignments still need to be maintained for compatibility
   - Consider handling special cases where Bestand value is null (no inventory)

3. **ProductStorage Enhancements**:
   - Add reservation system for tying inventory to orders
   - Implement status tracking (in_stock, reserved, allocated, etc.)
   - Create inventory movement history tracking
   - Add validation for quantity updates
   - Implement stock level alerts and notifications

This detailed understanding of the product storage data structure will enable us to properly implement the ProductStorage model and its synchronization with the legacy system, ensuring all inventory data is preserved while enhancing the functionality for modern warehouse management needs.

2. **Implementation Notes for BoxSlot Synchronization**:
   - The `data_` field contains crucial information in JSON format that must be parsed during synchronization
   - Box records must be synchronized before box slots to maintain referential integrity
   - The `ID_Lager_Schuetten_Slots` field is the key to linking slots to their parent boxes, not the `viele_zu_eins` reference
   - The `viele_zu_eins` reference provides additional validation but the primary relationship is through `ID_Lager_Schuetten_Slots`
   - Slot codes should be preserved for compatibility with legacy system
   - The `Einheitenfabe` field may need mapping to human-readable color names
   - Status should be derived based on associated inventory data

3. **BoxSlot Enhancements**:
   - Add barcode generation for each slot based on slot code and box identifier
   - Implement status tracking (empty, occupied, reserved)
   - Create relationships to ProductStorage records for inventory tracking
   - Add validation to ensure slot numbers are unique within a box
   - Implement history tracking for slot status changes

This detailed understanding of the slot data structure will enable us to properly implement the BoxSlot model and its synchronization with the legacy system, ensuring all relevant data is preserved while enhancing the functionality for modern warehouse management needs. 