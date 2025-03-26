"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { usePrinterStore } from "@/lib/stores/printer-store"

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
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Drucker Name / Ort</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">IP-Adresse</th>
            </tr>
          </thead>
          <tbody className="divide-y  ">
            {printers.length > 0 ? (
              printers.map((printer) => (
                <tr
                  key={printer.id}
                  className={`hover:bg-gray-50 cursor-pointer ${selectedPrinterId === printer.id ? "bg-blue-50" : ""}`}
                  onClick={() => handleSelectPrinter(printer)}
                >
                  <td className="px-4 py-3 text-sm text-black">{printer.name}</td>
                  <td className="px-4 py-3 text-sm text-black">{printer.ipAddress}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-gray-500">
                  Keine Drucker konfiguriert
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {(isAddingNew || selectedPrinterId) && (
        <div className="border rounded-md p-4 space-y-4">
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

