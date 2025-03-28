"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Currency, CurrencyInput, CurrencyUpdateInput } from "@/types/settings/currency"
import { useState } from "react"

// Mock API functions - replace with actual API calls
const fetchCurrencies = async (): Promise<Currency[]> => {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 500))

  // Return mock data
  return [
    {
      id: "1",
      code: "EUR",
      name: "Euro",
      realTimeRate: 1.0,
      calculationRate: 1.0,
      lastUpdated: new Date().toISOString(),
    },
    {
      id: "2",
      code: "USD",
      name: "US Dollar",
      realTimeRate: 0.9234,
      calculationRate: 0.92,
      lastUpdated: new Date().toISOString(),
    },
    {
      id: "3",
      code: "GBP",
      name: "British Pound",
      realTimeRate: 1.1756,
      calculationRate: 1.18,
      lastUpdated: new Date().toISOString(),
    },
    {
      id: "4",
      code: "JPY",
      name: "Japanese Yen",
      realTimeRate: 0.0061,
      calculationRate: 0.006,
      lastUpdated: new Date().toISOString(),
    },
  ]
}

const addCurrency = async (currency: CurrencyInput): Promise<Currency> => {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 1000))

  return {
    id: Math.random().toString(36).substring(2, 9),
    ...currency,
    lastUpdated: new Date().toISOString(),
  }
}

const updateCurrency = async (currency: CurrencyUpdateInput): Promise<Currency> => {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 1000))

  return {
    ...currency,
    lastUpdated: new Date().toISOString(),
  }
}

const deleteCurrency = async (id: string): Promise<void> => {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 1000))
}

const fetchExchangeRate = async (currencyCode: string): Promise<number> => {
  // Simulate API call to get exchange rate
  await new Promise((resolve) => setTimeout(resolve, 1000))

  // Wenn es sich um EUR handelt, ist der Kurs immer 1
  if (currencyCode === "EUR") return 1.0

  // Return a random rate between 0.5 and 1.5 for other currencies
  return 0.5 + Math.random()
}

// Custom hooks
export function useCurrencies() {
  return useQuery({
    queryKey: ["currencies"],
    queryFn: fetchCurrencies,
  })
}

export function useAddCurrency() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: addCurrency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
    },
  })
}

export function useUpdateCurrency() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateCurrency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
    },
  })
}

export function useDeleteCurrency() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteCurrency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
    },
  })
}

export function useFetchExchangeRate() {
  const [isLoading, setIsLoading] = useState(false)

  const fetchRate = async (currencyCode: string) => {
    setIsLoading(true)
    try {
      return await fetchExchangeRate(currencyCode)
    } finally {
      setIsLoading(false)
    }
  }

  return { fetchRate, isLoading }
}

