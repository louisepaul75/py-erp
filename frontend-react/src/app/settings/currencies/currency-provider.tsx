"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import type { Currency } from "@/types/settings/currency";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface CurrencyContextType {
  selectedCurrency: Currency | null;
  setSelectedCurrency: (currency: Currency | null) => void;
  isAddingCurrency: boolean;
  setIsAddingCurrency: (isAdding: boolean) => void;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(
  undefined
);

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [selectedCurrency, setSelectedCurrency] = useState<Currency | null>(
    null
  );
  const [isAddingCurrency, setIsAddingCurrency] = useState(false);

  return (
    <CurrencyContext.Provider
      value={{
        selectedCurrency,
        setSelectedCurrency,
        isAddingCurrency,
        setIsAddingCurrency,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrencyContext() {
  const { t } = useAppTranslation("settings_currency");

  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error(t("context_waraning"));
  }
  return context;
}
