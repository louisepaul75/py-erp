"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useScaleStore } from "@/lib/stores/scale-store"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"

interface Scale {
  id: string
  name: string
  ipAddress: string
  tolerance: number
}

export default function ScaleSettings() {
  const { scales, addScale, updateScale, deleteScale } = useScaleStore()
  const [selectedScaleId, setSelectedScaleId] = useState<string | null>(null)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [newScaleName, setNewScaleName] = useState("")
  const [newScaleIp, setNewScaleIp] = useState("")
  const [newScaleTolerance, setNewScaleTolerance] = useState("0")
  const [error, setError] = useState("")

  const handleAddNew = () => {
    setIsAddingNew(true)
    setSelectedScaleId(null)
    setNewScaleName("")
    setNewScaleIp("")
    setNewScaleTolerance("0")
    setError("")
  }

  const handleSave = () => {
    if (!newScaleName.trim()) {
      setError("Bitte geben Sie einen Namen für die Waage ein")
      return
    }

    if (!newScaleIp.trim()) {
      setError("Bitte geben Sie eine IP-Adresse ein")
      return
    }

    // Einfache IP-Validierung
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
    if (!ipRegex.test(newScaleIp)) {
      setError("Bitte geben Sie eine gültige IP-Adresse ein")
      return
    }

    // Toleranz-Validierung
    const tolerance = Number.parseFloat(newScaleTolerance)
    if (isNaN(tolerance) || tolerance < 0 || tolerance > 100) {
      setError("Bitte geben Sie eine gültige Toleranz zwischen 0 und 100 ein")
      return
    }

    if (isAddingNew) {
      addScale({
        id: crypto.randomUUID(),
        name: newScaleName,
        ipAddress: newScaleIp,
        tolerance: tolerance,
      })
    } else if (selectedScaleId) {
      updateScale(selectedScaleId, {
        id: selectedScaleId,
        name: newScaleName,
        ipAddress: newScaleIp,
        tolerance: tolerance,
      })
    }

    setIsAddingNew(false)
    setSelectedScaleId(null)
    setNewScaleName("")
    setNewScaleIp("")
    setNewScaleTolerance("0")
    setError("")
  }

  const handleDelete = () => {
    if (selectedScaleId) {
      deleteScale(selectedScaleId)
      setSelectedScaleId(null)
      setNewScaleName("")
      setNewScaleIp("")
      setNewScaleTolerance("0")
    }
  }

  const handleSelectScale = (scale: Scale) => {
    setSelectedScaleId(scale.id)
    setNewScaleName(scale.name)
    setNewScaleIp(scale.ipAddress)
    setNewScaleTolerance(scale.tolerance.toString())
    setIsAddingNew(false)
    setError("")
  }

  const handleCancel = () => {
    setIsAddingNew(false)
    setSelectedScaleId(null)
    setNewScaleName("")
    setNewScaleIp("")
    setNewScaleTolerance("0")
    setError("")
  }

  return (
    <div className="space-y-4">
      <div className="border rounded-md overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50 hover:bg-muted">
              <TableHead className="font-medium text-muted-foreground">Waage / Ort</TableHead>
              <TableHead className="font-medium text-muted-foreground">IP-Adresse</TableHead>
              <TableHead className="font-medium text-muted-foreground">Toleranz %</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scales.length > 0 ? (
              scales.map((scale: Scale) => (
                <TableRow
                  key={scale.id}
                  data-state={selectedScaleId === scale.id ? "selected" : undefined}
                  className="hover:bg-muted/50 cursor-pointer"
                  onClick={() => handleSelectScale(scale)}
                >
                  <TableCell className="text-sm">{scale.name}</TableCell>
                  <TableCell className="text-sm">{scale.ipAddress}</TableCell>
                  <TableCell className="text-sm">{scale.tolerance.toFixed(2)}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                  Keine Waagen konfiguriert
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {(isAddingNew || selectedScaleId) && (
        <div className="border rounded-md p-4 space-y-4 bg-muted/50">
          <h3 className="font-medium">{isAddingNew ? "Neue Waage hinzufügen" : "Waage bearbeiten"}</h3>

          <div className="space-y-2">
            <Label htmlFor="scaleName">Waage / Ort</Label>
            <Input
              id="scaleName"
              value={newScaleName}
              onChange={(e) => setNewScaleName(e.target.value)}
              placeholder="z.B. 1.Waage im Lager"
              className={error && !newScaleName ? "border-destructive" : ""}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="scaleIp">IP-Adresse</Label>
            <Input
              id="scaleIp"
              value={newScaleIp}
              onChange={(e) => setNewScaleIp(e.target.value)}
              placeholder="z.B. 192.168.1.100"
              className={error && !newScaleIp ? "border-destructive" : ""}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="scaleTolerance">Toleranz %</Label>
            <Input
              id="scaleTolerance"
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={newScaleTolerance}
              onChange={(e) => setNewScaleTolerance(e.target.value)}
              className={error && !newScaleTolerance ? "border-destructive" : ""}
            />
          </div>

          {error && <p className="text-destructive text-sm">{error}</p>}

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
          Neue
        </Button>
        <Button variant="outline" onClick={handleDelete} disabled={!selectedScaleId}>
          Löschen
        </Button>
      </div>
    </div>
  )
}

