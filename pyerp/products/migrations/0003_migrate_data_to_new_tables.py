from django.db import migrations


def migrate_products_to_new_tables(apps, schema_editor):
    """
    Migrate data from the old Product model to the new ParentProduct and VariantProduct models.
    """
    Product = apps.get_model('products', 'Product')
    ParentProduct = apps.get_model('products', 'ParentProduct')
    VariantProduct = apps.get_model('products', 'VariantProduct')
    
    # First, migrate all parent products
    parent_products = Product.objects.filter(is_parent=True)
    parent_mapping = {}  # To store mapping of old parent ID to new parent ID
    
    for old_parent in parent_products:
        new_parent = ParentProduct(
            # Basic identification
            sku=old_parent.sku,
            legacy_id=old_parent.legacy_id,
            base_sku=old_parent.base_sku,
            
            # Names and descriptions
            name=old_parent.name,
            name_en=old_parent.name_en,
            short_description=old_parent.short_description,
            short_description_en=old_parent.short_description_en,
            description=old_parent.description,
            description_en=old_parent.description_en,
            keywords=old_parent.keywords,
            
            # Physical attributes
            dimensions=old_parent.dimensions,
            weight=old_parent.weight,
            
            # Pricing
            list_price=old_parent.list_price,
            wholesale_price=old_parent.wholesale_price,
            gross_price=old_parent.gross_price,
            cost_price=old_parent.cost_price,
            
            # Inventory
            stock_quantity=old_parent.stock_quantity,
            min_stock_quantity=old_parent.min_stock_quantity,
            backorder_quantity=old_parent.backorder_quantity,
            open_purchase_quantity=old_parent.open_purchase_quantity,
            last_receipt_date=old_parent.last_receipt_date,
            last_issue_date=old_parent.last_issue_date,
            
            # Sales statistics
            units_sold_current_year=old_parent.units_sold_current_year,
            units_sold_previous_year=old_parent.units_sold_previous_year,
            revenue_previous_year=old_parent.revenue_previous_year,
            
            # Status flags
            is_active=old_parent.is_active,
            is_discontinued=old_parent.is_discontinued,
            
            # Manufacturing flags
            has_bom=old_parent.has_bom,
            
            # Product-specific flags
            is_one_sided=old_parent.is_one_sided,
            is_hanging=old_parent.is_hanging,
            
            # Category
            category=old_parent.category,
        )
        new_parent.save()
        parent_mapping[old_parent.id] = new_parent
    
    # Then, migrate all variant products
    variant_products = Product.objects.filter(is_parent=False)
    
    for old_variant in variant_products:
        # Skip variants without a parent
        if not old_variant.parent_id or old_variant.parent_id not in parent_mapping:
            print(f"Skipping variant {old_variant.sku} - parent not found")
            continue
        
        new_parent = parent_mapping[old_variant.parent_id]
        
        new_variant = VariantProduct(
            # Basic identification
            sku=old_variant.sku,
            legacy_id=old_variant.legacy_id,
            legacy_sku=old_variant.legacy_sku,
            base_sku=old_variant.base_sku,
            variant_code=old_variant.variant_code,
            
            # Parent reference
            parent=new_parent,
            
            # Names and descriptions
            name=old_variant.name,
            name_en=old_variant.name_en,
            short_description=old_variant.short_description,
            short_description_en=old_variant.short_description_en,
            description=old_variant.description,
            description_en=old_variant.description_en,
            keywords=old_variant.keywords,
            
            # Physical attributes
            dimensions=old_variant.dimensions,
            weight=old_variant.weight,
            
            # Pricing
            list_price=old_variant.list_price,
            wholesale_price=old_variant.wholesale_price,
            gross_price=old_variant.gross_price,
            cost_price=old_variant.cost_price,
            
            # Inventory
            stock_quantity=old_variant.stock_quantity,
            min_stock_quantity=old_variant.min_stock_quantity,
            backorder_quantity=old_variant.backorder_quantity,
            open_purchase_quantity=old_variant.open_purchase_quantity,
            last_receipt_date=old_variant.last_receipt_date,
            last_issue_date=old_variant.last_issue_date,
            
            # Sales statistics
            units_sold_current_year=old_variant.units_sold_current_year,
            units_sold_previous_year=old_variant.units_sold_previous_year,
            revenue_previous_year=old_variant.revenue_previous_year,
            
            # Status flags
            is_active=old_variant.is_active,
            is_discontinued=old_variant.is_discontinued,
            
            # Manufacturing flags
            has_bom=old_variant.has_bom,
            
            # Product-specific flags
            is_one_sided=old_variant.is_one_sided,
            is_hanging=old_variant.is_hanging,
            
            # Category
            category=old_variant.category,
        )
        new_variant.save()


def reverse_migration(apps, schema_editor):
    """
    Reverse the migration by clearing the new tables.
    """
    ParentProduct = apps.get_model('products', 'ParentProduct')
    VariantProduct = apps.get_model('products', 'VariantProduct')
    
    # Delete all variant products first to avoid foreign key constraints
    VariantProduct.objects.all().delete()
    ParentProduct.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_create_parent_variant_tables'),
    ]

    operations = [
        migrations.RunPython(migrate_products_to_new_tables, reverse_migration),
    ] 