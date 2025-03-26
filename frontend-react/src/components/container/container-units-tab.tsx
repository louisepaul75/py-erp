"use client"

import { useState } from "react"
import { Plus, Edit, Check, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { ContainerItem } from "@/types/warehouse-types"
import { createUnitFromSlots, findArticleByNumber, assignArticleToUnit } from "@/lib/container-utils"

interface ContainerUnitsTabProps {
  editedContainer: ContainerItem
  setEditedContainer: (container: ContainerItem) => void
  selectedUnitId: string | null
  setSelectedUnitId: (id: string | null) => void
  selectedSlotIds: string[]
  setSelectedSlotIds: (ids: string[]) => void
  onSplitUnit: () => void
  showConfirmationDialog: (action: () => void) => void
}

export default function ContainerUnitsTab({
  editedContainer,
  setEditedContainer,
  selectedUnitId,
  setSelectedUnitId,
  selectedSlotIds,
  setSelectedSlotIds,
  onSplitUnit,
  showConfirmationDialog,
}: ContainerUnitsTabProps) {
  const [editingUnitId, setEditingUnitId] = useState<string | null>(null)
  const [articleSearchTerm, setArticleSearchTerm] = useState("")
  const [isSearchingArticle, setIsSearchingArticle] = useState(false)

  // Ensure we have arrays to work with
  const slots = Array.isArray(editedContainer.slots) ? editedContainer.slots : []
  const units = Array.isArray(editedContainer.units) ? editedContainer.units : []

  // Function to handle creating a new unit from selected slots
  const handleCreateUnit = () => {
    try {
      // Check if this would delete article data
      const affectedUnits = selectedSlotIds
        .map((slotId) => {
          return units.find((unit) => Array.isArray(unit.slots) && unit.slots.includes(slotId))
        })
        .filter(Boolean)

      const hasArticleData = affectedUnits.some(
        (unit) =>
          unit && (unit.articleNumber || unit.oldArticleNumber || unit.description || (unit.stock && unit.stock > 0)),
      )

      // If there's only one unit with all slots selected, we should preserve the article data
      const isSingleUnitSelected =
        units.length === 1 && selectedSlotIds.length === slots.length && affectedUnits.length === 1

      if (hasArticleData && !isSingleUnitSelected) {
        // Show confirmation dialog
        showConfirmationDialog(() => {
          const updatedContainer = createUnitFromSlots(editedContainer, selectedSlotIds)
          setEditedContainer(updatedContainer)
          setSelectedSlotIds([])
        })
      } else {
        // If we're selecting all slots from a single unit, preserve the article data
        if (isSingleUnitSelected && affectedUnits[0]) {
          const articleData = {
            articleNumber: affectedUnits[0].articleNumber,
            oldArticleNumber: affectedUnits[0].oldArticleNumber,
            description: affectedUnits[0].description,
            stock: affectedUnits[0].stock,
          }

          // Create new unit but preserve article data
          const updatedContainer = createUnitFromSlots(editedContainer, selectedSlotIds)

          // Find the newly created unit and assign article data
          if (updatedContainer.units.length > 0) {
            const newUnit = updatedContainer.units[0]
            const updatedUnits = updatedContainer.units.map((unit) => {
              if (unit.id === newUnit.id) {
                return {
                  ...unit,
                  ...articleData,
                }
              }
              return unit
            })

            setEditedContainer({
              ...updatedContainer,
              units: updatedUnits,
            })
          } else {
            setEditedContainer(updatedContainer)
          }
          setSelectedSlotIds([])
        } else {
          // No article data to lose, proceed normally
          const updatedContainer = createUnitFromSlots(editedContainer, selectedSlotIds)
          setEditedContainer(updatedContainer)
          setSelectedSlotIds([])
        }
      }
    } catch (error) {
      console.error("Error creating unit from slots:", error)
    }
  }

  // Function to handle article assignment
  const handleAssignArticle = (
    unitId: string,
    articleData: {
      articleNumber: string
      oldArticleNumber: string
      description: string
      stock: number
    },
  ) => {
    try {
      if (!Array.isArray(editedContainer.units)) {
        return
      }

      const updatedUnits = editedContainer.units.map((unit) => {
        if (unit.id === unitId) {
          return {
            ...unit,
            ...articleData,
          }
        }
        return unit
      })

      const updatedContainer = {
        ...editedContainer,
        units: updatedUnits,
      }

      setEditedContainer(updatedContainer)
    } catch (error) {
      console.error("Error assigning article:", error)
    }
  }

  // Function to handle article search
  const handleSearchArticle = () => {
    try {
      if (!articleSearchTerm || !editingUnitId) return

      setIsSearchingArticle(true)

      // Simulate API call delay
      setTimeout(() => {
        // Check if it's an article number or old article number
        const isOldArticleNumber = articleSearchTerm.includes("-")

        // Find article
        const article = findArticleByNumber(
          editedContainer,
          isOldArticleNumber ? "" : articleSearchTerm,
          isOldArticleNumber ? articleSearchTerm : "",
        )

        if (article) {
          // Assign article to the selected unit
          const updatedContainer = assignArticleToUnit(
            editedContainer, 
            editingUnitId, 
            article.articleNumber || "",
            article.description || ""
          )
          setEditedContainer(updatedContainer)
        }

        setIsSearchingArticle(false)
        setArticleSearchTerm("")
      }, 500)
    } catch (error) {
      console.error("Error searching article:", error)
      setIsSearchingArticle(false)
    }
  }

  // Functions for unit editing
  const startEditingUnit = (unitId: string) => {
    setEditingUnitId(unitId)
  }

  const stopEditingUnit = () => {
    setEditingUnitId(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="font-medium text-lg">Einheiten und Artikel</h3>
        <div className="flex gap-2">
          {selectedSlotIds.length > 0 && (
            <Button variant="outline" size="sm" onClick={handleCreateUnit} className="flex items-center gap-1">
              <Plus className="h-4 w-4" />
              Neue Einheit
            </Button>
          )}
          {selectedUnitId && (() => {
            const selectedUnit = units.find((u) => u.id === selectedUnitId);
            return selectedUnit && Array.isArray(selectedUnit.slots) && selectedUnit.slots.length > 1 ? (
              <Button variant="outline" size="sm" onClick={onSplitUnit} className="flex items-center gap-1">
                Einheit teilen
              </Button>
            ) : null;
          })()}
        </div>
      </div>

      {/* Container visualization */}
      <div className="border rounded-md p-4 bg-gray-50">
        <h4 className="font-medium mb-4">Schütten-Visualisierung</h4>
        <div className="flex flex-col items-center">
          <div className="border-2 border-gray-400 rounded-md p-4 w-full max-w-3xl">
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2 max-h-[300px] overflow-y-auto p-2">
              {slots.map((slot) => {
                const unit = units.find((u) => Array.isArray(u.slots) && u.slots.includes(slot.id))
                const isSelected = selectedSlotIds.includes(slot.id)

                return (
                  <div
                    key={slot.id}
                    className={`flex items-center justify-center border ${slot.code.color} text-white font-bold rounded-md cursor-pointer ${
                      isSelected ? "ring-4 ring-blue-500" : ""
                    } h-16`}
                    onClick={() => {
                      if (selectedSlotIds.includes(slot.id)) {
                        setSelectedSlotIds(selectedSlotIds.filter((id) => id !== slot.id))
                      } else {
                        setSelectedSlotIds([...selectedSlotIds, slot.id])
                      }
                    }}
                  >
                    <div className="text-center">
                      <div>{slot.code.code}</div>
                      <div className="text-xs mt-1">Einheit {unit?.unitNumber || "-"}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          <div className="text-sm text-gray-500 mt-2">
            Klicken Sie auf Slots, um sie auszuwählen und zu einer neuen Einheit zusammenzufassen
          </div>
        </div>
      </div>

      <div className="border rounded-md overflow-hidden">
        <div className="max-h-[300px] overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-100 sticky top-0 z-10">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Einh.</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Code</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Artikel-Nr.</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">alte Art.-Nr.</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Bezeichnung</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Bestand</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Aktionen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {units.map((unit) => {
                // Get all slots for this unit
                const unitSlots = slots.filter((slot) => Array.isArray(unit.slots) && unit.slots.includes(slot.id))
                const isEditing = editingUnitId === unit.id

                return (
                  <tr
                    key={unit.id}
                    className={`hover:bg-gray-50 cursor-pointer ${selectedUnitId === unit.id ? "bg-blue-50" : ""}`}
                    onClick={() => setSelectedUnitId(unit.id)}
                  >
                    <td className="px-4 py-2 text-sm">{unit.unitNumber}</td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap gap-1 max-w-[200px]">
                        {unitSlots.map((slot) => (
                          <span
                            key={slot.id}
                            className={`inline-flex items-center justify-center w-10 h-6 ${slot.code.color} text-white font-medium rounded`}
                          >
                            {slot.code.code}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {isEditing ? (
                        <Input
                          value={unit.articleNumber || ""}
                          onChange={(e) =>
                            handleAssignArticle(unit.id, {
                              articleNumber: e.target.value,
                              oldArticleNumber: unit.oldArticleNumber || "",
                              description: unit.description || "",
                              stock: unit.stock || 0,
                            })
                          }
                          className="w-full"
                        />
                      ) : (
                        <div className="flex items-center">
                          <span className="font-medium">{unit.articleNumber || "-"}</span>
                          {unit.oldArticleNumber && (
                            <span className="text-xs text-gray-500 ml-1">({unit.oldArticleNumber})</span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {isEditing ? (
                        <Input
                          value={unit.oldArticleNumber || ""}
                          onChange={(e) =>
                            handleAssignArticle(unit.id, {
                              articleNumber: unit.articleNumber || "",
                              oldArticleNumber: e.target.value,
                              description: unit.description || "",
                              stock: unit.stock || 0,
                            })
                          }
                          className="w-full"
                        />
                      ) : (
                        unit.oldArticleNumber || "-"
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {isEditing ? (
                        <Input
                          value={unit.description || ""}
                          onChange={(e) =>
                            handleAssignArticle(unit.id, {
                              articleNumber: unit.articleNumber || "",
                              oldArticleNumber: unit.oldArticleNumber || "",
                              description: e.target.value,
                              stock: unit.stock || 0,
                            })
                          }
                          className="w-full"
                        />
                      ) : (
                        <div className="max-w-xs truncate">{unit.description || "-"}</div>
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {isEditing ? (
                        <Input
                          type="number"
                          value={unit.stock || 0}
                          onChange={(e) =>
                            handleAssignArticle(unit.id, {
                              articleNumber: unit.articleNumber || "",
                              oldArticleNumber: unit.oldArticleNumber || "",
                              description: unit.description || "",
                              stock: Number.parseInt(e.target.value) || 0,
                            })
                          }
                          className="w-full"
                        />
                      ) : (
                        unit.stock || 0
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {isEditing ? (
                        <Button size="sm" variant="outline" onClick={stopEditingUnit}>
                          <Check className="h-4 w-4 mr-1" />
                          Fertig
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" onClick={() => startEditingUnit(unit.id)}>
                          <Edit className="h-4 w-4 mr-1" />
                          Bearbeiten
                        </Button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {editingUnitId && (
        <div className="border rounded-md p-4 bg-gray-50">
          <h4 className="font-medium mb-2">Artikel suchen</h4>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                value={articleSearchTerm}
                onChange={(e) => setArticleSearchTerm(e.target.value)}
                placeholder="z.B. 123456 oder 13200-BE"
                className="pr-8"
              />
              <Search className="absolute right-2 top-2.5 h-4 w-4 text-gray-400" />
            </div>
            <Button onClick={handleSearchArticle} disabled={isSearchingArticle || !articleSearchTerm}>
              {isSearchingArticle ? "Suche..." : "Suchen"}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

