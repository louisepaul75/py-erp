"use client"

import { useTimer } from "./timer-context"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"

export function PauseOverlay() {
  const { isRunning, toggleTimer, remainingPauses } = useTimer()

  // Wenn der Timer läuft, zeige nichts an
  if (isRunning) return null

  return (
    <div className="fixed inset-0 bg-red-600 z-[9999] flex flex-col items-center justify-center">
      <div className="text-center text-white w-full max-w-md mx-auto px-4">
        <h1 className="text-6xl font-bold mb-16">PAUSE</h1>

        <div className="mb-12 text-xl">
          {remainingPauses === 0
            ? "Keine Pausen mehr verfügbar!"
            : `Noch ${remainingPauses} ${remainingPauses === 1 ? "Pause" : "Pausen"} verfügbar`}
        </div>

        <Button onClick={toggleTimer} size="lg" className="w-full bg-white text-red-600 hover:bg-gray-100 text-xl py-8">
          <Play className="mr-2 h-6 w-6" />
          Timer fortsetzen
        </Button>
      </div>
    </div>
  )
}

