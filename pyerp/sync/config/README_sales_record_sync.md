# Sales Record Synchronization

This document describes the implementation of the sales record synchronization from the legacy 4D-based ERP system to the new pyERP platform.

## Overview

The sales record sync integrates the following data from the legacy system:

1. **Sales Records** (from `Belege` table)
   - Invoices, proposals, delivery notes, credit notes, etc.
   - Header information including customer, dates, totals, etc.

2. **Sales Record Line Items** (from `Belege_Pos` table)
   - Line items associated with sales records
   - Product information, quantities, prices, etc.

## Implementation Details

### Data Models

The sync populates the following Django models:

- `SalesRecord`: Main model for all types of sales documents
- `SalesRecordItem`: Line items associated with sales records
- `PaymentTerms`: Payment terms referenced by sales records
- `PaymentMethod`: Payment methods referenced by sales records
- `ShippingMethod`: Shipping methods referenced by sales records

### Sync Components

The implementation consists of the following components:

1. **Transformer** (`sales_record.py`)
   - Converts legacy data format to Django model format
   - Handles data type conversions, field mappings, and lookups
   - Includes special handling for dates, addresses, and currency conversion

2. **Sync Configuration** (`sales_record_sync.py`)
   - Defines the mapping between legacy and new data models
   - Sets up source, target, and field mappings
   - Configures related mappings for line items

3. **Management Command** (`sync_sales_records.py`)
   - Provides a CLI interface for running the sync
   - Supports incremental and full sync options
   - Includes options for filtering and debugging

4. **Scheduled Tasks** (in `tasks.py`)
   - Incremental sync every 15 minutes
   - Full sync daily at 3:00 AM

## Usage

### Running the Sync Manually

To run the sync manually, use the management command:

```bash
# Run incremental sync (only new/modified records)
python manage.py sync_sales_records

# Run full sync (all records)
python manage.py sync_sales_records --full

# Limit the number of records
python manage.py sync_sales_records --limit 100

# Only sync sales records (not line items)
python manage.py sync_sales_records --records-only

# Only sync line items for existing sales records
python manage.py sync_sales_records --line-items-only

# Apply additional filters
python manage.py sync_sales_records --filters='{"Papierart": "R"}'

# Enable debug mode
python manage.py sync_sales_records --debug
```

### Monitoring Sync Status

You can monitor the sync status through:

1. **Django Admin**
   - Check `SyncLog` entries for sync results
   - Review `SyncLogDetail` for individual record sync details

2. **Log Files**
   - Check application logs for detailed sync information
   - Look for events with the prefix `sales_record_sync_`

## Data Mapping

### Sales Record Mapping

| Legacy Field (Belege)   | Django Field (SalesRecord)    | Notes                                      |
|-------------------------|-------------------------------|-------------------------------------------|
| AbsNr                   | legacy_id                     | Primary key in legacy system              |
| PapierNr                | record_number                 | Document number                           |
| Datum                   | record_date                   | Converted from D!M!Y format               |
| Papierart               | record_type                   | Mapped to INVOICE, PROPOSAL, etc.         |
| KundenNr                | customer                      | Foreign key to Customer model             |
| Netto                   | subtotal                      | Net amount before tax                     |
| MWST_EUR                | tax_amount                    | Tax amount                                |
| Frachtkosten            | shipping_cost                 | Shipping costs                            |
| Bearbeitungskos         | handling_fee                  | Handling/processing fee                   |
| Endbetrag               | total_amount                  | Total amount including tax                |
| bezahlt                 | payment_status                | Payment status                            |
| ZahlungsDat             | payment_date                  | Payment date                              |
| Währung                 | currency                      | Currency code (DM converted to EUR)       |
| MWSt_Art                | tax_type                      | Tax type                                  |
| Text                    | notes                         | Notes                                     |
| NettoTage               | payment_terms.days_due        | Payment due days                          |
| SkontoTage              | payment_terms.discount_days   | Cash discount days                        |
| Skonto_G                | payment_terms.discount_percent| Cash discount percentage                  |
| Zahlungsart_A           | payment_method.name           | Payment method name                       |
| Versandart              | shipping_method.name          | Shipping method name                      |
| Lief_Adr                | shipping_address              | Parsed and normalized                     |
| Rech_Adr                | billing_address               | Parsed and normalized                     |

### Sales Record Item Mapping

| Legacy Field (Belege_Pos) | Django Field (SalesRecordItem) | Notes                                  |
|---------------------------|--------------------------------|----------------------------------------|
| AbsNr + PosNr             | legacy_id                      | Composite key in legacy system         |
| PosNr                     | position                       | Line item position                     |
| ArtNr                     | product_code                   | Product code                           |
| Bezeichnung               | description                    | Product description                    |
| Menge                     | quantity                       | Quantity                               |
| Preis                     | unit_price                     | Unit price                             |
| Rabatt                    | discount_percentage            | Discount percentage                    |
| Pos_Betrag                | line_total                     | Line item total                        |
| Art                       | item_type                      | Mapped to PRODUCT, SERVICE, etc.       |
| Pick_Menge                | fulfilled_quantity             | Fulfilled quantity                     |
| Picking_ok                | fulfillment_status             | Mapped to PENDING, FULFILLED, etc.     |

## Future Enhancements

1. **Document Relationships**
   - Implement linking between related documents (proposal → invoice → credit note)
   - Database structure is prepared but functionality is deferred to a later phase

2. **Address Normalization**
   - Improve address parsing for more accurate extraction of components
   - Add geocoding for address validation and mapping

3. **Performance Optimization**
   - Add indexing for frequently queried fields
   - Implement batched processing for large datasets

4. **Data Validation**
   - Add more comprehensive validation rules
   - Implement data cleaning for legacy data issues 