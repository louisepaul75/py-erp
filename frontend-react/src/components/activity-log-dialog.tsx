"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { generateMockActivityLogs } from "@/lib/warehouse-service"

interface ActivityLogEntry {
  id: string
  timestamp: Date
  user: string
  action: string
  entityId: string
  entityType: string
  beforeState: string
  afterState: string
}

interface ActivityLogDialogProps {
  isOpen: boolean
  onClose: () => void
  locationId?: string
  locationType: "location" | "container"
}

export default function ActivityLogDialog({ isOpen, onClose, locationId, locationType }: ActivityLogDialogProps) {
  const [logs, setLogs] = useState<ActivityLogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<ActivityLogEntry[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [userFilter, setUserFilter] = useState("all")
  const [actionFilter, setActionFilter] = useState("all")
  const [dateFilter, setDateFilter] = useState("all")

  useEffect(() => {
    // In einer echten Anwendung würden hier die Logs vom Server geladen
    setLogs(generateMockActivityLogs(locationId, locationType, 20))
  }, [locationId, locationType])

  useEffect(() => {
    let filtered = [...logs]

    // Suche
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(
        (log) =>
          log.user.toLowerCase().includes(term) ||
          log.action.toLowerCase().includes(term) ||
          log.beforeState.toLowerCase().includes(term) ||
          log.afterState.toLowerCase().includes(term),
      )
    }

    // Benutzerfilter
    if (userFilter !== "all") {
      filtered = filtered.filter((log) => log.user === userFilter)
    }

    // Aktionsfilter
    if (actionFilter !== "all") {
      filtered = filtered.filter((log) => log.action === actionFilter)
    }

    // Datumsfilter
    if (dateFilter !== "all") {
      const now = new Date()
      const cutoffDate = new Date()

      switch (dateFilter) {
        case "today":
          cutoffDate.setHours(0, 0, 0, 0)
          break
        case "yesterday":
          cutoffDate.setDate(now.getDate() - 1)
          cutoffDate.setHours(0, 0, 0, 0)
          break
        case "week":
          cutoffDate.setDate(now.getDate() - 7)
          break
        case "month":
          cutoffDate.setMonth(now.getMonth() - 1)
          break
      }

      filtered = filtered.filter((log) => log.timestamp >= cutoffDate)
    }

    setFilteredLogs(filtered)
  }, [logs, searchTerm, userFilter, actionFilter, dateFilter])

  // Extrahiere eindeutige Benutzer und Aktionen für Filter
  const users = Array.from(new Set(logs.map((log) => log.user)))
  const actions = Array.from(new Set(logs.map((log) => log.action)))

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-4xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">
              Aktivitätslog {locationType === "location" ? "Lagerort" : "Schütten/Artikel"}
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-4 space-y-4">
            {/* Filter-Bereich */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Suche..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div>
                <Select
                  value={userFilter}
                  onValueChange={setUserFilter}
                  placeholder="Benutzer"
                  options={[
                    { value: "all", label: "Alle Benutzer" },
                    ...users.map((user) => ({ value: user, label: user })),
                  ]}
                />
              </div>

              <div>
                <Select
                  value={actionFilter}
                  onValueChange={setActionFilter}
                  placeholder="Aktion"
                  options={[
                    { value: "all", label: "Alle Aktionen" },
                    ...actions.map((action) => ({ value: action, label: action })),
                  ]}
                />
              </div>

              <div>
                <Select
                  value={dateFilter}
                  onValueChange={setDateFilter}
                  placeholder="Zeitraum"
                  options={[
                    { value: "all", label: "Alle Zeiträume" },
                    { value: "today", label: "Heute" },
                    { value: "yesterday", label: "Gestern" },
                    { value: "week", label: "Letzte Woche" },
                    { value: "month", label: "Letzter Monat" },
                  ]}
                />
              </div>
            </div>

            {/* Tabelle */}
            <div className="border rounded-md overflow-hidden max-h-[500px] overflow-y-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100 sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Zeitpunkt</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Benutzer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Aktion</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Vorher</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Nachher</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {filteredLogs.length > 0 ? (
                    filteredLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">
                          {log.timestamp.toLocaleString("de-DE", {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </td>
                        <td className="px-4 py-3 text-sm">{log.user}</td>
                        <td className="px-4 py-3 text-sm">{log.action}</td>
                        <td className="px-4 py-3 text-sm">
                          <div className="max-w-xs truncate">{log.beforeState}</div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="max-w-xs truncate">{log.afterState}</div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="px-4 py-6 text-center text-gray-500">
                        Keine Aktivitäten gefunden
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="p-4 border-t flex justify-end">
            <Button onClick={onClose}>Schließen</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

