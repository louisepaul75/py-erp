"use client"

import { createContext, useContext, useState, type ReactNode, useEffect } from "react"
import type { HistoryEntry } from "@/lib/types"
import { mockHistoryEntries } from "@/lib/api"

interface HistoryContextType {
  historyEntries: HistoryEntry[]
  addHistoryEntry: (entry: Omit<HistoryEntry, "id">) => void
}

const HistoryContext = createContext<HistoryContextType | undefined>(undefined)

export function HistoryProvider({ children }: { children: ReactNode }) {
  const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([])

  // Initialisiere die History-Einträge beim ersten Laden
  useEffect(() => {
    setHistoryEntries(mockHistoryEntries)
  }, [])

  const addHistoryEntry = (entry: Omit<HistoryEntry, "id">) => {
    const newEntry: HistoryEntry = {
      ...entry,
      id: `dynamic-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
    }

    setHistoryEntries((prev) => [newEntry, ...prev])
    console.log("Added history entry:", newEntry)
  }

  return <HistoryContext.Provider value={{ historyEntries, addHistoryEntry }}>{children}</HistoryContext.Provider>
}

export function useHistory() {
  const context = useContext(HistoryContext)
  if (context === undefined) {
    throw new Error("useHistory must be used within a HistoryProvider")
  }
  return context
}

