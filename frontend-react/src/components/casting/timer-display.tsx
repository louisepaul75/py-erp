"use client"

import { Clock, PauseCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

interface TimerDisplayProps {
  time: string
  userName: string
  pausesUsed: number
  maxPauses: number
  onPause: () => void
  disabled: boolean
}

export default function TimerDisplay({
  time,
  userName,
  pausesUsed,
  maxPauses,
  onPause,
  disabled,
}: TimerDisplayProps) {
  return (
    <div className="bg-slate-800 text-white p-4 sticky top-16 z-10">
      <div className="max-w-5xl mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <Clock className="h-5 w-5 mr-2" />
          <span className="text-xl font-mono">{time}</span>
        </div>

        <div className="text-center">
          <div className="text-sm opacity-80">Benutzername</div>
          <div className="font-medium">{userName}</div>
        </div>

        <div className="flex flex-col items-end">
          <Button
            variant="outline"
            size="sm"
            onClick={onPause}
            disabled={disabled || pausesUsed >= maxPauses}
            className="text-white border-white hover:bg-white/20 hover:text-white"
          >
            <PauseCircle className="h-4 w-4 mr-2" />
            Pause ({pausesUsed}/{maxPauses})
          </Button>
        </div>
      </div>
    </div>
  )
} 