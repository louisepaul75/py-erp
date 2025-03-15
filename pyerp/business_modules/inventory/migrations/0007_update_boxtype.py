from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_remove_storage_location'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productstorage",
            options={
                "verbose_name": "Product Storage",
                "verbose_name_plural": "Product Storage",
            },
        ),
        migrations.RenameIndex(
            model_name="productstorage",
            new_name="inventory_p_product_103f35_idx",
            old_name="inventory_p_product_801eb4_idx",
        ),
        migrations.RenameIndex(
            model_name="productstorage",
            new_name="inventory_p_reserva_11387a_idx",
            old_name="inventory_p_reserva_801eb4_idx",
        ),
    ] 