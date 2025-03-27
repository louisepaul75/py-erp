"use client"

import { useState } from "react"
import { useTimer } from "./timer-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Pause, Play, User } from "lucide-react"

export function GlobalTimer() {
  const { isRunning, seconds, toggleTimer, userName, setUserName, remainingPauses } = useTimer()
  const [isEditingName, setIsEditingName] = useState(false)
  const [nameInput, setNameInput] = useState(userName)

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

  const handleNameSubmit = () => {
    if (nameInput.trim()) {
      setUserName(nameInput)
    }
    setIsEditingName(false)
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-red-600 text-white p-2 shadow-lg z-50">
      <div className="container mx-auto max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {isEditingName ? (
              <div className="flex items-center">
                <Input
                  value={nameInput}
                  onChange={(e) => setNameInput(e.target.value)}
                  className="h-8 w-40 bg-red-700 border-red-400 text-white placeholder:text-red-300"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleNameSubmit()
                  }}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNameSubmit}
                  className="h-8 text-white hover:bg-red-700"
                >
                  <User className="h-4 w-4 mr-1" />
                  OK
                </Button>
              </div>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditingName(true)}
                className="text-white hover:bg-red-700"
              >
                <User className="h-4 w-4 mr-1" />
                {userName}
              </Button>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <div className="text-2xl font-mono font-bold tabular-nums">{formatTime(seconds)}</div>

            {isRunning && (
              <div className="flex items-center ml-4 text-sm bg-red-700 px-2 py-1 rounded">
                <span className="mr-1">Pausen:</span>
                <span className={remainingPauses === 0 ? "text-yellow-300 font-bold" : "font-bold"}>
                  {remainingPauses}/3
                </span>
              </div>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTimer}
              disabled={isRunning && remainingPauses === 0}
              className="text-white hover:bg-red-700 disabled:opacity-50 ml-2"
              title={isRunning && remainingPauses === 0 ? "Keine Pausen mehr verfügbar" : ""}
            >
              {isRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

