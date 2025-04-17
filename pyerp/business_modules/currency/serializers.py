# serializers.py

from rest_framework import serializers
from .models import Currency, ExchangeRate, CalculatedExchangeRate

class CalculatedExchangeRateUpdateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=3)
    name = serializers.CharField(max_length=100, required=False)  # still just for display
    realTimeRate = serializers.DecimalField(max_digits=20, decimal_places=6)
    calculationRate = serializers.DecimalField(max_digits=20, decimal_places=6)

    def update(self, instance, validated_data):
        instance.rate = validated_data.get("realTimeRate")
        instance.calculation_rate_stored = validated_data.get("calculationRate")
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "code": instance.target_currency.code,
            "name": instance.target_currency.name,
            "realTimeRate": instance.rate,
            "calculationRate": instance.calculation_rate_stored,
            "date": instance.date,
        }

    
class CalculatedExchangeRateSerializer(serializers.ModelSerializer):
    base_currency = serializers.StringRelatedField()
    target_currency = serializers.StringRelatedField()

    class Meta:
        model = CalculatedExchangeRate
        fields = [
            'base_currency',
            'target_currency',
            'rate',
            'calculation_rate_stored',
            'date'
        ]


class CalculatedExchangeRateCustomInputSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=3)
    name = serializers.CharField(max_length=100)
    realTimeRate = serializers.DecimalField(max_digits=20, decimal_places=6)
    calculationRate = serializers.DecimalField(max_digits=20, decimal_places=6)

    def create(self, validated_data):
        try:
            base_currency = Currency.objects.get(code="EUR")
        except Currency.DoesNotExist:
            raise serializers.ValidationError("Base currency 'EUR' is missing.")

        code = validated_data["code"].upper()
        name = validated_data["name"]

        # Ensure the target currency exists (or create it)
        target_currency, _ = Currency.objects.get_or_create(
            code=code,
            defaults={"name": name},
        )

        # Check if the combination already exists
        if CalculatedExchangeRate.objects.filter(
            base_currency=base_currency,
            target_currency=target_currency
        ).exists():
            raise serializers.ValidationError(
                {"detail": f"A calculated exchange rate for {code} already exists."}
            )

        # Create the new record
        instance = CalculatedExchangeRate.objects.create(
            base_currency=base_currency,
            target_currency=target_currency,
            rate=validated_data["realTimeRate"],
            calculation_rate_stored=validated_data["calculationRate"],
        )

        return instance
    
    def to_representation(self, instance):
        return {
            "code": instance.target_currency.code,
            "name": instance.target_currency.name,
            "realTimeRate": instance.rate,
            "calculationRate": instance.calculation_rate_stored,
            "date": instance.date,
        }

class ExchangeRateSerializer(serializers.ModelSerializer):
    target_currency = serializers.StringRelatedField()

    class Meta:
        model = ExchangeRate
        fields = ['target_currency', 'rate', 'date']

class CurrencyWithRatesSerializer(serializers.ModelSerializer):
    exchange_rates = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ['code', 'name', 'exchange_rates']

    def get_exchange_rates(self, obj):
        rates = ExchangeRate.objects.filter(base_currency=obj)
        return ExchangeRateSerializer(rates, many=True).data
