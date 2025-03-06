from rest_framework import serializers


class DummySalesSerializer(serializers.Serializer):
    """
    A dummy sales serializer to make the API documentation work.
    This is just a placeholder until real models are implemented.
    """
    id = serializers.IntegerField(read_only=True)  # noqa: F841
    name = serializers.CharField(max_length=100, required=False)  # noqa: F841
    description = serializers.CharField(max_length=500, required=False)  # noqa: F841
    created_at = serializers.DateTimeField(read_only=True)  # noqa: F841
