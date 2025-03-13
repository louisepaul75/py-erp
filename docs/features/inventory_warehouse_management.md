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
After examining the Stamm_Lagerorte table data (923 records), we have a clearer understanding of the legacy storage location structure:

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
   - `name` ← Generated from `location_code` or components

2. **Box and BoxSlot Models**:
   - These are new concepts not present in the legacy system
   - Boxes will be assigned to StorageLocations
   - Each Box will contain multiple BoxSlots based on BoxType configuration

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

### Implementation Notes
- The `ID_Lagerort` field is used as the primary identifier for synchronization, as it's also printed on labels and QR codes in the legacy system.
- We're skipping the `Schuette`, `Slots`, and `Schuette_und_Slots` fields for now, as they're not critical for the initial implementation.
- The `location_code` field stores the formatted location string from `Lagerort`, which provides a human-readable identifier.
- The `name` field is generated from the `location_code` if available, or from the individual components if not.
- The BoxType configuration will be used to standardize box creation and ensure consistency across the warehouse.
- For boxes with missing dimensions or weights, we'll implement validation rules to ensure data integrity.

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

## Next Steps
1. Implement the UI components for inventory management
2. Create APIs for inventory operations
3. Integrate with the sales module for order fulfillment
4. Implement picking list generation
5. Add inventory reporting features
6. Test the complete workflow with real data
7. Implement Box and BoxSlot synchronization
8. Develop inventory movement tracking functionality
9. Create standard BoxType configurations based on the identified parameters
10. Implement validation for boxes with missing dimensions or weights

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
  - Box (box type, code, storage location, status)
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
1. Data Synchronization
   - Setup: Configure test environment with mock legacy data
   - Steps: Run synchronization process
   - Expected: New data structure should be populated with legacy data
   - Status: ✅ Completed - Successfully synchronized 923 storage location records

2. Product Placement
   - Setup: Create test storage locations, boxes, and products
   - Steps: Assign products to box slots
   - Expected: Products should be correctly associated with slots and locations

3. Box Movement
   - Setup: Create test storage locations, boxes with products
   - Steps: Move a box to a different storage location
   - Expected: All product slots should update to the new location

4. Inventory Reservation
   - Setup: Create test products in storage
   - Steps: Reserve inventory for an order
   - Expected: Reserved inventory should be marked and not available for other orders

5. Picking Process
   - Setup: Create test order with multiple products
   - Steps: Generate picking list and complete picking
   - Expected: Inventory should be updated and movements recorded

## Dependencies
- [x] Access to legacy Stamm_Lagerorte table
- [x] Product module
- [x] User authentication and permissions module
- [x] ETL pipeline for data synchronization
- [ ] Sales module for order integration
- [ ] Production module for materials management
- [ ] UI components for inventory management

## Estimation
- Story Points: 21
- Time Estimate: 3 weeks 