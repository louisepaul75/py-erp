from rest_framework import viewsets, permissions, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import EmailLog, EmailEvent


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model."""

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "message_id",
            "subject",
            "from_email",
            "to_email",
            "status",
            "esp",
            "opens",
            "clicks",
            "created_at",
            "sent_at",
            "delivered_at",
            "error_message",
        ]
        read_only_fields = fields


class EmailEventSerializer(serializers.ModelSerializer):
    """Serializer for EmailEvent model."""

    class Meta:
        model = EmailEvent
        fields = [
            "id",
            "email_log",
            "event_type",
            "timestamp",
            "ip_address",
            "user_agent",
            "data",
        ]
        read_only_fields = fields


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing email logs."""

    queryset = EmailLog.objects.all().order_by("-created_at")
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "esp", "created_at", "sent_at"]
    search_fields = ["subject", "from_email", "to_email", "message_id"]
    ordering_fields = ["created_at", "sent_at", "subject", "status"]

    @action(detail=True, methods=["get"])
    def events(self, request, pk=None):
        """Get events for a specific email log."""
        email_log = self.get_object()
        events = email_log.events.all().order_by("-timestamp")
        serializer = EmailEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get email statistics."""
        total = EmailLog.objects.count()
        sent = EmailLog.objects.filter(status=EmailLog.STATUS_SENT).count()
        delivered = EmailLog.objects.filter(status=EmailLog.STATUS_DELIVERED).count()
        opened = EmailLog.objects.filter(status=EmailLog.STATUS_OPENED).count()
        clicked = EmailLog.objects.filter(status=EmailLog.STATUS_CLICKED).count()
        bounced = EmailLog.objects.filter(status=EmailLog.STATUS_BOUNCED).count()
        failed = EmailLog.objects.filter(status=EmailLog.STATUS_FAILED).count()

        return Response(
            {
                "total": total,
                "sent": sent,
                "delivered": delivered,
                "opened": opened,
                "clicked": clicked,
                "bounced": bounced,
                "failed": failed,
                "delivery_rate": (delivered / sent * 100) if sent > 0 else 0,
                "open_rate": (opened / delivered * 100) if delivered > 0 else 0,
                "click_rate": (clicked / opened * 100) if opened > 0 else 0,
                "bounce_rate": (bounced / sent * 100) if sent > 0 else 0,
                "failure_rate": (failed / total * 100) if total > 0 else 0,
            }
        )


class EmailEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing email events."""

    queryset = EmailEvent.objects.all().order_by("-timestamp")
    serializer_class = EmailEventSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["event_type", "timestamp", "email_log"]
    search_fields = ["event_type", "ip_address", "user_agent"]
    ordering_fields = ["timestamp", "event_type"]
