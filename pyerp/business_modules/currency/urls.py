from django.urls import path
from .views import CurrencyWithRatesListAPIView, CalculatedExchangeRateUpdateAPIView, HistoricalExchangeRatesCalculatedAPIView, CalculatedExchangeRateListCreateAPIView, index, CalculatedExchangeRateListAPIView

app_name = 'currency_api'

urlpatterns = [
    path('', index, name='currency-index'),
    path('currencies-with-rates/', CurrencyWithRatesListAPIView.as_view(), name='currencies-with-rates'),
    path('calculated-rates/', CalculatedExchangeRateListCreateAPIView.as_view(), name='calculated-exchange-rate-list-create'),
    path('calculated-rates-list/', CalculatedExchangeRateListAPIView.as_view(), name='calculated-rates'),
    path('historical-rates-calc/', HistoricalExchangeRatesCalculatedAPIView.as_view(), name='calculated-rates'),
    path('calculated-rates/update/', CalculatedExchangeRateUpdateAPIView.as_view(), name='calculated-rate-update'),
]
