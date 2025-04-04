"use client"

import type React from "react"

import { useState } from "react"
import { X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import type { ContainerItem } from "@/types/warehouse-types"

const CONTAINER_TYPES = [
  { value: "OD", label: "OD" },
  { value: "KC", label: "KC" },
  { value: "PT", label: "PT" },
  { value: "JK", label: "JK" },
  { value: "AR", label: "AR" },
  { value: "HF", label: "HF" },
]

const PURPOSES = [
  { value: "Lager", label: "Lager" },
  { value: "Transport", label: "Transport" },
  { value: "Picken", label: "Picken" },
  { value: "Werkstatt", label: "Werkstatt" },
]

interface CreateContainerDialogProps {
  isOpen: boolean
  onClose: () => void
  onSave: (container: ContainerItem) => void
  generateContainerCode: () => string
}

export default function CreateContainerDialog({
  isOpen,
  onClose,
  onSave,
  generateContainerCode,
}: CreateContainerDialogProps) {
  const [type, setType] = useState("")
  const [purpose, setPurpose] = useState("Lager")
  const [quantity, setQuantity] = useState("1")
  const [slotCount, setSlotCount] = useState("1")
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!type) newErrors.type = "Bitte wählen Sie einen Typ aus"
    if (!purpose) newErrors.purpose = "Bitte wählen Sie einen Zweck aus"

    const qty = Number.parseInt(quantity)
    if (isNaN(qty) || qty < 1) {
      newErrors.quantity = "Bitte geben Sie eine gültige Menge ein (mindestens 1)"
    }

    const slots = Number.parseInt(slotCount)
    if (isNaN(slots) || slots < 1 || slots > 30) {
      newErrors.slotCount = "Bitte geben Sie eine gültige Anzahl Slots ein (1-30)"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    const qty = Number.parseInt(quantity)
    const slots = Number.parseInt(slotCount)
    const containers: ContainerItem[] = []

    for (let i = 0; i < qty; i++) {
      containers.push({
        id: crypto.randomUUID(),
        containerCode: generateContainerCode(),
        type,
        description: "",
        status: "",
        purpose: purpose,
        stock: 0,
        slots: [],
        units: [],
        customSlotCount: slots,
      })
    }

    containers.forEach((container) => {
      onSave(container)
    })

    onClose()
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b w-full">
            <Dialog.Title className="text-xl font-semibold">Neue Schütte erstellen</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Typ</Label>
                <Select
                  value={type}
                  onValueChange={setType}
                >
                  <SelectTrigger id="type" className={errors.type ? "border-red-500" : ""}>
                    <SelectValue placeholder="Typ auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    {CONTAINER_TYPES.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.type && <p className="text-destructive text-sm">{errors.type}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="purpose">Zweck</Label>
                <Select
                  value={purpose}
                  onValueChange={setPurpose}
                >
                  <SelectTrigger id="purpose" className={errors.purpose ? "border-red-500" : ""}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PURPOSES.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.purpose && <p className="text-destructive text-sm">{errors.purpose}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Menge (Anzahl zu erstellender Schütten)</Label>
              <Input
                id="quantity"
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className={errors.quantity ? "border-destructive" : ""}
              />
              {errors.quantity && <p className="text-destructive text-sm">{errors.quantity}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="slotCount">Anzahl Slots (1-30)</Label>
              <Input
                id="slotCount"
                type="number"
                min="1"
                max="30"
                value={slotCount}
                onChange={(e) => setSlotCount(e.target.value)}
                className={errors.slotCount ? "border-destructive" : ""}
              />
              {errors.slotCount && <p className="text-destructive text-sm">{errors.slotCount}</p>}
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

