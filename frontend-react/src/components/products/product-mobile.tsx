"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit, Trash } from "lucide-react"
import { Product } from "../types/product"

interface ProductMobileProps {
  products: Product[]
  selectedProducts: number[]
  handleSelectProduct: (id: number, checked: boolean) => void
  handleRowClick: (product: Product) => void
  handleEditClick: (product: Product) => void
  handleDeleteClick: (product: Product) => void
}

export default function ProductMobile({
  products,
  selectedProducts,
  handleSelectProduct,
  handleRowClick,
  handleEditClick,
  handleDeleteClick,
}: ProductMobileProps) {
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
    <div className="md:hidden space-y-4">
      {products.map((product) => (
        <div
          key={product.id}
          className={`p-4 border rounded-lg shadow-sm ${
            selectedProducts.includes(product.id) ? "bg-blue-50 dark:bg-blue-900/20 border-blue-500" : "bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700"
          }`}
          onClick={() => handleRowClick(product)}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <Checkbox
                checked={selectedProducts.includes(product.id)}
                onCheckedChange={(checked) => {
                  handleSelectProduct(product.id, !!checked)
                  // Prevent the row click event
                  event?.stopPropagation()
                }}
              />
              <div>
                <p className="font-semibold">{product.name}</p>
                <p className="text-sm text-gray-500">SKU: {product.sku}</p>
              </div>
            </div>
            <div className="flex space-x-1">
              <Button variant="ghost" size="icon" onClick={(e) => {
                e.stopPropagation()
                handleEditClick(product)
              }}>
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="text-red-500" onClick={(e) => {
                e.stopPropagation()
                handleDeleteClick(product)
              }}>
                <Trash className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            <Badge
              variant={product.is_active ? "success" : "destructive"}
              className="text-xs"
            >
              {product.is_active ? "Aktiv" : "Inaktiv"}
            </Badge>
            {product.is_new && (
              <Badge
                variant="default"
                className="text-xs bg-purple-500"
              >
                Neu
              </Badge>
            )}
            {product.is_discontinued && (
              <Badge
                variant="outline"
                className="text-xs"
              >
                Eingestellt
              </Badge>
            )}
            {product.category && (
              <Badge variant="secondary" className="text-xs">
                {product.category}
              </Badge>
            )}
          </div>
        </div>
      ))}
    </div>
  )
} 