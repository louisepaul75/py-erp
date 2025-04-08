"use client"

import { useState, useEffect, useRef } from "react"
import type { Mold, Session } from "@/types/casting/mold"
import CastingCard from "./casting-card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import TimerDisplay from "./timer-display"
import PauseScreen from "./pause-screen"
import { useTimer } from "@/hooks/casting/use-timer"
import { updateSession } from "@/lib/casting/session-store"
import { Button } from "@/components/ui/button"
import { Plus, X } from "lucide-react"
import AddMoldModal from "./add-mold-modal"
import Image from "next/image"

interface CastingProcessProps {
  session: Session
  onUpdateSession: (session: Session) => void
  onExit: () => void
}

export default function CastingProcess({ session, onUpdateSession, onExit }: CastingProcessProps) {
  const [castCounts, setCastCounts] = useState<Record<string, number>>(
    session.molds.reduce((acc, mold) => ({ ...acc, [mold.id]: mold.castCount || 0 }), {}),
  )

  const [selectedArticles, setSelectedArticles] = useState<Record<string, string>>(
    session.molds.reduce(
      (acc, mold) => ({
        ...acc,
        [mold.id]: mold.selectedArticleId || mold.articles[0].id,
      }),
      {},
    ),
  )

  const [molds, setMolds] = useState<Mold[]>(session.molds)
  const [showAddMoldModal, setShowAddMoldModal] = useState(false)

  // Use refs to avoid state updates during render
  const sessionRef = useRef(session)
  const updatePending = useRef(false)

  // Update the ref when the session prop changes
  useEffect(() => {
    sessionRef.current = session
  }, [session])

  // Initialize timer with session data
  const timer = useTimer({
    maxPauses: session.maxPauses,
    initialTime: session.elapsedTime || 0,
    initialPauses: session.pauseCount || 0,
    onPauseExhausted: () => {
      // Optional: Handle when all pauses are used
    },
  })

  // Start or pause timer based on session state
  useEffect(() => {
    if (!session.isPaused) {
      timer.start()
    }
  }, [])

  // Function to safely update session
  const safeUpdateSession = (updates: Partial<Session>) => {
    if (updatePending.current) return null

    updatePending.current = true

    // Use setTimeout to move the update out of the render phase
    setTimeout(() => {
      const updatedSession = updateSession(sessionRef.current.id, {
        ...updates,
        lastActive: Date.now(),
      })

      if (updatedSession) {
        onUpdateSession(updatedSession)
      }

      updatePending.current = false
    }, 0)
  }

  // Save session data periodically
  useEffect(() => {
    const saveInterval = setInterval(() => {
      if (!updatePending.current) {
        safeUpdateSession({
          elapsedTime: timer.elapsedTime,
          pauseCount: timer.pausesUsed,
          isPaused: timer.isPaused,
          molds: molds.map((mold) => ({
            ...mold,
            castCount: castCounts[mold.id] || 0,
            selectedArticleId: selectedArticles[mold.id],
          })),
        })
      }
    }, 5000) // Save every 5 seconds

    return () => clearInterval(saveInterval)
  }, [timer, castCounts, selectedArticles, molds])

  const handleIncrementCast = (moldId: string) => {
    if (timer.isPaused) return

    setCastCounts((prev) => {
      const newCounts = {
        ...prev,
        [moldId]: (prev[moldId] || 0) + 1,
      }

      // Update session after state update
      setTimeout(() => {
        safeUpdateSession({
          molds: molds.map((mold) => ({
            ...mold,
            castCount: mold.id === moldId ? newCounts[moldId] : newCounts[mold.id] || 0,
            selectedArticleId: selectedArticles[mold.id],
          })),
          elapsedTime: timer.elapsedTime,
        })
      }, 0)

      return newCounts
    })
  }

  const handleSelectArticle = (moldId: string, articleId: string) => {
    setSelectedArticles((prev) => {
      const newSelections = {
        ...prev,
        [moldId]: articleId,
      }

      // Update session after state update
      setTimeout(() => {
        safeUpdateSession({
          molds: molds.map((mold) => ({
            ...mold,
            castCount: castCounts[mold.id] || 0,
            selectedArticleId: mold.id === moldId ? articleId : newSelections[mold.id],
          })),
          elapsedTime: timer.elapsedTime,
        })
      }, 0)

      return newSelections
    })
  }

  const handlePause = () => {
    if (timer.pause()) {
      safeUpdateSession({
        isPaused: true,
        pauseCount: timer.pausesUsed,
        elapsedTime: timer.elapsedTime,
      })
    }
  }

  const handleResume = () => {
    timer.resume()
    safeUpdateSession({
      isPaused: false,
      elapsedTime: timer.elapsedTime,
    })
  }

  // Add a new mold during the process
  const handleAddMold = (mold: Mold) => {
    if (molds.length >= 6) {
      return
    }

    setMolds((prev) => [...prev, mold])
    setSelectedArticles((prev) => ({
      ...prev,
      [mold.id]: mold.articles[0].id,
    }))
    setCastCounts((prev) => ({
      ...prev,
      [mold.id]: 0,
    }))

    // Update session with new mold
    setTimeout(() => {
      safeUpdateSession({
        molds: [...molds, mold],
      })
    }, 0)
  }

  // Remove a mold during the process
  const handleRemoveMold = (moldId: string) => {
    setMolds((prev) => prev.filter((mold) => mold.id !== moldId))

    // Update session after removing mold
    setTimeout(() => {
      safeUpdateSession({
        molds: molds.filter((mold) => mold.id !== moldId),
      })
    }, 0)
  }

  // Save session data when exiting
  const handleExit = () => {
    // Update session before exiting
    const updatedSession = updateSession(session.id, {
      elapsedTime: timer.elapsedTime,
      pauseCount: timer.pausesUsed,
      isPaused: timer.isPaused,
      molds: molds.map((mold) => ({
        ...mold,
        castCount: castCounts[mold.id] || 0,
        selectedArticleId: selectedArticles[mold.id],
      })),
      lastActive: Date.now(),
    })

    if (updatedSession) {
      // We don't need to call onUpdateSession here since we're exiting
    }

    onExit()
  }

  return (
    <div className="min-h-screen flex flex-col">
      <TimerDisplay
        time={timer.formatTime().formatted}
        userName={session.userName}
        pausesUsed={timer.pausesUsed}
        maxPauses={session.maxPauses}
        onPause={handlePause}
        disabled={timer.isPaused}
      />

      {timer.isPaused && <PauseScreen remainingPauses={timer.remainingPauses} onResume={handleResume} />}

      <div className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Arbeitsplatz: {session.workplace}</h2>
          <div className="flex items-center gap-2">
            <span className="text-sm">Schleudermaschinen: {session.centrifugeMachines}</span>
            <Button
              variant="outline"
              size="sm"
              className="mr-2"
              onClick={() => setShowAddMoldModal(true)}
              disabled={molds.length >= 6 || timer.isPaused}
            >
              <Plus className="h-4 w-4 mr-1" /> Form hinzufügen
            </Button>
            <button onClick={handleExit} className="px-3 py-1 text-sm bg-gray-100 rounded-md hover:bg-gray-200">
              Zurück zur Auswahl
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {molds.map((mold) => (
            <div key={mold.id} className="flex flex-col h-full relative">
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-0 right-0 z-10 text-red-500 hover:text-red-700 hover:bg-red-50"
                onClick={() => handleRemoveMold(mold.id)}
                disabled={timer.isPaused}
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Form entfernen</span>
              </Button>

              {mold.articles.length > 1 && (
                <div className="flex items-center gap-2 mb-2">
                  <Label htmlFor={`article-select-${mold.id}`} className="text-sm whitespace-nowrap">
                    Artikel:
                  </Label>
                  <Select
                    value={selectedArticles[mold.id]}
                    onValueChange={(value) => handleSelectArticle(mold.id, value)}
                    disabled={timer.isPaused}
                  >
                    <SelectTrigger id={`article-select-${mold.id}`} className="h-8 text-sm">
                      <SelectValue placeholder="Artikel wählen" />
                    </SelectTrigger>
                    <SelectContent>
                      {mold.articles.map((article) => (
                        <SelectItem key={article.id} value={article.id} className="text-sm">
                          <div className="flex items-center gap-2">
                            <div className="relative w-6 h-6 rounded overflow-hidden">
                              <Image
                                src={article.imageUrl || "/placeholder.svg"}
                                alt={article.name}
                                fill
                                className="object-contain"
                              />
                            </div>
                            <span>
                              {article.number} - {article.name}
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              <CastingCard
                mold={{
                  ...mold,
                  selectedArticleId: selectedArticles[mold.id],
                }}
                castCount={castCounts[mold.id] || 0}
                onIncrementCast={() => handleIncrementCast(mold.id)}
                disabled={timer.isPaused}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Add Mold Modal */}
      <AddMoldModal isOpen={showAddMoldModal} onClose={() => setShowAddMoldModal(false)} onAddMold={handleAddMold} />
    </div>
  )
} 