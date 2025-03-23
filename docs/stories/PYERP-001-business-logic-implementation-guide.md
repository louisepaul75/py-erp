# Story: PYERP-001 - Business Logic Implementation Guide

## Description
As a developer
I want to follow standardized patterns for implementing business logic
So that the codebase remains consistent, maintainable, and well-tested

## Background
The pyERP system needs a consistent approach to implementing business logic across different modules. This guide establishes standards for creating service layers, API endpoints, and tests to ensure code quality and maintainability.

This story provides a guide for implementing business functions across all modules, not just inventory. It's intended to serve as a reference document for current and future development.

## Acceptance Criteria
1. Given a new business function needs to be implemented
   When a developer follows the guide
   Then they should be able to create a well-structured service layer

2. Given an existing business function needs to be extended
   When a developer follows the guide
   Then they should be able to extend the functionality while maintaining consistency

3. Given a new domain-specific module is being created
   When developers implement it following the guide
   Then the implementation should follow the established patterns

## Technical Requirements
- [ ] Document the service-layer architecture pattern
- [ ] Provide examples of business logic implementation
- [ ] Define error handling and validation strategies
- [ ] Establish testing standards for business logic
- [ ] Define API endpoint patterns for exposing business logic
- [ ] Document transaction management and data integrity approaches

## Technical Guide

### 1. Service-Layer Architecture

All business logic should be implemented using the service layer pattern, separating business logic from presentation and data layers:

```
Business Modules Structure:
├── module_name/
│   ├── models.py         # Data structures
│   ├── services.py       # Business logic
│   ├── urls.py           # API endpoints
│   ├── tests/            # Test directory
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
```

### 2. Implementation Workflow

#### Step 1: Define Data Models
First, define or use existing data models (in `models.py`).

#### Step 2: Implement Service Layer
Create your service class with clear, focused methods:

```python
class BusinessModuleService:
    """Service for business module operations."""

    @classmethod
    @transaction.atomic
    def perform_business_operation(cls, entity_a, entity_b, **kwargs):
        """
        Business operation description.
        
        Args:
            entity_a: First entity needed
            entity_b: Second entity needed
            user: User performing the action (for audit)
            
        Returns:
            The operation result entity
            
        Raises:
            ValidationError: If the operation cannot be completed
        """
        # 1. Input validation
        if not entity_a or not entity_b:
            raise ValidationError(_("Required entities missing"))
            
        # 2. Business rule validation
        if not business_rule_satisfied(entity_a, entity_b):
            raise ValidationError(_("Business rule not satisfied"))
            
        # 3. Core operation logic
        result = perform_core_functionality(entity_a, entity_b)
        
        # 4. Record audit trail
        record_operation_audit(entity_a, entity_b, result, user)
        
        # 5. Return result
        return result
```

#### Step 3: Add API Endpoints
Expose your business logic via API endpoints in `urls.py`:

```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def business_operation_endpoint(request):
    """API endpoint for the business operation."""
    try:
        # 1. Extract request parameters
        entity_a_id = request.data.get("entity_a_id")
        entity_b_id = request.data.get("entity_b_id")
        
        # 2. Parameter validation
        if not entity_a_id or not entity_b_id:
            return Response(
                {"detail": "Required parameters missing"},
                status=400,
            )
            
        # 3. Entity retrieval
        try:
            entity_a = EntityA.objects.get(id=entity_a_id)
            entity_b = EntityB.objects.get(id=entity_b_id)
        except (EntityA.DoesNotExist, EntityB.DoesNotExist):
            return Response(
                {"detail": "Entities not found"},
                status=404,
            )
            
        # 4. Service call
        try:
            result = BusinessModuleService.perform_business_operation(
                entity_a=entity_a,
                entity_b=entity_b,
                user=request.user,
            )
            
            # 5. Response formatting
            return Response({
                "id": result.id,
                "status": result.status,
                "message": f"Operation completed successfully",
                # Other relevant data...
            })
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error in business operation: {e}")
        return Response({"detail": "Operation failed"}, status=500)
```

#### Step 4: Write Unit Tests
Create comprehensive tests for your business logic:

```python
class BusinessModuleServiceTestCase(TestCase):
    """Test case for the business module service."""

    def setUp(self):
        """Set up test data."""
        # Create test entities
        self.entity_a = EntityA.objects.create(...)
        self.entity_b = EntityB.objects.create(...)
        
    def test_successful_operation(self):
        """Test successful business operation."""
        result = BusinessModuleService.perform_business_operation(
            entity_a=self.entity_a,
            entity_b=self.entity_b,
        )
        
        # Verify results
        self.assertEqual(result.status, expected_status)
        
        # Verify database state
        self.entity_a.refresh_from_db()
        self.assertEqual(self.entity_a.some_field, expected_value)
        
    def test_validation_errors(self):
        """Test validation errors are raised appropriately."""
        with self.assertRaises(ValidationError):
            BusinessModuleService.perform_business_operation(
                entity_a=None,  # Invalid input
                entity_b=self.entity_b,
            )
```

### 3. Key Design Principles

1. **Transaction Management**: Use `@transaction.atomic` to ensure all database operations succeed or fail together.

2. **Input Validation**: Always validate inputs before processing.

3. **Business Rule Enforcement**: Enforce business rules explicitly with clear error messages.

4. **Audit Trails**: Log all significant operations for accountability.

5. **Error Handling**: Use specific exceptions and handle them appropriately.

6. **Idempotency**: Design operations to be safely repeatable without side effects.

7. **Separation of Concerns**: Keep business logic in services separate from API endpoints.

### 4. Testing Best Practices

1. **Test Isolation**: Each test should be independent.

2. **Coverage Goals**: Aim for at least 80% code coverage.

3. **Test Categories**:
   - **Unit Tests**: Test individual service methods
   - **Integration Tests**: Test API endpoints
   - **Edge Cases**: Test boundary conditions and error paths

4. **Test Data Setup**: Use `setUp` to create necessary test data.

5. **Mocks**: Use mocks for external dependencies.

6. **Assertions**: Verify both returned values and database state.

### 5. Error Handling Strategy

1. **Service Layer**: Use `ValidationError` with descriptive messages for business rule violations.

2. **API Layer**: 
   - HTTP 400: Client errors (validation failures)
   - HTTP 404: Resource not found
   - HTTP 500: Unexpected server errors

3. **Logging**: Log all errors with appropriate context.

### 6. Implementation Examples

#### Example: Product Transfer Between Warehouses

```python
class InventoryTransferService:
    @classmethod
    @transaction.atomic
    def transfer_product(cls, product, source_warehouse, target_warehouse, 
                         quantity, reference=None, user=None):
        """Transfer product between warehouses."""
        # Validation
        if quantity <= 0:
            raise ValidationError(_("Quantity must be positive"))
            
        # Check availability
        source_inventory = WarehouseInventory.objects.get(
            product=product, warehouse=source_warehouse)
            
        if source_inventory.available_quantity < quantity:
            raise ValidationError(_("Insufficient quantity available"))
            
        # Perform transfer
        source_inventory.quantity -= quantity
        source_inventory.save()
        
        target_inventory, created = WarehouseInventory.objects.get_or_create(
            product=product, warehouse=target_warehouse,
            defaults={"quantity": 0})
            
        target_inventory.quantity += quantity
        target_inventory.save()
        
        # Create transfer record
        transfer = InventoryTransfer.objects.create(
            product=product,
            source_warehouse=source_warehouse,
            target_warehouse=target_warehouse,
            quantity=quantity,
            reference=reference,
            performed_by=user,
        )
        
        return transfer
```

### 7. Documentation Standards

1. **Docstrings**: Always include detailed docstrings for all service methods:
   - Description of the operation
   - Args with types and descriptions
   - Returns with description
   - Raises with exception types and conditions

2. **Method Names**: Use clear, action-oriented method names (e.g., `transfer_product` not `do_transfer`).

3. **Parameters**: Use descriptive parameter names and appropriate default values.

### 8. Extending to New Business Domains

When implementing business logic for new domains:

1. **Domain Analysis**: Identify the key entities and operations in the domain.

2. **Data Model**: Design or update data models to represent the domain.

3. **Service Layer**: Create a dedicated service class with methods for each business operation.

4. **API Integration**: Add API endpoints that use the service methods.

5. **Testing**: Develop comprehensive tests covering the business rules.

## Test Scenarios
1. Inventory Box Movement
   - Setup: Create test box and storage locations
   - Steps: Move box to new location using service layer
   - Expected: Box location updated with proper audit trail

2. Product Transfer Between Warehouses
   - Setup: Create product inventory in two warehouses
   - Steps: Transfer quantity from source to target warehouse
   - Expected: Quantities updated correctly in both warehouses with proper audit trail

3. Error Handling in Product Transfer
   - Setup: Create product with insufficient quantity
   - Steps: Attempt to transfer more than available
   - Expected: ValidationError raised with appropriate message

## Dependencies
- [ ] Django framework
- [ ] Django REST framework

## Estimation
- Story Points: N/A (Reference document)
- Time Estimate: N/A (Ongoing standard) 