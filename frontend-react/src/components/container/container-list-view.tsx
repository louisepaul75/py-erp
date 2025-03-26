"use client"

import type React from "react"

import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Edit, Trash2, ArrowUp, ArrowDown } from "lucide-react"
import type { ContainerItem } from "@/types/warehouse-types"

interface ContainerListViewProps {
  containers: ContainerItem[]
  selectedContainers: string[]
  onSelectContainer: (id: string, checked: boolean) => void
  onSelectAll: (checked: boolean) => void
  onEditClick: (container: ContainerItem, e: React.MouseEvent) => void
  onDeleteClick: (container: ContainerItem, e: React.MouseEvent) => void
  onLocationClick?: (shelf: number, compartment: number, floor: number) => void
}

export default function ContainerListView({
  containers,
  selectedContainers,
  onSelectContainer,
  onSelectAll,
  onEditClick,
  onDeleteClick,
  onLocationClick,
}: ContainerListViewProps) {
  const [sortField, setSortField] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc")

  // Function to handle sorting
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  // Function to get sorted data
  const getSortedData = () => {
    if (!sortField) return containers

    return [...containers].sort((a, b) => {
      let valueA: any = a[sortField as keyof ContainerItem]
      let valueB: any = b[sortField as keyof ContainerItem]

      // Handle special cases
      if (sortField === "artikel") {
        valueA = a.units?.[0]?.description || ""
        valueB = b.units?.[0]?.description || ""
      }

      if (valueA === valueB) return 0

      const result = valueA > valueB ? 1 : -1
      return sortDirection === "asc" ? result : -result
    })
  }

  const sortedData = getSortedData()

  // Function to render sort indicator
  const renderSortIndicator = (field: string) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
  }

  // Function to create a sortable header
  const SortableHeader = ({ field, children }: { field: string; children: React.ReactNode }) => (
    <th
      className="px-4 py-3 text-left text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center">
        {children}
        {renderSortIndicator(field)}
      </div>
    </th>
  )

  return (
    <div className="border rounded-md overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-100 sticky top-0 z-10">
          <tr>
            <th className="w-10 px-4 py-3 text-left">
              <Checkbox
                checked={selectedContainers.length === containers.length && containers.length > 0}
                onCheckedChange={(checked) => onSelectAll(!!checked)}
                aria-label="Alle auswählen"
              />
            </th>
            <SortableHeader field="containerCode">Schütten</SortableHeader>
            <SortableHeader field="type">Type</SortableHeader>
            <SortableHeader field="zweck">Zweck</SortableHeader>
            <SortableHeader field="artikel">Artikel</SortableHeader>
            <SortableHeader field="slots">Slots</SortableHeader>
            <SortableHeader field="einh">Einh.</SortableHeader>
            <SortableHeader field="angelegt">angelegt</SortableHeader>
            <SortableHeader field="az">AZ</SortableHeader>
            <SortableHeader field="gedruckt">gedruckt</SortableHeader>
            <SortableHeader field="gz">GZ</SortableHeader>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">-</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {sortedData.length > 0 ? (
            sortedData.map((container) => {
              // Get the primary article from the first unit
              const primaryArticle = container.units?.find(
                (unit) => unit.articleNumber || unit.description || unit.stock,
              )

              // Get the purpose based on container type
              const purpose =
                container.type === "OD" || container.type === "KC"
                  ? "Transport"
                  : container.type === "PT" || container.type === "JK"
                    ? "Picken"
                    : "Lager"

              return (
                <tr key={container.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Checkbox
                      checked={selectedContainers.includes(container.id)}
                      onCheckedChange={(checked) => onSelectContainer(container.id, !!checked)}
                      aria-label={`Schütte ${container.containerCode} auswählen`}
                    />
                  </td>
                  <td className="px-4 py-3">{container.containerCode}</td>
                  <td className="px-4 py-3">{container.type}</td>
                  <td className="px-4 py-3">{purpose}</td>
                  <td className="px-4 py-3">
                    {primaryArticle?.articleNumber && (
                      <div>
                        <span>{primaryArticle.articleNumber}: </span>
                        <span>{primaryArticle.description}</span>
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">{container.slots?.length || 0}</td>
                  <td className="px-4 py-3">1/{container.units?.length || 1}</td>
                  <td className="px-4 py-3">{new Date().toLocaleDateString("de-DE")}</td>
                  <td className="px-4 py-3">
                    {new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}
                  </td>
                  <td className="px-4 py-3">-</td>
                  <td className="px-4 py-3">-</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={(e) => onEditClick(container, e)} title="Bearbeiten">
                        <Edit className="h-4 w-4 text-blue-500" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={(e) => onDeleteClick(container, e)} title="Löschen">
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </td>
                </tr>
              )
            })
          ) : (
            <tr>
              <td colSpan={12} className="px-4 py-6 text-center text-gray-500">
                Keine Schütten gefunden
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

