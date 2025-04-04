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

interface NewWarehouseLocationModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (location: WarehouseLocation) => void
  existingLocations: WarehouseLocation[]
}

const LOCATIONS = [
  { value: "Hauptlager 1", label: "🏢 Hauptlager 1" },
  { value: "Hauptlager 2", label: "🏢 Hauptlager 2" },
  { value: "Externes Lager", label: "🏢 Externes Lager" },
  { value: "Nebenlager", label: "🏢 Nebenlager" },
  { value: "Stammlager-Diessen", label: "🏢 Stammlager-Diessen" },
]

export default function NewWarehouseLocationModal({
  isOpen,
  onClose,
  onSave,
  existingLocations,
}: NewWarehouseLocationModalProps) {
  const [location, setLocation] = useState("")
  const [shelf, setShelf] = useState("")
  const [compartment, setCompartment] = useState("")
  const [floor, setFloor] = useState("")
  const [forSale, setForSale] = useState(false)
  const [specialStorage, setSpecialStorage] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!location) newErrors.location = "Bitte wählen Sie einen Ort/Gebäude"
    if (!shelf) newErrors.shelf = "Bitte geben Sie eine Regalnummer ein"
    if (!compartment) newErrors.compartment = "Bitte geben Sie eine Fachnummer ein"
    if (!floor) newErrors.floor = "Bitte geben Sie eine Bodennummer ein"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    const newLocation: WarehouseLocation = {
      id: crypto.randomUUID(),
      laNumber: generateLANumber(existingLocations),
      location,
      forSale,
      specialStorage,
      shelf: Number.parseInt(shelf),
      compartment: Number.parseInt(compartment),
      floor: Number.parseInt(floor),
      containerCount: 0,
      status: "free", // New locations are always free
    }

    onSave(newLocation)
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">Neuen Lagerort anlegen</Dialog.Title>
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

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="shelf">Regal</Label>
                <Input
                  id="shelf"
                  type="number"
                  min="1"
                  value={shelf}
                  onChange={(e) => setShelf(e.target.value)}
                  className={errors.shelf ? "border-destructive" : ""}
                />
                {errors.shelf && <p className="text-destructive text-sm">{errors.shelf}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="compartment">Fach</Label>
                <Input
                  id="compartment"
                  type="number"
                  min="1"
                  value={compartment}
                  onChange={(e) => setCompartment(e.target.value)}
                  className={errors.compartment ? "border-destructive" : ""}
                />
                {errors.compartment && <p className="text-destructive text-sm">{errors.compartment}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="floor">Boden</Label>
                <Input
                  id="floor"
                  type="number"
                  min="1"
                  value={floor}
                  onChange={(e) => setFloor(e.target.value)}
                  className={errors.floor ? "border-destructive" : ""}
                />
                {errors.floor && <p className="text-destructive text-sm">{errors.floor}</p>}
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

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="submit">Speichern</Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

