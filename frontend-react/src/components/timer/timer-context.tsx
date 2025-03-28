"use client"

import { createContext, useContext, useState, useEffect, type ReactNode, useRef } from "react"
import type { BookingItem } from "@/lib/types"

interface TimerContextType {
  isRunning: boolean
  seconds: number
  toggleTimer: () => void
  userName: string
  setUserName: (name: string) => void
  addBookedItems: (items: BookingItem[]) => void
  remainingPauses: number
}

const TimerContext = createContext<TimerContextType | undefined>(undefined)

const MAX_PAUSES = 3

export function TimerProvider({ children }: { children: ReactNode }) {
  const [isRunning, setIsRunning] = useState(true) // Automatisch starten
  const [seconds, setSeconds] = useState(0)
  const [userName, setUserName] = useState("Mitarbeiter")
  const [bookedItems, setBookedItems] = useState<BookingItem[]>([])
  const [remainingPauses, setRemainingPauses] = useState(MAX_PAUSES)

  // Referenz für den Interval
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Timer-Logik
  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setSeconds((prevSeconds) => prevSeconds + 1)
      }, 1000)
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isRunning])

  // Cleanup beim Beenden
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Simuliere Backend-Speicherung
      const sessionData = {
        mitarbeiter: userName,
        startzeit: new Date(Date.now() - seconds * 1000).toLocaleString(),
        endzeit: new Date().toLocaleString(),
        dauer: formatTime(seconds),
        artikel: bookedItems.map((item) => ({
          artikelnummer: item.articleNew,
          menge: item.quantity,
          ziel: item.targetSlot,
        })),
      }

      console.log("Arbeitssitzung beendet:", sessionData)
    }

    window.addEventListener("beforeunload", handleBeforeUnload)

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload)
    }
  }, [seconds, userName, bookedItems])

  // Formatiere die Sekunden in hh:mm:ss
  const formatTime = (totalSeconds: number) => {
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    return [
      hours.toString().padStart(2, "0"),
      minutes.toString().padStart(2, "0"),
      seconds.toString().padStart(2, "0"),
    ].join(":")
  }

  // Toggle Timer (nur Pause/Fortsetzen)
  const toggleTimer = () => {
    if (isRunning) {
      // Nur pausieren, wenn noch Pausen übrig sind
      if (remainingPauses > 0) {
        setIsRunning(false)
        setRemainingPauses((prev) => prev - 1)
      }
    } else {
      // Timer immer fortsetzen können
      setIsRunning(true)
    }
  }

  // Füge gebuchte Artikel zur aktuellen Sitzung hinzu
  const addBookedItems = (items: BookingItem[]) => {
    if (isRunning) {
      // Nur hinzufügen, wenn der Timer läuft
      setBookedItems((prev) => [...prev, ...items])
      console.log(`${items.length} Artikel zur aktuellen Sitzung hinzugefügt`)
    } else {
      console.warn("Artikel können nicht hinzugefügt werden, wenn der Timer pausiert ist")
    }
  }

  return (
    <TimerContext.Provider
      value={{
        isRunning,
        seconds,
        toggleTimer,
        userName,
        setUserName,
        addBookedItems,
        remainingPauses,
      }}
    >
      {children}
    </TimerContext.Provider>
  )
}

export function useTimer() {
  const context = useContext(TimerContext)
  if (context === undefined) {
    throw new Error("useTimer must be used within a TimerProvider")
  }
  return context
}

