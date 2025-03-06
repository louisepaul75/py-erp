from rest_framework import serializers


class DummySalesSerializer(serializers.Serializer):
    """
    A dummy sales serializer to make the API documentation work.
    This is just a placeholder until real models are implemented.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(max_length=500, required=False)
    created_at = serializers.DateTimeField(read_only=True)
