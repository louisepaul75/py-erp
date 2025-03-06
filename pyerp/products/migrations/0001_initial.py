
import django.db.models.deletion  # noqa: F401
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True  # noqa: F841

    dependencies = []  # noqa: F841

    operations = [  # noqa: F841
        migrations.CreateModel(
        name="ImageSyncLog",  # noqa: E128
        fields=[  # noqa: F841
        (  # noqa: E128
        "id",
        models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False  # noqa: E128
    ),
                  ),
                  (
                      "started_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now_add=True, help_text="When the sync process started"  # noqa: E501
                  ),
                  ),
                  (
                      "completed_at",  # noqa: E128
                      models.DateTimeField(
                      blank=True,  # noqa: E128
                      help_text="When the sync process completed",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "status",  # noqa: E128
                      models.CharField(
                      choices=[  # noqa: F841
                      # noqa: F841
                  ("in_progress", "In Progress"),
                  ("completed", "Completed"),
                  ("failed", "Failed"),
                  ],
                  default="in_progress",  # noqa: F841
                  help_text="Current status of the sync process",  # noqa: F841
                  max_length=20,  # noqa: F841
                  ),
                  ),
                  (
                      "images_added",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Number of new images added"  # noqa: E128
                  ),
                  ),
                  (
                      "images_updated",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Number of existing images updated"  # noqa: E501
                  ),
                  ),
                  (
                      "images_deleted",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Number of images deleted"  # noqa: E128
                  ),
                  ),
                  (
                      "products_affected",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Number of products affected by the sync"  # noqa: E501
                  ),
                  ),
                  (
                      "error_message",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Error message if the sync failed"  # noqa: E501
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Image Sync Log",  # noqa: E128
                      "verbose_name_plural": "Image Sync Logs",
                  "ordering": ["-started_at"],
                  },
                  ),
                  migrations.CreateModel(
                      name="ProductCategory",  # noqa: E128
                      fields=[  # noqa: F841
                      (  # noqa: E128
                      "id",
                      models.BigAutoField(
                      auto_created=True,  # noqa: E128
                      primary_key=True,  # noqa: F841
                      serialize=False,  # noqa: F841
                      verbose_name="ID",  # noqa: F841
                  ),
                  ),
                  (
                      "code",  # noqa: E128
                      models.CharField(
                      help_text="Unique category code", max_length=50, unique=True  # noqa: E501
                  ),
                  ),
                  ("name", models.CharField(help_text="Category name", max_length=100)),  # noqa: E501
                  (
                      "description",  # noqa: E128
                  models.TextField(blank=True, help_text="Category description"),  # noqa: E501
                  ),
                  (
                      "parent",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      help_text="Parent category",  # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                      related_name="children",  # noqa: F841
                      to="products.productcategory",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Product Category",  # noqa: E128
                      "verbose_name_plural": "Product Categories",
                  "ordering": ["name"],
                  },
                  ),
                  migrations.CreateModel(
                      name="Product",  # noqa: E128
                      fields=[  # noqa: F841
                      (  # noqa: E128
                      "id",
                      models.BigAutoField(
                      auto_created=True,  # noqa: E128
                      primary_key=True,  # noqa: F841
                      serialize=False,  # noqa: F841
                      verbose_name="ID",  # noqa: F841
                  ),
                  ),
                  (
                      "sku",  # noqa: E128
                      models.CharField(
                  help_text="Stock Keeping Unit (maps to ArtNr in legacy system)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "base_sku",  # noqa: E128
                      models.CharField(
                      db_index=True,  # noqa: E128
                  help_text="Base SKU without variant (maps to fk_ArtNr in legacy system)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  ),
                  ),
                  (
                      "variant_code",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Variant code (maps to ArtikelArt in legacy system)",  # noqa: E501
                  max_length=10,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_id",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="ID in the legacy system",  # noqa: F841
                      max_length=50,  # noqa: F841
                      null=True,  # noqa: F841
                      unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_sku",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Legacy SKU (maps to alteNummer in Artikel_Variante)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "is_parent",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                  help_text="Whether this is a parent product (maps to Art_Kalkulation records)",  # noqa: E501
                  ),
                  ),
                  (
                      "name",  # noqa: E128
                      models.CharField(
                  help_text="Product name (maps to Bezeichnung in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "name_en",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product name in English (maps to Bezeichnung_ENG in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "short_description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Short product description (maps to Beschreibung_kurz in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "short_description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Short product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Full product description (maps to Beschreibung in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Full product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "keywords",  # noqa: E128
                      models.CharField(
                      blank=True, help_text="Search keywords", max_length=255  # noqa: E128
                  ),
                  ),
                  (
                      "dimensions",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product dimensions (LxWxH)",  # noqa: F841
                  max_length=50,  # noqa: F841
                  ),
                  ),
                  (
                      "weight",  # noqa: E128
                      models.IntegerField(
                      blank=True, help_text="Weight in grams", null=True  # noqa: E128
                  ),
                  ),
                  (
                      "list_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Retail price (maps to Laden price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "wholesale_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Wholesale price (maps to Handel price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "gross_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Recommended retail price (maps to Empf. price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "cost_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Cost price (maps to Einkauf price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "stock_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Current stock quantity"),  # noqa: E501
                  ),
                  (
                      "min_stock_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Minimum stock quantity before reordering"  # noqa: E501
                  ),
                  ),
                  (
                      "backorder_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Quantity on backorder"),  # noqa: E501
                  ),
                  (
                      "open_purchase_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Quantity on open purchase orders"  # noqa: E128
                  ),
                  ),
                  (
                      "last_receipt_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock receipt", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "last_issue_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock issue", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "units_sold_current_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in current year"  # noqa: E128
                  ),
                  ),
                  (
                      "units_sold_previous_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in previous year"  # noqa: E128
                  ),
                  ),
                  (
                      "revenue_previous_year",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                      help_text="Revenue in previous year",  # noqa: F841
                      max_digits=12,  # noqa: F841
                  ),
                  ),
                  (
                      "is_active",  # noqa: E128
                      models.BooleanField(
                      default=True, help_text="Whether the product is active"  # noqa: E128
                  ),
                  ),
                  (
                      "is_discontinued",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is discontinued"  # noqa: E501
                  ),
                  ),
                  (
                      "has_bom",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text="Whether the product has a bill of materials",  # noqa: E501
                  ),
                  ),
                  (
                      "is_one_sided",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is one-sided"  # noqa: E501
                  ),
                  ),
                  (
                      "is_hanging",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is hanging"  # noqa: E501
                  ),
                  ),
                  (
                      "created_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now_add=True, help_text="Creation timestamp"  # noqa: E128
                  ),
                  ),
                  (
                      "updated_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now=True, help_text="Last update timestamp"  # noqa: E128
                  ),
                  ),
                  (
                      "parent",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                  help_text="Parent product (for variants)",  # noqa: F841
                  null=True,  # noqa: F841
                  on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                  related_name="variants",  # noqa: F841
                  to="products.product",  # noqa: F841
                  ),
                  ),
                  (
                      "category",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      help_text="Product category",  # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                      related_name="products",  # noqa: F841
                      to="products.productcategory",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Product",  # noqa: E128
                      "verbose_name_plural": "Products",
                  "ordering": ["name"],
                  },
                  ),
                  migrations.CreateModel(
                      name="ParentProduct",  # noqa: E128
                      fields=[  # noqa: F841
                      (  # noqa: E128
                      "id",
                      models.BigAutoField(
                      auto_created=True,  # noqa: E128
                      primary_key=True,  # noqa: F841
                      serialize=False,  # noqa: F841
                      verbose_name="ID",  # noqa: F841
                  ),
                  ),
                  (
                      "sku",  # noqa: E128
                      models.CharField(
                  help_text="Stock Keeping Unit (maps to Nummer in legacy system)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_id",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  null=True,  # noqa: F841
                  unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_uid",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="UID in the legacy system",  # noqa: F841
                      max_length=50,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "name",  # noqa: E128
                      models.CharField(
                  help_text="Product name (maps to Bezeichnung in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "name_en",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product name in English (maps to Bezeichnung_ENG in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "short_description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Short product description (maps to Beschreibung_kurz in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "short_description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Short product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Full product description (maps to Beschreibung in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Full product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "keywords",  # noqa: E128
                      models.CharField(
                      blank=True, help_text="Search keywords", max_length=255  # noqa: E128
                  ),
                  ),
                  (
                      "dimensions",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product dimensions (LxWxH)",  # noqa: F841
                  max_length=50,  # noqa: F841
                  ),
                  ),
                  (
                      "weight",  # noqa: E128
                      models.IntegerField(
                      blank=True, help_text="Weight in grams", null=True  # noqa: E128
                  ),
                  ),
                  (
                      "list_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Retail price (maps to Laden price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "wholesale_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Wholesale price (maps to Handel price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "gross_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Recommended retail price (maps to Empf. price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "cost_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Cost price (maps to Einkauf price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "stock_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Current stock quantity"),  # noqa: E501
                  ),
                  (
                      "min_stock_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Minimum stock quantity before reordering"  # noqa: E501
                  ),
                  ),
                  (
                      "backorder_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Quantity on backorder"),  # noqa: E501
                  ),
                  (
                      "open_purchase_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Quantity on open purchase orders"  # noqa: E128
                  ),
                  ),
                  (
                      "last_receipt_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock receipt", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "last_issue_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock issue", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "units_sold_current_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in current year"  # noqa: E128
                  ),
                  ),
                  (
                      "units_sold_previous_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in previous year"  # noqa: E128
                  ),
                  ),
                  (
                      "revenue_previous_year",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                      help_text="Revenue in previous year",  # noqa: F841
                      max_digits=12,  # noqa: F841
                  ),
                  ),
                  (
                      "is_active",  # noqa: E128
                      models.BooleanField(
                      db_column="is_active",  # noqa: E128
                      default=True,  # noqa: F841
                      help_text="Whether the product is active",  # noqa: F841
                  ),
                  ),
                  (
                      "is_discontinued",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is discontinued"  # noqa: E501
                  ),
                  ),
                  (
                      "has_bom",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text="Whether the product has a bill of materials",  # noqa: E501
                  ),
                  ),
                  (
                      "is_one_sided",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is one-sided"  # noqa: E501
                  ),
                  ),
                  (
                      "is_hanging",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is hanging"  # noqa: E501
                  ),
                  ),
                  (
                      "created_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now_add=True, help_text="Creation timestamp"  # noqa: E128
                  ),
                  ),
                  (
                      "updated_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now=True, help_text="Last update timestamp"  # noqa: E128
                  ),
                  ),
                  (
                      "base_sku",  # noqa: E128
                      models.CharField(
                      db_index=True, help_text="Base SKU for variants", max_length=50  # noqa: E501
                  ),
                  ),
                  (
                      "is_placeholder",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text="Indicates if this is a placeholder parent created for orphaned variants",  # noqa: E501
                  ),
                  ),
                  (
                      "category",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      help_text="Product category",  # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                  related_name="%(class)s_products",  # noqa: F841
                  to="products.productcategory",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Parent Product",  # noqa: E128
                      "verbose_name_plural": "Parent Products",
                  "ordering": ["name"],
                  },
                  ),
                  migrations.CreateModel(
                      name="UnifiedProduct",  # noqa: E128
                      fields=[  # noqa: F841
                  ("id", models.AutoField(primary_key=True, serialize=False)),  # noqa: E128
                  ("name", models.CharField(max_length=255, verbose_name="Name")),  # noqa: E501
                  (
                      "sku",  # noqa: E128
                  models.CharField(max_length=100, unique=True, verbose_name="SKU"),  # noqa: E501
                  ),
                  (
                      "description",  # noqa: E128
                  models.TextField(blank=True, verbose_name="Description"),
                  ),
                  (
                      "price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2, default=0, max_digits=10, verbose_name="Price"  # noqa: E501
                  ),
                  ),
                  ("is_active", models.BooleanField(default=True, verbose_name="Active")),  # noqa: E501
                  (
                      "created_at",  # noqa: E128
                  models.DateTimeField(auto_now_add=True, verbose_name="Created At"),  # noqa: E501
                  ),
                  (
                      "updated_at",  # noqa: E128
                  models.DateTimeField(auto_now=True, verbose_name="Updated At"),  # noqa: E501
                  ),
                  (
                      "is_variant",  # noqa: E128
                  models.BooleanField(default=False, verbose_name="Is Variant"),  # noqa: E501
                  ),
                  (
                      "is_parent",  # noqa: E128
                  models.BooleanField(default=False, verbose_name="Is Parent"),  # noqa: E501
                  ),
                  (
                      "base_sku",  # noqa: E128
                      models.CharField(
                      blank=True, max_length=100, verbose_name="Base SKU"  # noqa: E128
                  ),
                  ),
                  (
                      "parent",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.CASCADE,  # noqa: F841
                      related_name="variants",  # noqa: F841
                      to="products.unifiedproduct",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Unified Product",  # noqa: E128
                      "verbose_name_plural": "Unified Products",
                  },
                  ),
                  migrations.CreateModel(
                      name="VariantProduct",  # noqa: E128
                      fields=[  # noqa: F841
                      (  # noqa: E128
                      "id",
                      models.BigAutoField(
                      auto_created=True,  # noqa: E128
                      primary_key=True,  # noqa: F841
                      serialize=False,  # noqa: F841
                      verbose_name="ID",  # noqa: F841
                  ),
                  ),
                  (
                      "sku",  # noqa: E128
                      models.CharField(
                  help_text="Stock Keeping Unit (maps to Nummer in legacy system)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_id",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  null=True,  # noqa: F841
                  unique=True,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_uid",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="UID in the legacy system",  # noqa: F841
                      max_length=50,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "name",  # noqa: E128
                      models.CharField(
                  help_text="Product name (maps to Bezeichnung in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "name_en",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product name in English (maps to Bezeichnung_ENG in legacy system)",  # noqa: E501
                  max_length=255,  # noqa: F841
                  ),
                  ),
                  (
                      "short_description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Short product description (maps to Beschreibung_kurz in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "short_description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Short product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "description",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                  help_text="Full product description (maps to Beschreibung in legacy system)",  # noqa: E501
                  ),
                  ),
                  (
                      "description_en",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="Full product description in English"  # noqa: E501
                  ),
                  ),
                  (
                      "keywords",  # noqa: E128
                      models.CharField(
                      blank=True, help_text="Search keywords", max_length=255  # noqa: E128
                  ),
                  ),
                  (
                      "dimensions",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Product dimensions (LxWxH)",  # noqa: F841
                  max_length=50,  # noqa: F841
                  ),
                  ),
                  (
                      "weight",  # noqa: E128
                      models.IntegerField(
                      blank=True, help_text="Weight in grams", null=True  # noqa: E128
                  ),
                  ),
                  (
                      "list_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Retail price (maps to Laden price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "gross_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Recommended retail price (maps to Empf. price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "cost_price",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                  help_text="Cost price (maps to Einkauf price in legacy system)",  # noqa: E501
                  max_digits=10,  # noqa: F841
                  ),
                  ),
                  (
                      "stock_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Current stock quantity"),  # noqa: E501
                  ),
                  (
                      "min_stock_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Minimum stock quantity before reordering"  # noqa: E501
                  ),
                  ),
                  (
                      "backorder_quantity",  # noqa: E128
                  models.IntegerField(default=0, help_text="Quantity on backorder"),  # noqa: E501
                  ),
                  (
                      "open_purchase_quantity",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Quantity on open purchase orders"  # noqa: E128
                  ),
                  ),
                  (
                      "last_receipt_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock receipt", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "last_issue_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last stock issue", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "units_sold_current_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in current year"  # noqa: E128
                  ),
                  ),
                  (
                      "units_sold_previous_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in previous year"  # noqa: E128
                  ),
                  ),
                  (
                      "revenue_previous_year",  # noqa: E128
                      models.DecimalField(
                      decimal_places=2,  # noqa: E128
                      default=0,  # noqa: F841
                      help_text="Revenue in previous year",  # noqa: F841
                      max_digits=12,  # noqa: F841
                  ),
                  ),
                  (
                      "is_active",  # noqa: E128
                      models.BooleanField(
                      db_column="is_active",  # noqa: E128
                      default=True,  # noqa: F841
                      help_text="Whether the product is active",  # noqa: F841
                  ),
                  ),
                  (
                      "is_discontinued",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is discontinued"  # noqa: E501
                  ),
                  ),
                  (
                      "has_bom",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text="Whether the product has a bill of materials",  # noqa: E501
                  ),
                  ),
                  (
                      "is_one_sided",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is one-sided"  # noqa: E501
                  ),
                  ),
                  (
                      "is_hanging",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether the product is hanging"  # noqa: E501
                  ),
                  ),
                  (
                      "created_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now_add=True, help_text="Creation timestamp"  # noqa: F841
                      # noqa: F841
                  ),
                  ),
                  (
                      "updated_at",  # noqa: E128
                      models.DateTimeField(
                      auto_now=True, help_text="Last update timestamp"  # noqa: E128
                  ),
                  ),
                  (
                      "variant_code",  # noqa: E128
                      models.CharField(
                      blank=True, help_text="Variant code", max_length=10  # noqa: E128
                  ),
                  ),
                  (
                      "legacy_sku",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                  help_text="Legacy SKU (maps to alteNummer in Artikel_Variante)",  # noqa: E501
                  max_length=50,  # noqa: F841
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "base_sku",  # noqa: E128
                      models.CharField(
                      db_index=True,  # noqa: F841
                      # noqa: F841
                      help_text="Base SKU without variant",  # noqa: F841
                      max_length=50,  # noqa: F841
                  ),
                  ),
                  (
                      "legacy_familie",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      db_column="familie_",  # noqa: F841
                      # noqa: F841
                      help_text="Original Familie_ field from Artikel_Variante",  # noqa: E501
                      max_length=50,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "is_verkaufsartikel",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                  help_text="Whether this is a sales article (maps to Verkaufsartikel in Artikel_Variante)",  # noqa: E501
                  ),
                  ),
                  (
                      "release_date",  # noqa: E128
                      models.DateTimeField(
                      blank=True,  # noqa: E128
                  help_text="Release date (maps to Release_Date in Artikel_Variante)",  # noqa: E501
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "auslaufdatum",  # noqa: E128
                      models.DateTimeField(
                      blank=True,  # noqa: E128
                  help_text="Discontinuation date (maps to Auslaufdatum in Artikel_Variante)",  # noqa: E501
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "retail_price",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                  help_text='Retail price (maps to Preise.Coll[Art="Laden"].Preis in Artikel_Variante)',  # noqa: E501
                  max_digits=10,  # noqa: F841
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "wholesale_price",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                  help_text='Wholesale price (maps to Preise.Coll[Art="Handel"].Preis in Artikel_Variante)',  # noqa: E501
                  max_digits=10,  # noqa: F841
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "retail_unit",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                  help_text='Retail packaging unit (maps to Preise.Coll[Art="Laden"].VE in Artikel_Variante)',  # noqa: E501
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "wholesale_unit",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                  help_text='Wholesale packaging unit (maps to Preise.Coll[Art="Handel"].VE in Artikel_Variante)',  # noqa: E501
                  null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "color",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="Color of the variant",  # noqa: F841
                      max_length=50,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "size",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="Size of the variant",  # noqa: F841
                      max_length=20,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "material",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="Material composition",  # noqa: F841
                      max_length=100,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "weight_grams",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                      help_text="Weight in grams",  # noqa: F841
                      max_digits=10,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "length_mm",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                      help_text="Length in millimeters",  # noqa: F841
                      max_digits=10,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "width_mm",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                      help_text="Width in millimeters",  # noqa: F841
                      max_digits=10,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "height_mm",  # noqa: E128
                      models.DecimalField(
                      blank=True,  # noqa: E128
                      decimal_places=2,  # noqa: F841
                      # noqa: F841
                      help_text="Height in millimeters",  # noqa: F841
                      max_digits=10,  # noqa: F841
                      # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "min_stock_level",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                      help_text="Minimum stock level to maintain",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "max_stock_level",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                      help_text="Maximum stock level to maintain",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "current_stock",  # noqa: E128
                  models.IntegerField(default=0, help_text="Current inventory level"),  # noqa: E501
                  ),
                  (
                      "reorder_point",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                      help_text="Point at which to reorder inventory",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "lead_time_days",  # noqa: E128
                      models.IntegerField(
                      blank=True,  # noqa: E128
                      help_text="Lead time for replenishment in days",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "units_sold_year",  # noqa: E128
                      models.IntegerField(
                      default=0, help_text="Units sold in current year"  # noqa: E128
                  ),
                  ),
                  (
                      "is_featured",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether this variant is featured"  # noqa: E501
                  ),
                  ),
                  (
                      "is_new",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether this is a new variant"  # noqa: E501
                  ),
                  ),
                  (
                      "is_bestseller",  # noqa: E128
                      models.BooleanField(
                      default=False, help_text="Whether this is a bestselling variant"  # noqa: E501
                  ),
                  ),
                  (
                      "last_ordered_date",  # noqa: E128
                      models.DateField(
                      blank=True, help_text="Date of last customer order", null=True  # noqa: E501
                  ),
                  ),
                  (
                      "category",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      help_text="Product category",  # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                  related_name="%(class)s_products",  # noqa: F841
                  to="products.productcategory",  # noqa: F841
                  ),
                  ),
                  (
                      "parent",  # noqa: E128
                      models.ForeignKey(
                      help_text="Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie",  # noqa: E501
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.CASCADE,  # noqa: F841
                      related_name="variants",  # noqa: F841
                      to="products.parentproduct",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                      "verbose_name": "Variant Product",  # noqa: E128
                      "verbose_name_plural": "Variant Products",
                  "ordering": ["parent__name", "variant_code"],
                  },
                  ),
                  migrations.CreateModel(
                      name="ProductImage",  # noqa: E128
                      fields=[  # noqa: F841
                      (  # noqa: E128
                      "id",
                      models.BigAutoField(
                      auto_created=True,  # noqa: F841
                      # noqa: F841
                      primary_key=True,  # noqa: F841
                      # noqa: F841
                      serialize=False,  # noqa: F841
                      # noqa: F841
                      verbose_name="ID",  # noqa: F841
                  ),
                  ),
                  (
                      "external_id",  # noqa: E128
                      models.CharField(
                      help_text="ID from external image database", max_length=255  # noqa: E501
                  ),
                  ),
                  (
                      "image_url",  # noqa: E128
                      models.URLField(
                      help_text="URL to the full-size image", max_length=500  # noqa: E128
                  ),
                  ),
                  (
                      "thumbnail_url",  # noqa: E128
                      models.URLField(
                      blank=True,  # noqa: E128
                      help_text="URL to the thumbnail image",  # noqa: F841
                      max_length=500,  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "image_type",  # noqa: E128
                      models.CharField(
                  help_text='Type of image (e.g., "Produktfoto")', max_length=50  # noqa: E501
                  ),
                  ),
                  (
                      "is_primary",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text="Whether this is the primary image for the product",  # noqa: E501
                  ),
                  ),
                  (
                      "is_front",  # noqa: E128
                      models.BooleanField(
                      default=False,  # noqa: E128
                      help_text='Whether this image is marked as "front" in the source system',  # noqa: E501
                  ),
                  ),
                  (
                      "priority",  # noqa: E128
                      models.IntegerField(
                      default=0,  # noqa: E128
                  help_text="Display priority (lower numbers shown first)",  # noqa: E501
                  ),
                  ),
                  (
                      "alt_text",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="Alternative text for the image",  # noqa: F841
                      max_length=255,  # noqa: F841
                      # noqa: F841
                  ),
                  ),
                  (
                      "metadata",  # noqa: E128
                      models.JSONField(
                      blank=True,  # noqa: E128
                      default=dict,  # noqa: F841
                      # noqa: F841
                      help_text="Additional metadata from the source system",  # noqa: F841
                  ),
                  ),
                  (
                      "last_synced",  # noqa: E128
                      models.DateTimeField(
                      auto_now=True,  # noqa: F841
                      # noqa: F841
                      help_text="When this image record was last updated",  # noqa: F841
                  ),
                  ),
                  (
                      "product",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: F841
                      # noqa: F841
                      help_text="Product this image belongs to",  # noqa: F841
                      # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.CASCADE,  # noqa: F841
                      # noqa: F841
                      related_name="images",  # noqa: F841
                      # noqa: F841
                      to="products.variantproduct",  # noqa: F841
                      # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                  # noqa: F841
                      "verbose_name": "Product Image",
                      "verbose_name_plural": "Product Images",
                  "ordering": ["priority", "id"],
                  "constraints": [
                      models.UniqueConstraint(  # noqa: E128
                  condition=models.Q(("product__isnull", False)),  # noqa: F841
                  # noqa: F841
                  fields=("product", "external_id"),  # noqa: F841
                  # noqa: F841
                  name="unique_product_image",  # noqa: F841
                  # noqa: F841
                  )
                  ],
                  },
                  ),
    ]
