"use client"

import { ChevronDown, ChevronUp, Edit, Trash } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"
import { Product } from "../types/product"

interface ProductTableProps {
  products: Product[]
  selectedProducts: number[]
  handleSelectProduct: (id: number, checked: boolean) => void
  handleRowClick: (product: Product) => void
  handleEditClick: (product: Product) => void
  handleDeleteClick: (product: Product) => void
  isLoading: boolean
}

export default function ProductTable({
  products,
  selectedProducts,
  handleSelectProduct,
  handleRowClick,
  handleEditClick,
  handleDeleteClick,
  isLoading,
}: ProductTableProps) {
  const [sortField, setSortField] = useState<keyof Product>("id")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")

  const handleSort = (field: keyof Product) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortOrder("asc")
    }
  }

  const sortedProducts = [...products].sort((a, b) => {
    const aValue = a[sortField]
    const bValue = b[sortField]

    if (aValue === null || aValue === undefined) return sortOrder === "asc" ? -1 : 1
    if (bValue === null || bValue === undefined) return sortOrder === "asc" ? 1 : -1

    if (typeof aValue === "string" && typeof bValue === "string") {
      return sortOrder === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
    } else {
      return sortOrder === "asc" ? (aValue < bValue ? -1 : 1) : aValue > bValue ? -1 : 1
    }
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
        <span className="ml-3">Lade Produkte...</span>
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 p-4 text-center">
        <p className="text-sm text-slate-500 dark:text-slate-400">Keine Produkte gefunden</p>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
          Versuchen Sie, Ihre Suchkriterien zu ändern
        </p>
      </div>
    )
  }

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-slate-100 dark:bg-slate-800 text-left">
            <th className="p-2">
              <Checkbox
                checked={products.length > 0 && selectedProducts.length === products.length}
                onCheckedChange={(checked) => {
                  if (checked) {
                    const allIds = products.map((product) => product.id)
                    handleSelectProduct(0, true) // Dummy call to select all
                  } else {
                    handleSelectProduct(0, false) // Dummy call to deselect all
                  }
                }}
              />
            </th>
            <th
              className="p-2 cursor-pointer"
              onClick={() => handleSort("sku")}
            >
              <div className="flex items-center">
                SKU
                {sortField === "sku" && (
                  <span className="ml-1">
                    {sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </span>
                )}
              </div>
            </th>
            <th
              className="p-2 cursor-pointer"
              onClick={() => handleSort("name")}
            >
              <div className="flex items-center">
                Name
                {sortField === "name" && (
                  <span className="ml-1">
                    {sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </span>
                )}
              </div>
            </th>
            <th
              className="p-2 cursor-pointer"
              onClick={() => handleSort("is_active")}
            >
              <div className="flex items-center">
                Status
                {sortField === "is_active" && (
                  <span className="ml-1">
                    {sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </span>
                )}
              </div>
            </th>
            <th
              className="p-2 cursor-pointer"
              onClick={() => handleSort("category")}
            >
              <div className="flex items-center">
                Kategorie
                {sortField === "category" && (
                  <span className="ml-1">
                    {sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </span>
                )}
              </div>
            </th>
            <th className="p-2">Aktionen</th>
          </tr>
        </thead>
        <tbody>
          {sortedProducts.map((product) => (
            <tr
              key={product.id}
              className={`border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 ${
                selectedProducts.includes(product.id) ? "bg-blue-50 dark:bg-blue-900/20" : ""
              }`}
              onClick={() => handleRowClick(product)}
            >
              <td className="p-2" onClick={(e) => e.stopPropagation()}>
                <Checkbox
                  checked={selectedProducts.includes(product.id)}
                  onCheckedChange={(checked) => handleSelectProduct(product.id, !!checked)}
                />
              </td>
              <td className="p-2">{product.sku}</td>
              <td className="p-2">{product.name}</td>
              <td className="p-2">
                <Badge
                  variant={product.is_active ? "success" : "destructive"}
                  className="text-xs"
                >
                  {product.is_active ? "Aktiv" : "Inaktiv"}
                </Badge>
                {product.is_new && (
                  <Badge
                    variant="default"
                    className="text-xs ml-1 bg-purple-500"
                  >
                    Neu
                  </Badge>
                )}
                {product.is_discontinued && (
                  <Badge
                    variant="outline"
                    className="text-xs ml-1"
                  >
                    Eingestellt
                  </Badge>
                )}
              </td>
              <td className="p-2">{product.category || "—"}</td>
              <td className="p-2" onClick={(e) => e.stopPropagation()}>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEditClick(product)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => handleDeleteClick(product)}
                  >
                    <Trash className="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
} 