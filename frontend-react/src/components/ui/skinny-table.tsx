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

  // Add debug logging for data processing
  React.useEffect(() => {
    // First, log the data we received
    console.log("SkinnyTable received data:", data);
    
    // Check if there's any product with sku 415220
    if (Array.isArray(data)) {
      const testProduct = data.find(item => item.sku === "415220");
      if (testProduct) {
        console.log("SkinnyTable found product 415220:", testProduct);
        console.log("legacy_base_sku value in SkinnyTable:", testProduct.legacy_base_sku);
        console.log("Type of legacy_base_sku in SkinnyTable:", typeof testProduct.legacy_base_sku);
      }
    }
  }, [data]);

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

  // Process data to ensure all legacy_base_sku values are properly handled
  React.useEffect(() => {
    if (Array.isArray(data)) {
      // Process each item to ensure legacy_base_sku is a string if present
      data.forEach(item => {
        if (item.legacy_base_sku !== undefined && item.legacy_base_sku !== null) {
          // Convert to string if it's not already
          if (typeof item.legacy_base_sku !== 'string') {
            console.log(`Converting legacy_base_sku for ${item.sku} from ${typeof item.legacy_base_sku} to string`);
            item.legacy_base_sku = String(item.legacy_base_sku);
          }
        }
      });
    }
  }, [data]);

  return (
    <Table className={cn("h-full", className)}>
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

      <TableBody className="relative h-full">
        {isLoading ? (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-center py-8">
              <div className="flex justify-center items-center gap-2 h-full">
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
              {columns.map((column) => {
                // Debug for legacy_base_sku column
                if (column.field === 'legacy_base_sku' && item.sku === '415220') {
                  console.log(`Rendering legacy_base_sku for SKU 415220:`, {
                    value: item[column.field],
                    type: typeof item[column.field],
                    isEmpty: !item[column.field] || item[column.field] === "",
                    cellContent: column.render 
                      ? column.render(item) 
                      : (column.field === "legacy_base_sku" && (!item[column.field] || item[column.field] === "") 
                        ? "—" 
                        : (item[column.field] || ""))
                  });
                }
                
                // For legacy_base_sku column, check if value exists and is not empty string
                const isLegacySku = column.field === "legacy_base_sku";
                const cellValue = item[column.field];
                const isEmpty = cellValue === null || cellValue === undefined || cellValue === "";

                return (
                  <TableCell
                    key={String(column.field)}
                    className={selectedItem === item[columns[0].field] ? "font-medium" : ""}
                  >
                    {column.render 
                      ? column.render(item) 
                      : (isLegacySku && isEmpty)
                        ? "—" 
                        : (cellValue !== undefined && cellValue !== null) 
                          ? String(cellValue) 
                          : ""}
                  </TableCell>
                );
              })}
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-center py-8">
              <div className="flex justify-center items-center gap-2 h-full">
                <span className="text-slate-600 dark:text-slate-400">{noDataMessage}</span>
              </div>
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
} 