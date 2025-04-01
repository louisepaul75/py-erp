"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { usePrinterStore } from "@/lib/stores/printer-store"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"

interface Printer {
  id: string
  name: string
  ipAddress: string
}

export default function PrinterSettings() {
  const { printers, addPrinter, updatePrinter, deletePrinter } = usePrinterStore()
  const [selectedPrinterId, setSelectedPrinterId] = useState<string | null>(null)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [newPrinterName, setNewPrinterName] = useState("")
  const [newPrinterIp, setNewPrinterIp] = useState("")
  const [error, setError] = useState("")

  const handleAddNew = () => {
    setIsAddingNew(true)
    setSelectedPrinterId(null)
    setNewPrinterName("")
    setNewPrinterIp("")
    setError("")
  }

  const handleSave = () => {
    if (!newPrinterName.trim()) {
      setError("Bitte geben Sie einen Druckernamen ein")
      return
    }

    if (!newPrinterIp.trim()) {
      setError("Bitte geben Sie eine IP-Adresse ein")
      return
    }

    // Einfache IP-Validierung
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
    if (!ipRegex.test(newPrinterIp)) {
      setError("Bitte geben Sie eine gültige IP-Adresse ein")
      return
    }

    if (isAddingNew) {
      addPrinter({
        id: crypto.randomUUID(),
        name: newPrinterName,
        ipAddress: newPrinterIp,
      })
    } else if (selectedPrinterId) {
      updatePrinter(selectedPrinterId, {
        id: selectedPrinterId,
        name: newPrinterName,
        ipAddress: newPrinterIp,
      })
    }

    setIsAddingNew(false)
    setSelectedPrinterId(null)
    setNewPrinterName("")
    setNewPrinterIp("")
    setError("")
  }

  const handleDelete = () => {
    if (selectedPrinterId) {
      deletePrinter(selectedPrinterId)
      setSelectedPrinterId(null)
      setNewPrinterName("")
      setNewPrinterIp("")
    }
  }

  const handleSelectPrinter = (printer: Printer) => {
    setSelectedPrinterId(printer.id)
    setNewPrinterName(printer.name)
    setNewPrinterIp(printer.ipAddress)
    setIsAddingNew(false)
    setError("")
  }

  const handleCancel = () => {
    setIsAddingNew(false)
    setSelectedPrinterId(null)
    setNewPrinterName("")
    setNewPrinterIp("")
    setError("")
  }

  return (
    <div className="space-y-4">
      <div className="border rounded-md overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50">
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">Drucker Name / Ort</TableHead>
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">IP-Adresse</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {printers.length > 0 ? (
              printers.map((printer: Printer) => (
                <TableRow
                  key={printer.id}
                  data-state={selectedPrinterId === printer.id ? "selected" : undefined}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/70 cursor-pointer"
                  onClick={() => handleSelectPrinter(printer)}
                >
                  <TableCell className="text-sm">{printer.name}</TableCell>
                  <TableCell className="text-sm">{printer.ipAddress}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={2} className="h-24 text-center text-muted-foreground">
                  Keine Drucker konfiguriert
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {(isAddingNew || selectedPrinterId) && (
        <div className="border rounded-md p-4 space-y-4 bg-slate-50 dark:bg-slate-800/50">
          <h3 className="font-medium">{isAddingNew ? "Neuen Drucker hinzufügen" : "Drucker bearbeiten"}</h3>

          <div className="space-y-2">
            <Label htmlFor="printerName">Drucker Name / Ort</Label>
            <Input
              id="printerName"
              value={newPrinterName}
              onChange={(e) => setNewPrinterName(e.target.value)}
              placeholder="z.B. Lager01-Diessen"
              className={error && !newPrinterName ? "border-red-500" : ""}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="printerIp">IP-Adresse</Label>
            <Input
              id="printerIp"
              value={newPrinterIp}
              onChange={(e) => setNewPrinterIp(e.target.value)}
              placeholder="z.B. 192.168.1.100"
              className={error && !newPrinterIp ? "border-red-500" : ""}
            />
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleCancel}>
              Abbrechen
            </Button>
            <Button onClick={handleSave}>Speichern</Button>
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <Button variant="outline" onClick={handleAddNew}>
          Neuer
        </Button>
        <Button variant="outline" onClick={handleDelete} disabled={!selectedPrinterId}>
          Löschen
        </Button>
      </div>
    </div>
  )
}

