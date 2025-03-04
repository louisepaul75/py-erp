from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(
                default=False,
                help_text='Designates that this user has all permissions without explicitly assigning them.',
                verbose_name='superuser status'
            ),
        ),
    ] 