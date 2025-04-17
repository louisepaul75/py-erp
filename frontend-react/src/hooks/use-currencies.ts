"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Currency, CurrencyList, CurrencyInput, CurrencyUpdateInput } from "@/types/settings/currency"
import { useState } from "react"
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";

// Mock API functions - replace with actual API calls
const fetchCurrencies = async (): Promise<Currency[]> => {
  const token = await authService.getToken();
  const endpoint = `/currency/calculated-rates-list/`; 
  const response = await fetch(API_URL + endpoint, {
    method: "GET", // Use GET to retrieve the list
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(`Failed to fetch currencies: ${response.status} ${response.statusText}`);
  }
  const data = await response.json()

  const compactRates = data.results.map((item, index) => {
    const [code, name] = item.target_currency.split(" - ");
    console.log("RESPONSE", item)
  
    return {
      id: (index + 1).toString(), 
      code,
      name,
      realTimeRate: parseFloat(item.rate),
      calculationRate: parseFloat(item.calculation_rate_stored),
      lastUpdated: item.date,
    };
  });
  
  return compactRates
}

const fetchCurrenciesList = async (): Promise<any> => {
  const token = await authService.getToken();
  const endpoint = `/currency/currencies-with-rates/`; 
  const response = await fetch(API_URL + endpoint, {
    method: "GET", // Use GET to retrieve the list
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(`Failed to fetch currencies: ${response.status} ${response.statusText}`);
  }
  const data = await response.json()
  return data.results as CurrencyList
};

const addCurrency = async (currency: CurrencyInput): Promise<any> => {
  const token = await authService.getToken();
  const endpoint = `/currency/calculated-rates/`;

  const response = await fetch(API_URL + endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(currency),
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(`Failed to submit rate: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() ;

}

const updateCurrency = async (currency: CurrencyUpdateInput): Promise<Currency> => {
  console.log("updateCurrency", currency)
  const token = await authService.getToken();
  const endpoint = `/currency/calculated-rates/update/`;

  const response = await fetch(API_URL + endpoint, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(currency),
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(`Failed to update rate: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();

  return {
    ...data,
    lastUpdated: new Date().toISOString(),
  };
};

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

export function useCurrenciesList() {
  return useQuery({
    queryKey: ["currencies-list"],
    queryFn: fetchCurrenciesList,
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

