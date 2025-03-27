"use client"

import { useState, useEffect, useRef } from "react"
import { User, Pause, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface TimerHeaderProps {
  userName?: string
  onPause?: () => void
  onResume?: () => void
  className?: string
}

export function TimerHeader({ userName = "Mitarbeiter", onPause, onResume, className }: TimerHeaderProps) {
  const [elapsedTime, setElapsedTime] = useState(0) // Zeit in Sekunden
  const [isPaused, setIsPaused] = useState(false)
  const [pausesUsed, setPausesUsed] = useState(0)
  const [showPauseScreen, setShowPauseScreen] = useState(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  const MAX_PAUSES = 3
  const pausesRemaining = MAX_PAUSES - pausesUsed

  // Timer starten/stoppen
  useEffect(() => {
    if (!isPaused) {
      timerRef.current = setInterval(() => {
        setElapsedTime((prevTime) => prevTime + 1)
      }, 1000)
    } else if (timerRef.current) {
      clearInterval(timerRef.current)
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [isPaused])

  // Formatiere die Zeit im Format hh:mm:ss
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    return [
      hours.toString().padStart(2, "0"),
      minutes.toString().padStart(2, "0"),
      secs.toString().padStart(2, "0"),
    ].join(":")
  }

  const handlePauseResume = () => {
    if (!isPaused && pausesUsed < MAX_PAUSES) {
      // Pause starten
      setIsPaused(true)
      setShowPauseScreen(true)
      setPausesUsed((prev) => prev + 1)
      if (onPause) onPause()
    } else if (isPaused) {
      // Pause beenden
      setIsPaused(false)
      setShowPauseScreen(false)
      if (onResume) onResume()
    }
  }

  return (
    <>
      <div className={cn("w-full bg-red-600 text-white p-3 flex items-center justify-between", className)}>
        <div className="flex items-center gap-2">
          <User className="h-5 w-5" />
          <span className="font-medium">{userName}</span>
        </div>

        <div className="text-3xl font-bold tracking-wider">{formatTime(elapsedTime)}</div>

        <div className="flex items-center gap-4">
          <span>
            Pausen: {pausesUsed}/{MAX_PAUSES}
          </span>
          <Button
            variant="ghost"
            size="icon"
            onClick={handlePauseResume}
            disabled={!isPaused && pausesUsed >= MAX_PAUSES}
            className="h-8 w-8 text-white hover:bg-red-700 disabled:opacity-50"
          >
            {isPaused ? <Play className="h-5 w-5" /> : <Pause className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Pause-Vollbildschirm */}
      {showPauseScreen && (
        <div className="fixed inset-0 z-[100] bg-red-600 text-white flex flex-col items-center justify-center">
          <h1 className="text-7xl font-bold mb-8">PAUSE</h1>
          <p className="text-xl mb-12">Noch {pausesRemaining} Pausen verfügbar</p>
          <Button
            variant="outline"
            onClick={handlePauseResume}
            className="bg-white text-red-600 hover:bg-gray-100 hover:text-red-700 px-8 py-6 text-lg"
          >
            <Play className="h-5 w-5 mr-2" /> Timer fortsetzen
          </Button>
        </div>
      )}
    </>
  )
}

