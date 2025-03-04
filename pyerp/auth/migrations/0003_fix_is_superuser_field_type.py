from django.db import migrations, models

def convert_to_boolean(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    for user in User.objects.all():
        user.is_superuser = bool(user.is_superuser)
        user.save()

def convert_to_smallint(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    for user in User.objects.all():
        user.is_superuser = 1 if user.is_superuser else 0
        user.save()

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0002_fix_is_superuser_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            convert_to_boolean,
            convert_to_smallint
        ),
    ] 