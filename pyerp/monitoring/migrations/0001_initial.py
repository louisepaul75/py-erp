
import django.utils.timezone  # noqa: F401
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True  # noqa: F841

    dependencies = []  # noqa: F841

    operations = [  # noqa: F841
        migrations.CreateModel(
        name="HealthCheckResult",  # noqa: E128
        fields=[  # noqa: F841
        (  # noqa: E128
        "id",
        models.BigAutoField(
        auto_created=True,  # noqa: F841
        primary_key=True,  # noqa: F841
        serialize=False,  # noqa: F841
        verbose_name="ID",  # noqa: F841
    ),
                  ),
                  (
                      "component",  # noqa: E128
                      models.CharField(
                      choices=[  # noqa: E128
                  ("database", "Database"),
                  ("legacy_erp", "Legacy ERP"),
                  ("pictures_api", "Pictures API"),
                  ("database_validation", "Database Validation"),
                  ],
                  help_text="System component being checked",  # noqa: F841
                  max_length=50,  # noqa: F841
                  verbose_name="Component",  # noqa: F841
                  ),
                  ),
                  (
                      "status",  # noqa: E128
                      models.CharField(
                      choices=[  # noqa: F841
                      # noqa: F841
                  ("success", "Success"),
                  ("warning", "Warning"),
                  ("error", "Error"),
                  ],
                  help_text="Health check result status",  # noqa: F841
                  max_length=20,  # noqa: F841
                  # noqa: F841
                  verbose_name="Status",  # noqa: F841
                  ),
                  ),
                  (
                      "timestamp",  # noqa: E128
                      models.DateTimeField(
                      default=django.utils.timezone.now,  # noqa: F841
                      # noqa: F841
                      help_text="When the health check was performed",  # noqa: F841
                      verbose_name="Timestamp",  # noqa: F841
                  ),
                  ),
                  (
                      "details",  # noqa: E128
                      models.TextField(
                      blank=True,  # noqa: E128
                      help_text="Additional details about the health check result",  # noqa: E501
                      null=True,  # noqa: F841
                      verbose_name="Details",  # noqa: F841
                  ),
                  ),
                  (
                      "response_time",  # noqa: E128
                      models.FloatField(
                      blank=True,  # noqa: F841
                      # noqa: F841
                      help_text="Time taken to complete the health check in milliseconds",  # noqa: E501
                      # noqa: E501, F841
                      null=True,  # noqa: F841
                      # noqa: F841
                  verbose_name="Response Time (ms)",  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                  # noqa: F841
                      "verbose_name": "Health Check Result",
                      "verbose_name_plural": "Health Check Results",
                  "ordering": ["-timestamp"],
                  "indexes": [
                      models.Index(  # noqa: E128
                  fields=["component", "-timestamp"],  # noqa: F841
                  # noqa: F841
                  name="monitoring__compone_c08af6_idx",  # noqa: F841
                  # noqa: F841
                  )
                  ],
                  },
                  ),
    ]
