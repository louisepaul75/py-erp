from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from django.http import HttpResponse, JsonResponse
from .models import Currency, CalculatedExchangeRate, CalculatedExchangeRate
from .serializers import CurrencyWithRatesSerializer, CalculatedExchangeRateUpdateSerializer, CalculatedExchangeRateCustomInputSerializer, CalculatedExchangeRateSerializer
import requests
from datetime import datetime, timedelta

class CalculatedExchangeRateUpdateAPIView(APIView):
    def patch(self, request):
        print("patch",request.data )
        serializer = CalculatedExchangeRateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get("code", "").upper()
            try:
                instance = CalculatedExchangeRate.objects.get(target_currency__code=code)
            except CalculatedExchangeRate.DoesNotExist:
                return Response({"error": f"No CalculatedExchangeRate found for currency code '{code}'."}, status=status.HTTP_404_NOT_FOUND)

            updated_instance = serializer.update(instance, serializer.validated_data)
            return Response(serializer.to_representation(updated_instance), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class HistoricalExchangeRatesCalculatedAPIView(APIView):
    def get(self, request):
        try:
            # Parameters from query string
            target_currency = request.GET.get('currency', 'CNY')
            time_range = request.GET.get('range', 'month')
            base_currency = request.GET.get('base', 'USD')

            # Determine points and interval
            now = datetime.now()
            time_settings = {
                "day": (24, timedelta(hours=1)),
                "week": (7, timedelta(days=1)),
                "month": (30, timedelta(days=1)),
                "quarter": (90, timedelta(days=1)),
                "year": (12, timedelta(days=30)),
            }

            if time_range not in time_settings:
                return Response({"error": "Invalid time range."}, status=400)

            points, interval = time_settings[time_range]

            results = []

            for i in range(points):
                date = now - interval * i
                date_str = date.strftime("%Y-%m-%d")
                url = f"https://api.frankfurter.app/{date_str}"
                params = {
                    "from": base_currency,
                    "to": target_currency
                }
                res = requests.get(url, params=params)
                if res.status_code != 200:
                    continue
                data = res.json()
                rate = data["rates"].get(target_currency)
                if rate:
                    results.append({
                        "date": date_str,
                        "rate": rate,
                    })

            results.reverse()  # So data is in chronological order
            return Response({
                "base": base_currency,
                "currency": target_currency,
                "range": time_range,
                "data": results
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class CalculatedExchangeRateListAPIView(generics.ListAPIView):
    queryset = CalculatedExchangeRate.objects.all()
    serializer_class = CalculatedExchangeRateSerializer

class CalculatedExchangeRateListCreateAPIView(generics.ListCreateAPIView):
    queryset = CalculatedExchangeRate.objects.all()
    serializer_class = CalculatedExchangeRateCustomInputSerializer

class CurrencyWithRatesListAPIView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencyWithRatesSerializer

def index(request):
    return HttpResponse("Currency app is working!")
