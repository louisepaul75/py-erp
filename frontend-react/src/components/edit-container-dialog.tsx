"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import type { ContainerItem } from "./warehouse-location-list"

interface EditContainerDialogProps {
  isOpen: boolean
  onClose: () => void
  container: ContainerItem
  onSave: (container: ContainerItem) => void
}

export default function EditContainerDialog({ isOpen, onClose, container, onSave }: EditContainerDialogProps) {
  const [editedContainer, setEditedContainer] = useState<ContainerItem>({ ...container })
  const [purpose, setPurpose] = useState(
    container.type === "OD" || container.type === "KC"
      ? "Transport"
      : container.type === "PT" || container.type === "JK"
        ? "Picken"
        : "Lager",
  )
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    setEditedContainer({ ...container })
    setPurpose(
      container.type === "OD" || container.type === "KC"
        ? "Transport"
        : container.type === "PT" || container.type === "JK"
          ? "Picken"
          : "Lager",
    )
  }, [container])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!editedContainer.containerCode) newErrors.containerCode = "Bitte geben Sie einen Schütten-Code ein"
    else if (!editedContainer.containerCode.startsWith("SC"))
      newErrors.containerCode = "Der Schütten-Code muss mit SC beginnen"

    if (!editedContainer.type) newErrors.type = "Bitte wählen Sie einen Typ aus"
    if (!purpose) newErrors.purpose = "Bitte wählen Sie einen Zweck aus"
    if (!editedContainer.articleNumber) newErrors.articleNumber = "Bitte geben Sie eine Artikel-Nr. ein"
    if (!editedContainer.description) newErrors.description = "Bitte geben Sie eine Bezeichnung ein"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    onSave(editedContainer)
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">Schütte bearbeiten</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="containerCode">Schütten-Code</Label>
              <Input
                id="containerCode"
                value={editedContainer.containerCode}
                onChange={(e) => setEditedContainer({ ...editedContainer, containerCode: e.target.value })}
                placeholder="SC123456"
                className={errors.containerCode ? "border-red-500" : ""}
              />
              {errors.containerCode && <p className="text-red-500 text-sm">{errors.containerCode}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Typ</Label>
                <Select
                  value={editedContainer.type}
                  onValueChange={(value) => setEditedContainer({ ...editedContainer, type: value })}
                  placeholder="Typ auswählen"
                  options={[
                    { value: "OD", label: "OD" },
                    { value: "KC", label: "KC" },
                    { value: "PT", label: "PT" },
                    { value: "JK", label: "JK" },
                    { value: "AR", label: "AR" },
                    { value: "HF", label: "HF" },
                  ]}
                  error={errors.type}
                />
                {errors.type && <p className="text-red-500 text-sm">{errors.type}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="purpose">Zweck</Label>
                <Select
                  value={purpose}
                  onValueChange={setPurpose}
                  placeholder="Zweck auswählen"
                  options={[
                    { value: "Lager", label: "Lager" },
                    { value: "Transport", label: "Transport" },
                    { value: "Picken", label: "Picken" },
                    { value: "Werkstatt", label: "Werkstatt" },
                  ]}
                  error={errors.purpose}
                />
                {errors.purpose && <p className="text-red-500 text-sm">{errors.purpose}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="articleNumber">Artikel-Nr.</Label>
              <Input
                id="articleNumber"
                value={editedContainer.articleNumber}
                onChange={(e) => setEditedContainer({ ...editedContainer, articleNumber: e.target.value })}
                placeholder="123456"
                className={errors.articleNumber ? "border-red-500" : ""}
              />
              {errors.articleNumber && <p className="text-red-500 text-sm">{errors.articleNumber}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="oldArticleNumber">Alte Artikel-Nr.</Label>
              <Input
                id="oldArticleNumber"
                value={editedContainer.oldArticleNumber}
                onChange={(e) => setEditedContainer({ ...editedContainer, oldArticleNumber: e.target.value })}
                placeholder="9315XXX-BE"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Bezeichnung</Label>
              <Input
                id="description"
                value={editedContainer.description}
                onChange={(e) => setEditedContainer({ ...editedContainer, description: e.target.value })}
                placeholder="Produktbezeichnung"
                className={errors.description ? "border-red-500" : ""}
              />
              {errors.description && <p className="text-red-500 text-sm">{errors.description}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="stock">Bestand</Label>
              <Input
                id="stock"
                type="number"
                min="0"
                value={editedContainer.stock}
                onChange={(e) => setEditedContainer({ ...editedContainer, stock: Number(e.target.value) })}
              />
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

