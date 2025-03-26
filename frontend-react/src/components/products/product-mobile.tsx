"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Edit, Trash } from "lucide-react"
import { Product } from "../types/product"
import { StatusBadge } from "@/components/ui"

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
        <p className="text-sm text-slate-500 dark:text-slate-400">No products found</p>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
          Try adjusting your search criteria
        </p>
      </div>
    )
  }

  return (
    <div className="md:hidden space-y-4">
      {products.map((product) => (
        <div
          key={product.id}
          className={`p-4 rounded-lg border border-slate-200 dark:border-slate-800 ${
            selectedProducts.includes(product.id) 
              ? "bg-slate-50 dark:bg-slate-800/50" 
              : "bg-white dark:bg-slate-900"
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
                <p className="font-medium text-slate-900 dark:text-slate-100">{product.name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">SKU: {product.sku}</p>
              </div>
            </div>
            <div className="flex space-x-1">
              <Button 
                variant="ghost" 
                size="icon" 
                className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                onClick={(e) => {
                  e.stopPropagation()
                  handleEditClick(product)
                }}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                className="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300"
                onClick={(e) => {
                  e.stopPropagation()
                  handleDeleteClick(product)
                }}
              >
                <Trash className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            <StatusBadge status={product.is_active ? "active" : "inactive"}>
              {product.is_active ? "Active" : "Inactive"}
            </StatusBadge>
            {product.is_new && (
              <StatusBadge status="info" className="bg-purple-500">
                New
              </StatusBadge>
            )}
            {product.is_discontinued && (
              <StatusBadge status="warning">
                Discontinued
              </StatusBadge>
            )}
            {product.category && (
              <StatusBadge status="default">
                {product.category}
              </StatusBadge>
            )}
          </div>
        </div>
      ))}
    </div>
  )
} 