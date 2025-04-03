"use client"

import type React from "react"

import { useState } from "react"
import { X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { generateLANumber } from "@/lib/warehouse-service"
// Update the import to use the types file
import type { WarehouseLocation } from "@/types/warehouse-types"

interface MultipleWarehouseLocationsModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (locations: WarehouseLocation[]) => void
  existingLocations: WarehouseLocation[]
}

const LOCATIONS = [
  { value: "Hauptlager 1", label: "🏢 Hauptlager 1" },
  { value: "Hauptlager 2", label: "🏢 Hauptlager 2" },
  { value: "Externes Lager", label: "🏢 Externes Lager" },
  { value: "Nebenlager", label: "🏢 Nebenlager" },
]

export default function MultipleWarehouseLocationsModal({
  isOpen,
  onClose,
  onSave,
  existingLocations,
}: MultipleWarehouseLocationsModalProps) {
  const [location, setLocation] = useState("")
  const [shelfStart, setShelfStart] = useState("")
  const [shelfCount, setShelfCount] = useState("")
  const [compartmentStart, setCompartmentStart] = useState("")
  const [compartmentCount, setCompartmentCount] = useState("")
  const [floorStart, setFloorStart] = useState("")
  const [floorCount, setFloorCount] = useState("")
  const [forSale, setForSale] = useState(false)
  const [specialStorage, setSpecialStorage] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [preview, setPreview] = useState<WarehouseLocation[]>([])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!location) newErrors.location = "Bitte wählen Sie einen Ort/Gebäude"
    if (!shelfStart) newErrors.shelfStart = "Bitte geben Sie eine Start-Regalnummer ein"
    if (!shelfCount) newErrors.shelfCount = "Bitte geben Sie die Anzahl der Regale ein"
    if (!compartmentStart) newErrors.compartmentStart = "Bitte geben Sie eine Start-Fachnummer ein"
    if (!compartmentCount) newErrors.compartmentCount = "Bitte geben Sie die Anzahl der Fächer ein"
    if (!floorStart) newErrors.floorStart = "Bitte geben Sie eine Start-Bodennummer ein"
    if (!floorCount) newErrors.floorCount = "Bitte geben Sie die Anzahl der Böden ein"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const generatePreview = () => {
    if (!validateForm()) return

    const newLocations: WarehouseLocation[] = []
    const shelfStartNum = Number.parseInt(shelfStart)
    const shelfCountNum = Number.parseInt(shelfCount)
    const compartmentStartNum = Number.parseInt(compartmentStart)
    const compartmentCountNum = Number.parseInt(compartmentCount)
    const floorStartNum = Number.parseInt(floorStart)
    const floorCountNum = Number.parseInt(floorCount)

    // Generate all combinations
    for (let s = 0; s < shelfCountNum; s++) {
      const currentShelf = shelfStartNum + s

      for (let c = 0; c < compartmentCountNum; c++) {
        const currentCompartment = compartmentStartNum + c

        for (let f = 0; f < floorCountNum; f++) {
          const currentFloor = floorStartNum + f

          newLocations.push({
            id: `preview-${currentShelf}-${currentCompartment}-${currentFloor}`,
            laNumber: `LA-Vorschau`,
            location,
            forSale,
            specialStorage,
            shelf: currentShelf,
            compartment: currentCompartment,
            floor: currentFloor,
            containerCount: 0,
            status: "free",
          })
        }
      }
    }

    setPreview(newLocations)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    const newLocations: WarehouseLocation[] = []
    const shelfStartNum = Number.parseInt(shelfStart)
    const shelfCountNum = Number.parseInt(shelfCount)
    const compartmentStartNum = Number.parseInt(compartmentStart)
    const compartmentCountNum = Number.parseInt(compartmentCount)
    const floorStartNum = Number.parseInt(floorStart)
    const floorCountNum = Number.parseInt(floorCount)

    // Generate all combinations
    for (let s = 0; s < shelfCountNum; s++) {
      const currentShelf = shelfStartNum + s

      for (let c = 0; c < compartmentCountNum; c++) {
        const currentCompartment = compartmentStartNum + c

        for (let f = 0; f < floorCountNum; f++) {
          const currentFloor = floorStartNum + f

          newLocations.push({
            id: crypto.randomUUID(),
            laNumber: generateLANumber(existingLocations),
            location,
            forSale,
            specialStorage,
            shelf: currentShelf,
            compartment: currentCompartment,
            floor: currentFloor,
            containerCount: 0,
            status: "free",
          })
        }
      }
    }

    onSave(newLocations)
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-2xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none overflow-y-auto">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">Mehrere Lagerorte anlegen</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="location">Ort/Gebäude</Label>
              <Select
                value={location}
                onValueChange={setLocation}
              >
                <SelectTrigger className={errors.location ? "border-destructive" : ""}>
                  <SelectValue placeholder="Ort/Gebäude auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {LOCATIONS.map((loc) => (
                    <SelectItem key={loc.value} value={loc.value}>
                      {loc.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.location && <p className="text-destructive text-sm">{errors.location}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="shelfStart">Regal</Label>
                    <Input
                      id="shelfStart"
                      type="number"
                      min="1"
                      value={shelfStart}
                      onChange={(e) => setShelfStart(e.target.value)}
                      className={errors.shelfStart ? "border-destructive" : ""}
                      placeholder="Start"
                    />
                    {errors.shelfStart && <p className="text-destructive text-sm">{errors.shelfStart}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="shelfCount">Anzahl</Label>
                    <Input
                      id="shelfCount"
                      type="number"
                      min="1"
                      value={shelfCount}
                      onChange={(e) => setShelfCount(e.target.value)}
                      className={errors.shelfCount ? "border-destructive" : ""}
                    />
                    {errors.shelfCount && <p className="text-destructive text-sm">{errors.shelfCount}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="compartmentStart">Fach</Label>
                    <Input
                      id="compartmentStart"
                      type="number"
                      min="1"
                      value={compartmentStart}
                      onChange={(e) => setCompartmentStart(e.target.value)}
                      className={errors.compartmentStart ? "border-destructive" : ""}
                      placeholder="Start"
                    />
                    {errors.compartmentStart && <p className="text-destructive text-sm">{errors.compartmentStart}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="compartmentCount">Anzahl</Label>
                    <Input
                      id="compartmentCount"
                      type="number"
                      min="1"
                      value={compartmentCount}
                      onChange={(e) => setCompartmentCount(e.target.value)}
                      className={errors.compartmentCount ? "border-destructive" : ""}
                    />
                    {errors.compartmentCount && <p className="text-destructive text-sm">{errors.compartmentCount}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="floorStart">Boden</Label>
                    <Input
                      id="floorStart"
                      type="number"
                      min="1"
                      value={floorStart}
                      onChange={(e) => setFloorStart(e.target.value)}
                      className={errors.floorStart ? "border-destructive" : ""}
                      placeholder="Start"
                    />
                    {errors.floorStart && <p className="text-destructive text-sm">{errors.floorStart}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="floorCount">Anzahl</Label>
                    <Input
                      id="floorCount"
                      type="number"
                      min="1"
                      value={floorCount}
                      onChange={(e) => setFloorCount(e.target.value)}
                      className={errors.floorCount ? "border-destructive" : ""}
                    />
                    {errors.floorCount && <p className="text-destructive text-sm">{errors.floorCount}</p>}
                  </div>
                </div>

                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox id="forSale" checked={forSale} onCheckedChange={(checked) => setForSale(!!checked)} />
                    <Label htmlFor="forSale" className="cursor-pointer">
                      Lagerort für Abverkauf
                    </Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="specialStorage"
                      checked={specialStorage}
                      onCheckedChange={(checked) => setSpecialStorage(!!checked)}
                    />
                    <Label htmlFor="specialStorage" className="cursor-pointer">
                      Sonderlagerort Lagerort
                    </Label>
                  </div>
                </div>

                <Button type="button" variant="outline" onClick={generatePreview} className="w-full">
                  Vorschau generieren
                </Button>
              </div>

              <div className="border rounded-md p-4 space-y-4">
                <h3 className="font-medium">Vorschau</h3>
                <p className="text-sm text-muted-foreground">
                  {preview.length > 0
                    ? `${preview.length} Lagerorte werden erstellt`
                    : 'Füllen Sie das Formular aus und klicken Sie auf "Vorschau generieren"'}
                </p>

                {preview.length > 0 && (
                  <div className="max-h-60 overflow-y-auto border rounded-md">
                    <table className="min-w-full divide-y divide-border">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Regal</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Fach</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Boden</th>
                        </tr>
                      </thead>
                      <tbody className="bg-background divide-y divide-border">
                        {preview.map((loc) => (
                          <tr key={loc.id} className="hover:bg-muted/50">
                            <td className="px-3 py-2 text-xs">{loc.shelf}</td>
                            <td className="px-3 py-2 text-xs">{loc.compartment}</td>
                            <td className="px-3 py-2 text-xs">{loc.floor}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="submit" disabled={preview.length === 0}>
                {preview.length} Lagerorte anlegen
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

