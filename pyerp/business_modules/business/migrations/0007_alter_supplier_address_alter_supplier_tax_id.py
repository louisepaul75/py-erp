# Generated by Django 5.1.8 on 2025-04-15 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0006_supplier_bic_supplier_iban"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supplier",
            name="address",
            field=models.TextField(blank=True, null=True, verbose_name="Address"),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="tax_id",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Tax ID"
            ),
        ),
    ]
