"use client"

import { useState, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import WorkplaceSelector from "./workplace-selector"
import MoldManager from "./mold-manager"
import CastingProcess from "./casting-process"
import SessionSelector from "./session-selector"
import CentrifugeSelector from "./centrifuge-selector"
import { Button } from "@/components/ui/button"
import type { Mold, Session, User } from "@/types/casting/mold"
import { useToast } from "@/components/ui/use-toast"
import { createSession, initSessionStore } from "@/lib/casting/session-store"
import { useAuthContext } from "@/context/AuthContext"

type SetupStep = "session" | "workplace" | "centrifuge" | "molds" | "process"

export default function CastingManager() {
  const [currentStep, setCurrentStep] = useState<SetupStep>("session")
  const [selectedWorkplace, setSelectedWorkplace] = useState<string>("")
  const [molds, setMolds] = useState<Mold[]>([])
  const [centrifugeMachines, setCentrifugeMachines] = useState(1)
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const { toast } = useToast()
  const { user } = useAuthContext()

  // Get current user from authentication context
  const currentUser: User = {
    id: user?.id?.toString() || "guest",
    name: user?.username || "Gast",
  }

  // Initialize session store
  useEffect(() => {
    initSessionStore()
  }, [])

  const handleAddMold = (mold: Mold) => {
    if (molds.length >= 6) {
      toast({
        title: "Maximale Anzahl erreicht",
        description: "Es können maximal 6 Formen gleichzeitig verwaltet werden.",
        variant: "destructive",
      })
      return
    }

    setMolds((prev) => [...prev, mold])
  }

  const handleRemoveMold = (moldId: string) => {
    setMolds((prev) => prev.filter((mold) => mold.id !== moldId))
  }

  const handleStartProcess = () => {
    if (molds.length === 0) {
      toast({
        title: "Keine Formen ausgewählt",
        description: "Bitte fügen Sie mindestens eine Form hinzu, um den Prozess zu starten.",
        variant: "destructive",
      })
      return
    }

    // Create a new session
    const newSession: Session = {
      id: uuidv4(),
      userId: currentUser.id,
      userName: currentUser.name,
      workplace: selectedWorkplace,
      molds: molds,
      startTime: Date.now(),
      pauseCount: 0,
      maxPauses: 3,
      isPaused: false,
      elapsedTime: 0,
      centrifugeMachines: centrifugeMachines,
      lastActive: Date.now(),
    }

    const createdSession = createSession(newSession)
    setCurrentSession(createdSession)
    setCurrentStep("process")
  }

  const handleSelectSession = (session: Session) => {
    setCurrentSession(session)
    setCurrentStep("process")
  }

  const handleCreateNewSession = () => {
    setCurrentStep("workplace")
  }

  // Use useCallback to prevent recreation of this function on each render
  const handleUpdateSession = useCallback((session: Session) => {
    setCurrentSession(session)
  }, [])

  const handleResetProcess = () => {
    setCurrentSession(null)
    setMolds([])
    setSelectedWorkplace("")
    setCentrifugeMachines(1)
    setCurrentStep("session")
  }

  const handleSelectCentrifuge = (count: number) => {
    setCentrifugeMachines(count)
    setCurrentStep("molds")
  }

  return (
    <div className="max-w-5xl mx-auto pt-6 pb-16">
      <h1 className="text-2xl md:text-3xl font-bold mb-6 text-center">Casting Manager</h1>

      {currentStep === "session" && (
        <SessionSelector
          userId={currentUser.id}
          onSelectSession={handleSelectSession}
          onCreateNewSession={handleCreateNewSession}
        />
      )}

      {currentStep === "workplace" && (
        <WorkplaceSelector
          selectedWorkplace={selectedWorkplace}
          onSelectWorkplace={(workplace) => {
            setSelectedWorkplace(workplace)
            setCurrentStep("centrifuge")
          }}
        />
      )}

      {currentStep === "centrifuge" && (
        <CentrifugeSelector onSelect={handleSelectCentrifuge} defaultValue={centrifugeMachines} />
      )}

      {currentStep === "molds" && (
        <div className="mt-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border mb-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Arbeitsplatz: {selectedWorkplace}</h2>
              <div className="text-sm">Schleudermaschinen: {centrifugeMachines}</div>
            </div>
          </div>

          <MoldManager onAddMold={handleAddMold} molds={molds} onRemoveMold={handleRemoveMold} />

          {molds.length > 0 && (
            <div className="mt-8 flex justify-center">
              <Button size="lg" onClick={handleStartProcess} className="px-8 py-6 text-lg">
                Gießprozess starten
              </Button>
            </div>
          )}
        </div>
      )}

      {currentStep === "process" && currentSession && (
        <CastingProcess session={currentSession} onUpdateSession={handleUpdateSession} onExit={handleResetProcess} />
      )}
    </div>
  )
} 