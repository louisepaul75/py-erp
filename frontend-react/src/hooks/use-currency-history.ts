"use client"

import { useQuery } from "@tanstack/react-query"
import type { CurrencyHistory, TimeRange } from "@/types/settings/currency-history"
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";

// Hilfsfunktion zum Generieren von Mock-Daten für historische Kurse
const generateHistoricalData = async (
  currencyId: string,
  currencyCode: string,
  timeRange: TimeRange,
  baseRate: number,
): Promise<CurrencyHistory> => {
  try {
    const token = await authService.getToken()
    const baseCurrency = "EUR"
    const endpoint = `/currency/historical-rates-calc/?currency=${currencyCode}&range=${timeRange}&base=${baseCurrency}`
    
    const response = await fetch(API_URL + endpoint, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    })

    if (!response.ok) {
      console.error("API Error:", response.status, await response.text())
      throw new Error(`Failed to fetch historical rates: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    console.log("HISTORICAL DATA", data)
    const history = data.data.map((item: { date: string; rate: number }) => ({
      date: item.date,
      rate: Number(item.rate.toFixed(4)),
    }))

    return {
      currencyId,
      currencyCode,
      history,
    }
  } catch (error) {
    console.error("Error fetching historical data:", error)
    return {
      currencyId,
      currencyCode,
      history: [],
    }
  }
}

// Funktion zum Abrufen historischer Kursdaten
const fetchCurrencyHistory = async (
  currencyId: string,
  currencyCode: string,
  timeRange: TimeRange,
  baseRate: number,
): Promise<CurrencyHistory> => {
  // Simuliere API-Aufruf
  await new Promise((resolve) => setTimeout(resolve, 800))
  return generateHistoricalData(currencyId, currencyCode, timeRange, baseRate)
}

// Hook für historische Kursdaten
export function useCurrencyHistory(
  currencyId: string | undefined,
  currencyCode: string | undefined,
  timeRange: TimeRange,
  baseRate = 1,
) {
  return useQuery({
    queryKey: ["currencyHistory", currencyId, timeRange],
    queryFn: () => fetchCurrencyHistory(currencyId || "0", currencyCode || "EUR", timeRange, baseRate),
    enabled: !!currencyId && !!currencyCode,
    staleTime: 5 * 60 * 1000, // 5 Minuten
  })
}

