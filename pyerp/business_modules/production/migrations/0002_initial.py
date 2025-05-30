# Generated by Django 5.1.7 on 2025-03-28 18:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("production", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productionorderitem",
            name="parent_product",
            field=models.ForeignKey(
                blank=True,
                help_text="Reference to parent product (maps to Art_Nr in WerksauftrPos)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="production_items",
                to="products.parentproduct",
                verbose_name="Parent Product",
            ),
        ),
        migrations.AddField(
            model_name="productionorderitem",
            name="production_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="production.productionorder",
                verbose_name="Production Order",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="productionorderitem",
            unique_together={("production_order", "item_number")},
        ),
    ]
