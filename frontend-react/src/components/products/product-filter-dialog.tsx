"use client"
import { X, Filter } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { useState } from "react"

interface ProductFilterDialogProps {
  isOpen: boolean
  onClose: () => void
  onApplyFilters: (filters: ProductFilters) => void
  initialFilters: ProductFilters
}

export interface ProductFilters {
  isActive: boolean | null;
  hasVariants: boolean | null;
  productType: string;
}

const PRODUCT_TYPES = [
  { value: "all", label: "All Types" },
  { value: "physical", label: "Physical" },
  { value: "digital", label: "Digital" },
  { value: "service", label: "Service" },
]

export default function ProductFilterDialog({ 
  isOpen, 
  onClose, 
  onApplyFilters,
  initialFilters 
}: ProductFilterDialogProps) {
  const [filters, setFilters] = useState<ProductFilters>(initialFilters)

  const handleApplyFilters = () => {
    onApplyFilters(filters)
    onClose()
  }

  const handleResetFilters = () => {
    const resetFilters = {
      isActive: null,
      hasVariants: null,
      productType: "all",
    }
    setFilters(resetFilters)
    onApplyFilters(resetFilters)
    onClose()
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Description asChild>
          <div className="sr-only" id="product-filter-dialog-description">
            Dialog to filter products by various criteria such as active status, variants, and product type.
          </div>
        </Dialog.Description>
        <Dialog.Content 
          className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none overflow-hidden"
          aria-describedby="product-filter-dialog-description"
        >
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2 text-popover-foreground">
              <Filter className="h-5 w-5" />
              Filter Products
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4 text-popover-foreground" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-6 overflow-y-auto" style={{ maxHeight: "calc(85vh - 60px)" }}>
            <div className="space-y-6">
              {/* Product Type Filter */}
              <div className="space-y-2">
                <Label htmlFor="productType" className="text-sm font-medium">
                  Product Type
                </Label>
                <Select
                  value={filters.productType}
                  onValueChange={(value) => setFilters({...filters, productType: value})}
                >
                  <SelectTrigger id="productType">
                    <SelectValue placeholder="Select product type" />
                  </SelectTrigger>
                  <SelectContent>
                    {PRODUCT_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Active Status Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">
                  Active Status
                </Label>
                <div className="flex flex-col space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="activeOnly" 
                      checked={filters.isActive === true}
                      onCheckedChange={(checked) => 
                        setFilters({...filters, isActive: checked ? true : null})
                      }
                    />
                    <Label htmlFor="activeOnly" className="text-sm">
                      Active Only
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="inactiveOnly" 
                      checked={filters.isActive === false}
                      onCheckedChange={(checked) => 
                        setFilters({...filters, isActive: checked ? false : null})
                      }
                    />
                    <Label htmlFor="inactiveOnly" className="text-sm">
                      Inactive Only
                    </Label>
                  </div>
                </div>
              </div>

              {/* Has Variants Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="hasVariants" 
                  checked={filters.hasVariants === true}
                  onCheckedChange={(checked) => 
                    setFilters({...filters, hasVariants: checked ? true : null})
                  }
                />
                <Label htmlFor="hasVariants" className="text-sm font-medium">
                  Has Variants
                </Label>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 p-4 border-t">
            <Button variant="outline" onClick={handleResetFilters}>
              Reset
            </Button>
            <Button onClick={handleApplyFilters}>
              Apply Filters
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
