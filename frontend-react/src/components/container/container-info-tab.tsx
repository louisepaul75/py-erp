"use client"

import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { generateContainerSlots, generateInitialUnits } from "@/lib/container-utils"
import type { ContainerItem } from "@/types/warehouse-types"

interface ContainerInfoTabProps {
  container: ContainerItem
  editedContainer: ContainerItem
  setEditedContainer: (container: ContainerItem) => void
  isEditing: boolean
  slotCount: number
  setSlotCount: (count: number) => void
  dateInfo: {
    createdAt: Date
    lastModified: Date
    printedAt: Date
  }
}

export default function ContainerInfoTab({
  container,
  editedContainer,
  setEditedContainer,
  isEditing,
  slotCount,
  setSlotCount,
  dateInfo,
}: ContainerInfoTabProps) {
  // Ensure we have arrays to work with
  const slots = Array.isArray(editedContainer.slots) ? editedContainer.slots : []
  const units = Array.isArray(editedContainer.units) ? editedContainer.units : []

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-medium text-lg">Schütten-Informationen</h3>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Schütten-Code</Label>
            {isEditing ? (
              <Input
                value={editedContainer.containerCode}
                onChange={(e) => {
                  setEditedContainer({
                    ...editedContainer,
                    containerCode: e.target.value,
                  })
                }}
              />
            ) : (
              <div className="p-2 border rounded-md bg-gray-50">{container.containerCode}</div>
            )}
          </div>

          <div className="space-y-2">
            <Label>Typ</Label>
            {isEditing ? (
              <Select
                value={editedContainer.type}
                onValueChange={(value) => {
                  try {
                    // Update slots when type changes
                    const newSlots = generateContainerSlots(value, [], slotCount)
                    const newUnits = generateInitialUnits(newSlots)

                    setEditedContainer({
                      ...editedContainer,
                      type: value,
                      slots: Array.isArray(newSlots) ? newSlots : [],
                      units: Array.isArray(newUnits) ? newUnits : [],
                    })
                  } catch (error) {
                    console.error("Error changing type:", error)
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Typ auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="OD">OD</SelectItem>
                  <SelectItem value="KC">KC</SelectItem>
                  <SelectItem value="PT">PT</SelectItem>
                  <SelectItem value="JK">JK</SelectItem>
                  <SelectItem value="AR">AR</SelectItem>
                  <SelectItem value="HF">HF</SelectItem>
                </SelectContent>
              </Select>
            ) : (
              <div className="p-2 border rounded-md bg-gray-50">{container.type}</div>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Zweck</Label>
          {isEditing ? (
            <Select
              value={
                container.type === "OD" || container.type === "KC"
                  ? "Transport"
                  : container.type === "PT" || container.type === "JK"
                    ? "Picken"
                    : "Lager"
              }
              onValueChange={(value) => {
                // Hier würde die Logik zum Ändern des Zwecks implementiert werden
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Zweck auswählen" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Lager">Lager</SelectItem>
                <SelectItem value="Transport">Transport</SelectItem>
                <SelectItem value="Picken">Picken</SelectItem>
                <SelectItem value="Werkstatt">Werkstatt</SelectItem>
              </SelectContent>
            </Select>
          ) : (
            <div className="p-2 border rounded-md bg-gray-50">
              {container.type === "OD" || container.type === "KC"
                ? "Transport"
                : container.type === "PT" || container.type === "JK"
                  ? "Picken"
                  : "Lager"}
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Slots</Label>
            {isEditing ? (
              <Input
                type="number"
                min="1"
                max="30"
                value={slotCount}
                onChange={(e) => setSlotCount(Number.parseInt(e.target.value) || 1)}
              />
            ) : (
              <div className="p-2 border rounded-md bg-gray-50">{slots.length || 1}</div>
            )}
          </div>

          <div className="space-y-2">
            <Label>Einheiten</Label>
            <div className="p-2 border rounded-md bg-gray-50">
              {editedContainer.units?.filter((u) => u.articleNumber || u.description || u.stock > 0).length || 0}/
              {editedContainer.units?.length || 0}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Angelegt am</Label>
            <div className="p-2 border rounded-md bg-gray-50">{dateInfo.createdAt.toLocaleDateString("de-DE")}</div>
          </div>

          <div className="space-y-2">
            <Label>Angelegt um</Label>
            <div className="p-2 border rounded-md bg-gray-50">
              {dateInfo.createdAt.toLocaleTimeString("de-DE", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Gedruckt am</Label>
            <div className="p-2 border rounded-md bg-gray-50">{dateInfo.printedAt.toLocaleDateString("de-DE")}</div>
          </div>

          <div className="space-y-2">
            <Label>Gedruckt um</Label>
            <div className="p-2 border rounded-md bg-gray-50">
              {dateInfo.printedAt.toLocaleTimeString("de-DE", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-medium text-lg">Slot-Codes</h3>

        <div className="border rounded-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Nr.</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Code</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Einheit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {slots.map((slot, index) => {
                const unit = units.find((u) => Array.isArray(u.slots) && u.slots.includes(slot.id))
                return (
                  <tr key={slot.id}>
                    <td className="px-4 py-2 text-sm">{index + 1}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`inline-flex items-center justify-center w-10 h-6 ${slot.code.color} text-white font-medium rounded`}
                      >
                        {slot.code.code}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">{unit?.unitNumber || "-"}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

