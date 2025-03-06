import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HealthCheckResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "component",
                    models.CharField(
                        choices=[
                            ("database", "Database"),
                            ("legacy_erp", "Legacy ERP"),
                            ("pictures_api", "Pictures API"),
                            ("database_validation", "Database Validation"),
                        ],
                        help_text="System component being checked",
                        max_length=50,
                        verbose_name="Component",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("warning", "Warning"),
                            ("error", "Error"),
                        ],
                        help_text="Health check result status",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="When the health check was performed",
                        verbose_name="Timestamp",
                    ),
                ),
                (
                    "details",
                    models.TextField(
                        blank=True,
                        help_text="Additional details about the health check result",
                        null=True,
                        verbose_name="Details",
                    ),
                ),
                (
                    "response_time",
                    models.FloatField(
                        blank=True,
                        help_text="Time taken to complete the health check in milliseconds",  # noqa: E501
                        null=True,
                        verbose_name="Response Time (ms)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Health Check Result",
                "verbose_name_plural": "Health Check Results",
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["component", "-timestamp"],
                        name="monitoring__compone_c08af6_idx",
                    )
                ],
            },
        ),
    ]
