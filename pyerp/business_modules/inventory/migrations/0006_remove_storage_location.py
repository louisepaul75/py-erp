from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_boxtype_update'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='box',
                    name='storage_location',
                ),
            ],
            database_operations=[],
        ),
    ] 