# Generated by Django 5.1.8 on 2025-04-15 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0005_alter_supplier_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="bic",
            field=models.CharField(
                blank=True, max_length=11, null=True, verbose_name="BIC (Swift)"
            ),
        ),
        migrations.AddField(
            model_name="supplier",
            name="iban",
            field=models.CharField(
                blank=True, max_length=34, null=True, verbose_name="IBAN"
            ),
        ),
    ]
