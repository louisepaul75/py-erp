
import django.db.models.deletion  # noqa: F401
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True  # noqa: F841

    dependencies = [  # noqa: F841
                    ("contenttypes", "0002_remove_content_type_name"),
                    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [  # noqa: F841
        migrations.CreateModel(
        name="AuditLog",  # noqa: E128
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
                      "timestamp",  # noqa: E128
                      models.DateTimeField(
                      auto_now_add=True, help_text="When the event occurred"  # noqa: F841
                      # noqa: F841
                  ),
                  ),
                  (
                      "event_type",  # noqa: E128
                      models.CharField(
                      choices=[  # noqa: F841
                      # noqa: F841
                  ("login", "Login"),
                  ("logout", "Logout"),
                  ("login_failed", "Login Failed"),
                  ("password_change", "Password Change"),
                  ("password_reset", "Password Reset"),
                  ("user_created", "User Created"),
                  ("user_updated", "User Updated"),
                  ("user_deleted", "User Deleted"),
                  ("permission_change", "Permission Change"),
                  ("data_access", "Data Access"),
                  ("data_change", "Data Change"),
                  ("system_error", "System Error"),
                  ("other", "Other"),
                  ],
                  help_text="Type of event being logged",  # noqa: F841
                  max_length=50,  # noqa: F841
                  ),
                  ),
                  ("message", models.TextField(help_text="Description of the event")),  # noqa: E501
                  (
                      "username",  # noqa: E128
                      models.CharField(
                      blank=True,  # noqa: E128
                      help_text="Username as a backup if user record is deleted",  # noqa: E501
                      max_length=150,  # noqa: F841
                  ),
                  ),
                  (
                      "ip_address",  # noqa: E128
                      models.GenericIPAddressField(
                      blank=True,  # noqa: E128
                      help_text="IP address where the event originated",  # noqa: F841
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "user_agent",  # noqa: E128
                      models.TextField(
                      blank=True, help_text="User agent/browser information"  # noqa: E128
                  ),
                  ),
                  (
                      "object_id",  # noqa: E128
                      models.CharField(
                      blank=True, help_text="ID of related object", max_length=255  # noqa: E501
                  ),
                  ),
                  (
                      "additional_data",  # noqa: E128
                      models.JSONField(
                      blank=True,  # noqa: E128
                      help_text="Additional event-specific data stored as JSON",  # noqa: E501
                      null=True,  # noqa: F841
                  ),
                  ),
                  (
                      "uuid",  # noqa: E128
                      models.UUIDField(
                      default=uuid.uuid4,  # noqa: F841
                      # noqa: F841
                      editable=False,  # noqa: F841
                      # noqa: F841
                      help_text="Unique identifier for this audit event",  # noqa: F841
                      unique=True,  # noqa: F841
                      # noqa: F841
                  ),
                  ),
                  (
                      "content_type",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: E128
                      help_text="Type of object this event relates to",  # noqa: F841
                      null=True,  # noqa: F841
                      on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                      to="contenttypes.contenttype",  # noqa: F841
                  ),
                  ),
                  (
                      "user",  # noqa: E128
                      models.ForeignKey(
                      blank=True,  # noqa: F841
                      # noqa: F841
                  help_text="User who triggered the event (if applicable)",  # noqa: E501
                  # noqa: E501, F841
                  null=True,  # noqa: F841
                  # noqa: F841
                  on_delete=django.db.models.deletion.SET_NULL,  # noqa: F841
                  # noqa: F841
                  related_name="audit_logs",  # noqa: F841
                  # noqa: F841
                  to=settings.AUTH_USER_MODEL,  # noqa: F841
                  # noqa: F841
                  ),
                  ),
                  ],
                  options={  # noqa: F841
                  # noqa: F841
                      "verbose_name": "Audit Log",
                      "verbose_name_plural": "Audit Logs",
                  "ordering": ["-timestamp"],
                  "indexes": [
                      models.Index(  # noqa: E128
                  fields=["timestamp"], name="core_auditl_timesta_80074f_idx"  # noqa: E501
                  ),
                  models.Index(
                  fields=["event_type"], name="core_auditl_event_t_04b2f0_idx"  # noqa: E501
                  ),
                  models.Index(
                  fields=["username"], name="core_auditl_usernam_6bebd7_idx"  # noqa: E501
                  ),
                  models.Index(
                  fields=["ip_address"], name="core_auditl_ip_addr_d66782_idx"  # noqa: E501
                  ),
                  models.Index(
                  fields=["content_type", "object_id"],  # noqa: F841
                  # noqa: F841
                  name="core_auditl_content_fec0c4_idx",  # noqa: F841
                  # noqa: F841
                  ),
                  ],
                  },
                  ),
    ]
