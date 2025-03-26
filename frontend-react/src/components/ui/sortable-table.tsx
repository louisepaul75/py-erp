"use client"

import type React from "react"

import { useState, useRef } from "react"
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react"

interface Column<T> {
  id: string
  header: string
  cell: (row: T) => React.ReactNode
  sortable?: boolean
}

interface SortableTableProps<T> {
  data: T[]
  columns: Column<T>[]
  onRowClick?: (row: T) => void
  handleRowClick?: (row: T) => void
  renderRow?: (props: { row: T; index: number; columns: Column<T>[] }) => React.ReactNode
}

type SortDirection = "asc" | "desc" | null

interface SortState {
  column: string | null
  direction: SortDirection
}

export function SortableTable<T>({ data, columns, onRowClick, handleRowClick, renderRow }: SortableTableProps<T>) {
  const [sortState, setSortState] = useState<SortState>({ column: null, direction: null })
  const [columnOrder, setColumnOrder] = useState<string[]>(columns.map((col) => col.id))
  const [draggedColumn, setDraggedColumn] = useState<string | null>(null)
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null)
  const headerRefs = useRef<Record<string, HTMLTableCellElement | null>>({})

  // Sortieren der Daten basierend auf dem aktuellen Sortierstatus
  const sortedData = [...data].sort((a: any, b: any) => {
    if (!sortState.column || !sortState.direction) return 0

    const columnId = sortState.column
    const valueA = a[columnId]
    const valueB = b[columnId]

    if (valueA === valueB) return 0

    // Numerische Sortierung für Zahlen
    if (typeof valueA === "number" && typeof valueB === "number") {
      return sortState.direction === "asc" ? valueA - valueB : valueB - valueA
    }

    // String-Sortierung für Texte
    const strA = String(valueA).toLowerCase()
    const strB = String(valueB).toLowerCase()

    return sortState.direction === "asc" ? strA.localeCompare(strB) : strB.localeCompare(strA)
  })

  // Sortierung umschalten
  const toggleSort = (columnId: string) => {
    setSortState((prev) => {
      if (prev.column === columnId) {
        // Zyklus: asc -> desc -> null
        if (prev.direction === "asc") return { column: columnId, direction: "desc" }
        if (prev.direction === "desc") return { column: null, direction: null }
      }
      // Neue Spalte oder zurück zu asc
      return { column: columnId, direction: "asc" }
    })
  }

  // Drag-and-Drop-Funktionen für Spalten
  const handleDragStart = (columnId: string) => {
    setDraggedColumn(columnId)
  }

  const handleDragOver = (e: React.DragEvent, columnId: string) => {
    e.preventDefault()
    if (draggedColumn && draggedColumn !== columnId) {
      setDragOverColumn(columnId)
    }
  }

  const handleDrop = (columnId: string) => {
    if (!draggedColumn || draggedColumn === columnId) return

    const newColumnOrder = [...columnOrder]
    const draggedIndex = newColumnOrder.indexOf(draggedColumn)
    const dropIndex = newColumnOrder.indexOf(columnId)

    newColumnOrder.splice(draggedIndex, 1)
    newColumnOrder.splice(dropIndex, 0, draggedColumn)

    setColumnOrder(newColumnOrder)
    setDraggedColumn(null)
    setDragOverColumn(null)
  }

  const handleDragEnd = () => {
    setDraggedColumn(null)
    setDragOverColumn(null)
  }

  // Sortierte und neu angeordnete Spalten
  const orderedColumns = columnOrder.map((id) => columns.find((col) => col.id === id)).filter(Boolean) as Column<T>[]

  // Use the provided click handler or default to onRowClick
  const rowClickHandler = handleRowClick || onRowClick

  return (
    <div className="overflow-x-auto overflow-y-auto" style={{ maxHeight: "600px" }}>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-100 sticky top-0 z-10">
          <tr>
            {orderedColumns.map((column) => (
              <th
                key={column.id}
                ref={(el) => {
                  headerRefs.current[column.id] = el;
                }}
                className={`px-4 py-3 text-left text-sm font-medium text-gray-500 select-none sticky top-0 bg-gray-100 ${
                  column.sortable ? "cursor-pointer" : ""
                } ${dragOverColumn === column.id ? "bg-blue-100" : ""}`}
                onClick={() => column.sortable && toggleSort(column.id)}
                draggable={true}
                onDragStart={() => handleDragStart(column.id)}
                onDragOver={(e) => handleDragOver(e, column.id)}
                onDrop={() => handleDrop(column.id)}
                onDragEnd={handleDragEnd}
              >
                <div className="flex items-center gap-1">
                  {column.header}
                  {column.sortable && (
                    <div className="flex items-center">
                      {sortState.column === column.id ? (
                        sortState.direction === "asc" ? (
                          <ArrowUp className="h-4 w-4" />
                        ) : (
                          <ArrowDown className="h-4 w-4" />
                        )
                      ) : (
                        <ArrowUpDown className="h-4 w-4 opacity-50" />
                      )}
                    </div>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {renderRow ? (
            // Use custom row rendering if provided
            sortedData.map((row, index) => renderRow({ row, index, columns: orderedColumns }))
          ) : // Default row rendering
          sortedData.length > 0 ? (
            sortedData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`hover:bg-gray-50 ${rowClickHandler ? "cursor-pointer" : ""}`}
                onClick={() => rowClickHandler && rowClickHandler(row)}
              >
                {orderedColumns.map((column) => (
                  <td key={column.id} className="px-4 py-3 text-sm text-black">
                    {column.cell(row)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-center text-gray-500">
                Keine Daten vorhanden
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

