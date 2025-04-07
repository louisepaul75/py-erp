"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { getUserSessions, deleteSession } from "@/lib/casting/session-store"
import type { Session } from "@/types/casting/mold"
import { Clock, Plus, Trash2 } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface SessionSelectorProps {
  userId: string
  onSelectSession: (session: Session) => void
  onCreateNewSession: () => void
}

export default function SessionSelector({
  userId,
  onSelectSession,
  onCreateNewSession,
}: SessionSelectorProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null)

  useEffect(() => {
    // Get user sessions on component mount
    setSessions(getUserSessions(userId))
  }, [userId])

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  const formatElapsedTime = (ms: number) => {
    const hours = Math.floor(ms / 3600000)
    const minutes = Math.floor((ms % 3600000) / 60000)
    const seconds = Math.floor((ms % 60000) / 1000)
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
  }

  const handleSelectSession = () => {
    if (selectedSessionId) {
      const session = sessions.find((s) => s.id === selectedSessionId)
      if (session) {
        onSelectSession(session)
      }
    }
  }

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setSessionToDelete(sessionId)
    setDeleteConfirmOpen(true)
  }

  const confirmDelete = () => {
    if (sessionToDelete) {
      deleteSession(sessionToDelete)
      setSessions(getUserSessions(userId))
      if (selectedSessionId === sessionToDelete) {
        setSelectedSessionId(null)
      }
    }
    setDeleteConfirmOpen(false)
    setSessionToDelete(null)
  }

  return (
    <div className="max-w-3xl mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Gießsitzungen</h2>

      {sessions.length > 0 ? (
        <div className="space-y-4">
          <div className="bg-white rounded-lg border shadow-sm">
            <div className="p-4 border-b bg-muted/20">
              <h3 className="font-medium">Vorhandene Sitzungen fortsetzen</h3>
            </div>
            <div className="divide-y">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`p-4 cursor-pointer hover:bg-muted/10 transition-colors ${
                    selectedSessionId === session.id ? "bg-primary/5 border-l-4 border-primary" : ""
                  }`}
                  onClick={() => setSelectedSessionId(session.id)}
                >
                  <div className="flex justify-between">
                    <div>
                      <div className="font-medium">Arbeitsplatz: {session.workplace}</div>
                      <div className="text-sm text-muted-foreground">
                        Erstellt: {formatTime(session.startTime)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center text-sm font-medium">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatElapsedTime(session.elapsedTime)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {session.molds.length} Formen, {session.centrifugeMachines} Maschinen
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive hover:text-destructive/90 hover:bg-destructive/10"
                      onClick={(e) => handleDeleteSession(session.id, e)}
                    >
                      <Trash2 className="h-4 w-4" />
                      <span className="sr-only">Löschen</span>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <Button variant="outline" onClick={onCreateNewSession}>
              <Plus className="h-4 w-4 mr-2" />
              Neue Sitzung erstellen
            </Button>
            <Button onClick={handleSelectSession} disabled={!selectedSessionId}>
              Ausgewählte Sitzung fortsetzen
            </Button>
          </div>
        </div>
      ) : (
        <div className="text-center py-10 bg-muted/20 rounded-lg border border-dashed mb-6">
          <div className="text-muted-foreground">Keine aktiven Gießsitzungen gefunden</div>
          <div className="mt-6">
            <Button onClick={onCreateNewSession}>
              <Plus className="h-4 w-4 mr-2" />
              Neue Sitzung erstellen
            </Button>
          </div>
        </div>
      )}

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Sitzung löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie diese Gießsitzung wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
} 