"use client"

import { Play } from "lucide-react"
import { Button } from "@/components/ui/button"

interface PauseScreenProps {
  remainingPauses: number
  onResume: () => void
}

export default function PauseScreen({ remainingPauses, onResume }: PauseScreenProps) {
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-white">
      <div className="bg-slate-800 p-8 rounded-lg max-w-md w-full text-center space-y-6">
        <h2 className="text-3xl font-bold">Pause</h2>
        
        <p className="text-lg">
          Drücken Sie auf Fortsetzen, um den Gießprozess fortzuführen.
        </p>
        
        <div className="text-amber-400 font-medium">
          {remainingPauses} Pausen verbleiben
        </div>
        
        <Button
          size="lg"
          onClick={onResume}
          className="w-full py-6 text-lg"
        >
          <Play className="mr-2 h-5 w-5" />
          Fortsetzen
        </Button>
      </div>
    </div>
  )
} 