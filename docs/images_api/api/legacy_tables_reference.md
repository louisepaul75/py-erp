# Legacy ERP Tables Reference

This document provides a reference for the tables available in the legacy ERP system and their filtering capabilities. It is based on our testing and exploration of the legacy API.

## Available Tables

Based on our testing, the following tables are available in the legacy ERP system:

- **Kunden** - Customers
- **Heimarbeiter** - Home workers
- **Kassenbuch** - Cash book
- **Lieferant** - Suppliers
- **Artikel** - Products/Articles

## Table Details

### Kunden (Customers)

The Kunden table contains customer information.

**Access URL**: `/rest/Kunden`

**Common Fields**:
- `Kunden_Nr` - Customer number
- `Name` - Customer name
- `Strasse` - Street address
- `PLZ` - Postal code
- `Ort` - City
- `Land` - Country
- `Telefon` - Phone number
- `Email` - Email address
- `aktiv` - Active status (boolean)
- `CREATIONDATE` - Creation date

**Supported Filters**:
- Equality filters: `Kunden_Nr = '12345'`
- Text search: `Name LIKE '%Company%'`
- Boolean filters: `aktiv = true`
- Date filters: `CREATIONDATE >= '2023-01-01'`

**Example Queries**:
```
/rest/Kunden?$top=10&$skip=0&$filter="Name LIKE '%GmbH%'"
/rest/Kunden?$top=10&$skip=0&$filter="aktiv = true"
```

### Artikel (Products/Articles)

The Artikel table contains product information.

**Access URL**: `/rest/Artikel`

**Common Fields**:
- `Artikel_Nr` - Product number
- `Bezeichnung` - Product description/name
- `Preis` - Price
- `Einheit` - Unit
- `aktiv` - Active status (boolean)
- `CREATIONDATE` - Creation date

**Supported Filters**:
- Equality filters: `Artikel_Nr = '115413'`
- Text search: `Bezeichnung LIKE '%Test%'`
- Numeric comparisons: `Preis > 10`
- Boolean filters: `aktiv = true`
- Date filters: `CREATIONDATE >= '2023-01-01'`
- Combined filters: `Preis > 5 AND aktiv = true`

**Example Queries**:
```
/rest/Artikel?$top=10&$skip=0&$filter="Artikel_Nr = '115413'"
/rest/Artikel?$top=10&$skip=0&$filter="Preis > 10 AND aktiv = true"
```

## Testing Table Filtering

To test which filters are supported by a specific table, you can use the `test_filter.py` script:

```bash
python pyerp/direct_api/scripts/test_filter.py --env live --table Kunden --verbose
```

To list all available tables in the legacy ERP system:

```bash
python pyerp/direct_api/scripts/test_filter.py --env live --list-tables --verbose
```

## Notes on Table Access

1. **Authentication Required**: All table access requires a valid session cookie.
2. **Pagination**: Use `$top` and `$skip` parameters to paginate results.
3. **Response Format**: The response format may vary between tables.
4. **Field Names**: Field names are case-sensitive in filter expressions.
5. **Filter Support**: Not all tables support all filter types. Test each table to determine supported filters.

## Common Issues and Solutions

1. **"Table not found" errors**: Verify the table name is correct and that you have permission to access it.
2. **Filter errors**: If a filter returns an error, try removing the filter or using a different filter type.
3. **Empty results**: Some tables may have no data or may require specific filters to return results.
4. **Performance issues**: Large tables may require pagination and efficient filtering to avoid timeouts.

## Updating This Document

This document should be updated as new tables are discovered or as more information about existing tables becomes available. When adding a new table, include:

1. The table name and description
2. Common fields and their data types
3. Supported filter types with examples
4. Any special considerations for accessing the table
