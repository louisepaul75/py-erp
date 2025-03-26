"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { usePurposeStore } from "@/lib/stores/purpose-store"

export default function PurposeSettings() {
  const { purposes, addPurpose, deletePurpose } = usePurposeStore()
  const [selectedPurposeId, setSelectedPurposeId] = useState<string | null>(null)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [newPurposeName, setNewPurposeName] = useState("")
  const [error, setError] = useState("")

  const handleAddNew = () => {
    setIsAddingNew(true)
    setSelectedPurposeId(null)
    setNewPurposeName("")
    setError("")
  }

  const handleSave = () => {
    if (!newPurposeName.trim()) {
      setError("Bitte geben Sie einen Zweck ein")
      return
    }

    // Prüfen, ob der Zweck bereits existiert
    if (purposes.some((p) => p.name.toLowerCase() === newPurposeName.toLowerCase())) {
      setError("Dieser Zweck existiert bereits")
      return
    }

    addPurpose({
      id: crypto.randomUUID(),
      name: newPurposeName,
    })

    setIsAddingNew(false)
    setNewPurposeName("")
    setError("")
  }

  const handleDelete = () => {
    if (selectedPurposeId) {
      deletePurpose(selectedPurposeId)
      setSelectedPurposeId(null)
    }
  }

  const handleSelectPurpose = (id: string) => {
    setSelectedPurposeId(id)
    setIsAddingNew(false)
    setError("")
  }

  const handleCancel = () => {
    setIsAddingNew(false)
    setNewPurposeName("")
    setError("")
  }

  return (
    <div className="space-y-4">
      <div className="border rounded-md overflow-hidden max-h-[400px] overflow-y-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Schüttenzweck</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {purposes.length > 0 ? (
              purposes.map((purpose) => (
                <tr
                  key={purpose.id}
                  className={`hover:bg-gray-50 cursor-pointer ${selectedPurposeId === purpose.id ? "bg-blue-50" : ""}`}
                  onClick={() => handleSelectPurpose(purpose.id)}
                >
                  <td className="px-4 py-3 text-black">{purpose.name}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-6 text-center text-gray-500">Keine Zwecke definiert</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isAddingNew && (
        <div className="border rounded-md p-4 space-y-4">
          <h3 className="font-medium">Neuen Zweck hinzufügen</h3>

          <div className="space-y-2">
            <Input
              value={newPurposeName}
              onChange={(e) => setNewPurposeName(e.target.value)}
              placeholder="Zweck eingeben"
              className={error ? "border-red-500" : ""}
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
          Neue
        </Button>
        <Button variant="outline" onClick={handleDelete} disabled={!selectedPurposeId}>
          Löschen
        </Button>
      </div>
    </div>
  )
}

