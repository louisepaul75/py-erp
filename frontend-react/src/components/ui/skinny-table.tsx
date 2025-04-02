"use client"

import { useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { cn } from "@/lib/utils"
import React from "react"

export interface SkinnyTableColumn<T> {
  field: keyof T
  header: string
  render?: (item: T) => React.ReactNode
}

export interface SkinnyTableProps<T> {
  data: T[]
  columns: SkinnyTableColumn<T>[]
  selectedItem?: T[keyof T]
  onItemSelect?: (item: T) => void
  isLoading?: boolean
  noDataMessage?: string
  className?: string
}

export function SkinnyTable<T extends { [key: string]: any }>({
  data,
  columns,
  selectedItem,
  onItemSelect,
  isLoading = false,
  noDataMessage = "No data found",
  className,
}: SkinnyTableProps<T>) {
  const [sortField, setSortField] = useState<keyof T>(columns[0]?.field || "id")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")

  const handleSort = (field: keyof T) => {
    setSortField(field)
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))
  }

  const sortedData = React.useMemo(() => {
    // Ensure data is an array before sorting
    const dataToSort = Array.isArray(data) ? data : []; 
    return [...dataToSort].sort((a, b) => {
      const aValue = a[sortField] ?? "";
      const bValue = b[sortField] ?? "";

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [data, sortField, sortOrder]);

  return (
    <Table className={className}>
      <TableHeader>
        <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50">
          {columns.map((column) => (
            <TableHead
              key={String(column.field)}
              className="font-medium cursor-pointer text-slate-700 dark:text-slate-300"
              onClick={() => handleSort(column.field)}
            >
              <div className="flex items-center gap-2">
                {column.header}
                {sortField === column.field && (
                  <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                )}
              </div>
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>

      <TableBody className="min-h-[500px]">
        {isLoading ? (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-center py-8">
              <div className="flex justify-center items-center gap-2 min-h-[500px]">
                <span className="text-slate-600 dark:text-slate-400">Loading...</span>
              </div>
            </TableCell>
          </TableRow>
        ) : sortedData.length > 0 ? (
          sortedData.map((item) => (
            <TableRow
              key={String(item[columns[0].field])}
              onClick={() => onItemSelect?.(item)}
              className={cn(
                "cursor-pointer transition-colors",
                selectedItem === item[columns[0].field]
                  ? "bg-blue-50 dark:bg-blue-900/20 text-slate-900 dark:text-slate-100"
                  : "hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-800 dark:text-slate-300"
              )}
            >
              {columns.map((column) => (
                <TableCell
                  key={String(column.field)}
                  className={selectedItem === item[columns[0].field] ? "font-medium" : ""}
                >
                  {column.render ? column.render(item) : 
                    (column.field === "legacy_base_sku" && (!item[column.field] || item[column.field] === "") 
                      ? "—" 
                      : (item[column.field] || ""))}
                </TableCell>
              ))}
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-center py-8">
              <div className="flex justify-center items-center gap-2 min-h-[500px]">
                <span className="text-slate-600 dark:text-slate-400">{noDataMessage}</span>
              </div>
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
} 