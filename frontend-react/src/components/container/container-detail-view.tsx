"use client"

import { Button } from "@/components/ui/button"
import type { ContainerItem } from "@/types/warehouse-types"
import { Edit } from "lucide-react"

interface ContainerDetailViewProps {
  container: ContainerItem
  onClose: () => void
}

export default function ContainerDetailView({ container, onClose }: ContainerDetailViewProps) {
  // Ensure we have arrays to work with
  const slots = Array.isArray(container.slots) ? container.slots : []
  const units = Array.isArray(container.units) ? container.units : []

  return (
    <div className="bg-white border rounded-lg shadow-lg p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">{container.containerCode}</h2>
        <Button variant="outline" onClick={onClose}>
          Schließen
        </Button>
      </div>

      <div className="space-y-6">
        {/* Container Visualization */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Schütten-Visualisierung</h3>
          <div className="border-2 border-gray-300 rounded-lg p-4">
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
              {slots.map((slot) => {
                const unit = units.find((u) => Array.isArray(u.slots) && u.slots.includes(slot.id))

                return (
                  <div
                    key={slot.id}
                    className={`flex flex-col items-center justify-center ${slot.code.color} text-white font-bold rounded-md h-24 p-2`}
                  >
                    <div className="text-xl">{slot.code.code}</div>
                    <div className="text-sm mt-2">Einheit {unit?.unitNumber || "-"}</div>
                  </div>
                )
              })}
            </div>
          </div>
          <p className="text-sm text-gray-500 text-center">
            Klicken Sie auf Slots, um sie auszuwählen und zu einer neuen Einheit zusammenzufassen
          </p>
        </div>

        {/* Units and Articles Table */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Einheiten und Artikel</h3>
          <div className="border rounded-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Einh.</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Code</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Artikel-Nr.</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">alte Art.-Nr.</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Bezeichnung</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Bestand</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Aktionen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {units.map((unit) => {
                  // Get all slots for this unit
                  const unitSlots = slots.filter((slot) => Array.isArray(unit.slots) && unit.slots.includes(slot.id))

                  return (
                    <tr key={unit.id} className="hover:bg-gray-50">
                      <td className="px-3 py-2 text-xs">{unit.unitNumber}</td>
                      <td className="px-3 py-2 text-xs">
                        <div className="flex flex-wrap gap-1">
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
                      <td className="px-3 py-2 text-xs">{unit.articleNumber || "-"}</td>
                      <td className="px-3 py-2 text-xs">{unit.oldArticleNumber || "-"}</td>
                      <td className="px-3 py-2 text-xs">{unit.description || "-"}</td>
                      <td className="px-3 py-2 text-xs">{unit.stock || 0}</td>
                      <td className="px-3 py-2 text-xs">
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </td>
                    </tr>
                  )
                })}
                {(!units || units.length === 0) && (
                  <tr>
                    <td colSpan={7} className="px-3 py-2 text-center text-xs text-gray-500">
                      Keine Einheiten vorhanden
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

