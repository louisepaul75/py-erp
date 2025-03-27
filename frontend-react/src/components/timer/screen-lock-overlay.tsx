"use client"

import { useTimer } from "./timer-context"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"

export function ScreenLockOverlay() {
  const { isScreenLocked, toggleTimer, remainingPauses } = useTimer()

  if (!isScreenLocked) return null

  return (
    <div className="fixed inset-0 bg-red-600 z-[100] flex flex-col items-center justify-center">
      <div className="text-center text-white w-full max-w-md mx-auto px-4">
        <h1 className="text-5xl font-bold mb-12">PAUSE</h1>

        <div className="mb-8 text-xl">
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

