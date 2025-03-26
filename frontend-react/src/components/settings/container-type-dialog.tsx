"use client"

import type React from "react"

import { useState, useRef } from "react"
import { X, Trash2, Upload } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useContainerTypeStore, type ContainerType, type ContainerTypeImage } from "@/lib/stores/container-type-store"

interface ContainerTypeDialogProps {
  isOpen: boolean
  onClose: () => void
  containerType: ContainerType | null
  isCreating: boolean
}

export default function ContainerTypeDialog({ isOpen, onClose, containerType, isCreating }: ContainerTypeDialogProps) {
  const { addContainerType, updateContainerType, addImageToContainerType, deleteImageFromContainerType } =
    useContainerTypeStore()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [formData, setFormData] = useState<ContainerType>(
    containerType || {
      id: crypto.randomUUID(),
      name: "",
      manufacturer: "",
      articleNumber: "",
      length: 0,
      width: 0,
      height: 0,
      boxWeight: 0,
      dividerWeight: 0,
      standardSlots: 1,
      images: [],
    },
  )

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target

    if (["length", "width", "height", "boxWeight", "dividerWeight", "standardSlots"].includes(name)) {
      setFormData({
        ...formData,
        [name]: Number(value),
      })
    } else {
      setFormData({
        ...formData,
        [name]: value,
      })
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name) newErrors.name = "Schüttentype ist erforderlich"
    if (!formData.manufacturer) newErrors.manufacturer = "Hersteller ist erforderlich"
    if (!formData.articleNumber) newErrors.articleNumber = "Artikel-Nr. ist erforderlich"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    if (isCreating) {
      addContainerType(formData)
    } else {
      updateContainerType(formData.id, formData)
    }

    onClose()
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    // In einer echten Anwendung würden wir die Datei zu einem Server hochladen
    // Hier simulieren wir das mit einer lokalen URL
    const file = files[0]
    const reader = new FileReader()

    reader.onload = (event) => {
      if (event.target && event.target.result) {
        const newImage: ContainerTypeImage = {
          id: crypto.randomUUID(),
          url: event.target.result as string,
        }

        // Direkt zum formData hinzufügen
        setFormData({
          ...formData,
          images: [...formData.images, newImage],
        })

        // In einer echten Anwendung würden wir hier addImageToContainerType aufrufen
        // wenn der Schüttentyp bereits existiert
        if (!isCreating && containerType) {
          addImageToContainerType(containerType.id, newImage)
        }
      }
    }

    reader.readAsDataURL(file)

    // Zurücksetzen des Datei-Inputs
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleDeleteImage = (imageId: string) => {
    // Aus dem lokalen formData entfernen
    setFormData({
      ...formData,
      images: formData.images.filter((img) => img.id !== imageId),
    })

    // In einer echten Anwendung würden wir hier deleteImageFromContainerType aufrufen
    // wenn der Schüttentyp bereits existiert
    if (!isCreating && containerType) {
      deleteImageFromContainerType(containerType.id, imageId)
    }
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-3xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none overflow-y-auto">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">
              {isCreating ? "Neuen Schüttentyp erstellen" : "Schüttentyp bearbeiten"}
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Schüttentype</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={errors.name ? "border-red-500" : ""}
                />
                {errors.name && <p className="text-red-500 text-sm">{errors.name}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="manufacturer">Hersteller</Label>
                <Input
                  id="manufacturer"
                  name="manufacturer"
                  value={formData.manufacturer}
                  onChange={handleChange}
                  className={errors.manufacturer ? "border-red-500" : ""}
                />
                {errors.manufacturer && <p className="text-red-500 text-sm">{errors.manufacturer}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="articleNumber">Hersteller Art.-Nr.</Label>
                <Input
                  id="articleNumber"
                  name="articleNumber"
                  value={formData.articleNumber}
                  onChange={handleChange}
                  className={errors.articleNumber ? "border-red-500" : ""}
                />
                {errors.articleNumber && <p className="text-red-500 text-sm">{errors.articleNumber}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="standardSlots">Standardanzahl Slots</Label>
                <Input
                  id="standardSlots"
                  name="standardSlots"
                  type="number"
                  min="0"
                  value={formData.standardSlots}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="length">Länge</Label>
                <div className="flex items-center">
                  <Input
                    id="length"
                    name="length"
                    type="number"
                    min="0"
                    value={formData.length}
                    onChange={handleChange}
                  />
                  <span className="ml-2">mm</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="width">Breite</Label>
                <div className="flex items-center">
                  <Input id="width" name="width" type="number" min="0" value={formData.width} onChange={handleChange} />
                  <span className="ml-2">mm</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="height">Höhe</Label>
                <div className="flex items-center">
                  <Input
                    id="height"
                    name="height"
                    type="number"
                    min="0"
                    value={formData.height}
                    onChange={handleChange}
                  />
                  <span className="ml-2">mm</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="boxWeight">Box Gewicht</Label>
                <div className="flex items-center">
                  <Input
                    id="boxWeight"
                    name="boxWeight"
                    type="number"
                    min="0"
                    value={formData.boxWeight}
                    onChange={handleChange}
                  />
                  <span className="ml-2">g</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dividerWeight">Trenner Gewicht</Label>
                <div className="flex items-center">
                  <Input
                    id="dividerWeight"
                    name="dividerWeight"
                    type="number"
                    min="0"
                    value={formData.dividerWeight}
                    onChange={handleChange}
                  />
                  <span className="ml-2">g</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <Label>Bilder</Label>
                <div className="mt-2">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    accept="image/*"
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Bild hochladen
                  </Button>
                </div>
              </div>

              {formData.images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {formData.images.map((image, index) => (
                    <div key={image.id} className="relative">
                      <img
                        src={image.url || "/placeholder.svg"}
                        alt={`Bild ${index + 1}`}
                        className="w-full h-32 object-cover border rounded-md"
                      />
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        className="absolute top-1 right-1 h-6 w-6 p-0"
                        onClick={() => handleDeleteImage(image.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                      <p className="text-xs text-center mt-1">Bild {index + 1}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="submit">{isCreating ? "Erstellen" : "Speichern"}</Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

