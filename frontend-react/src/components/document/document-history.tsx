"use client"

import { useDocumentHistory } from "@/hooks/document/use-document-history"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Clock, User, FileText, AlertCircle } from "lucide-react"
import type { HistoryActionType } from "@/types/document/document-history"

/**
 * Props for the DocumentHistory component
 */
interface DocumentHistoryProps {
  documentId: string
}

/**
 * DocumentHistory component that displays the history of a document
 */
export function DocumentHistory({ documentId }: DocumentHistoryProps) {
  // Fetch document history using TanStack Query
  const { data: historyEntries, isLoading, isError } = useDocumentHistory(documentId)

  // Get badge color based on action type
  const getActionColor = (actionType: HistoryActionType) => {
    switch (actionType) {
      case "CREATE":
        return "bg-green-100 text-green-800 border-green-200"
      case "UPDATE":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "STATUS_CHANGE":
        return "bg-purple-100 text-purple-800 border-purple-200"
      case "CANCEL":
        return "bg-red-100 text-red-800 border-red-200"
      case "ITEM_ADD":
        return "bg-emerald-100 text-emerald-800 border-emerald-200"
      case "ITEM_REMOVE":
        return "bg-amber-100 text-amber-800 border-amber-200"
      case "ITEM_UPDATE":
        return "bg-cyan-100 text-cyan-800 border-cyan-200"
      case "RELATION_ADD":
        return "bg-indigo-100 text-indigo-800 border-indigo-200"
      case "RELATION_REMOVE":
        return "bg-rose-100 text-rose-800 border-rose-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  // Get action type label
  const getActionLabel = (actionType: HistoryActionType) => {
    switch (actionType) {
      case "CREATE":
        return "Erstellt"
      case "UPDATE":
        return "Aktualisiert"
      case "STATUS_CHANGE":
        return "Status geändert"
      case "CANCEL":
        return "Storniert"
      case "ITEM_ADD":
        return "Position hinzugefügt"
      case "ITEM_REMOVE":
        return "Position entfernt"
      case "ITEM_UPDATE":
        return "Position aktualisiert"
      case "RELATION_ADD":
        return "Beziehung hinzugefügt"
      case "RELATION_REMOVE":
        return "Beziehung entfernt"
      default:
        return actionType
    }
  }

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  // Loading state
  if (isLoading) {
    return <div className="flex justify-center p-4">Lade Dokumentenhistorie...</div>
  }

  // Error state
  if (isError) {
    return (
      <div className="flex items-center justify-center p-4 text-red-500">
        <AlertCircle className="h-5 w-5 mr-2" />
        Fehler beim Laden der Dokumentenhistorie
      </div>
    )
  }

  // Empty state
  if (!historyEntries || historyEntries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-muted-foreground">
        <FileText className="h-12 w-12 mb-2 opacity-20" />
        <p>Keine Historieneinträge für dieses Dokument gefunden.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 py-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-medium">Dokumentenhistorie</h3>
        <Badge variant="outline">{historyEntries.length} Einträge</Badge>
      </div>

      <div className="space-y-4">
        {historyEntries.map((entry) => (
          <Card key={entry.id} className="overflow-hidden">
            <CardContent className="p-0">
              <div className="flex items-center p-4 bg-muted/30">
                <Badge className={`mr-3 ${getActionColor(entry.actionType)}`}>{getActionLabel(entry.actionType)}</Badge>
                <div className="flex-1 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1">
                  <div className="flex items-center text-sm">
                    <User className="h-3.5 w-3.5 mr-1 text-muted-foreground" />
                    <span>{entry.userName}</span>
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="h-3.5 w-3.5 mr-1" />
                    <span>{formatTimestamp(entry.timestamp)}</span>
                  </div>
                </div>
              </div>

              <div className="p-4">
                <p className="font-medium mb-2">{entry.description}</p>

                {(entry.oldValue || entry.newValue) && (
                  <div className="mt-2 text-sm">
                    {entry.oldValue && (
                      <div className="flex items-start mb-1">
                        <span className="font-medium w-24 shrink-0">Alter Wert:</span>
                        <span className="text-muted-foreground">{entry.oldValue}</span>
                      </div>
                    )}
                    {entry.oldValue && entry.newValue && <Separator className="my-1" />}
                    {entry.newValue && (
                      <div className="flex items-start">
                        <span className="font-medium w-24 shrink-0">Neuer Wert:</span>
                        <span>{entry.newValue}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
