"use client"

import { useQuery } from "@tanstack/react-query"
import type { CurrencyHistory, TimeRange } from "@/types/settings/currency-history"

// Hilfsfunktion zum Generieren von Mock-Daten für historische Kurse
const generateHistoricalData = (
  currencyId: string,
  currencyCode: string,
  timeRange: TimeRange,
  baseRate: number,
): CurrencyHistory => {
  const now = new Date()
  const history: { date: string; rate: number }[] = []

  // Anzahl der Datenpunkte je nach Zeitraum
  let points = 0
  let intervalHours = 0

  switch (timeRange) {
    case "day":
      points = 24
      intervalHours = 1
      break
    case "week":
      points = 7
      intervalHours = 24
      break
    case "month":
      points = 30
      intervalHours = 24
      break
    case "quarter":
      points = 90
      intervalHours = 24
      break
    case "year":
      points = 12
      intervalHours = 24 * 30
      break
  }

  // Volatilität je nach Währung
  const volatility = currencyCode === "EUR" ? 0 : currencyCode === "JPY" ? 0.005 : 0.01

  // Generiere Datenpunkte
  for (let i = points - 1; i >= 0; i--) {
    const date = new Date(now.getTime() - i * intervalHours * 60 * 60 * 1000)

    // Zufällige Schwankung um den Basiskurs
    const randomFactor = 1 + (Math.random() - 0.5) * volatility * 2
    const rate = baseRate * randomFactor

    history.push({
      date: date.toISOString(),
      rate: Number(rate.toFixed(4)),
    })
  }

  return {
    currencyId,
    currencyCode,
    history,
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

