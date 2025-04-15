"use client"
import { X, Filter } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { useState } from "react"

interface CustomerFilterDialogProps {
  isOpen: boolean
  onClose: () => void
  onApplyFilters: (filters: CustomerFilters) => void
  initialFilters: CustomerFilters
}

export interface CustomerFilters {
  hasOrders: boolean
  customerType: string
  customerGroup: string
}

const CUSTOMER_TYPES = [
  { value: "all", label: "All Types" },
  { value: "individual", label: "Individual" },
  { value: "company", label: "Company" },
]

const CUSTOMER_GROUPS = [
  { value: "all", label: "All Groups" },
  { value: "regular", label: "Regular" },
  { value: "vip", label: "VIP" },
  { value: "wholesale", label: "Wholesale" },
]

export default function CustomerFilterDialog({ 
  isOpen, 
  onClose, 
  onApplyFilters,
  initialFilters 
}: CustomerFilterDialogProps) {
  const [filters, setFilters] = useState<CustomerFilters>(initialFilters)

  const handleApplyFilters = () => {
    onApplyFilters(filters)
    onClose()
  }

  const handleResetFilters = () => {
    const resetFilters = {
      hasOrders: false,
      customerType: "all",
      customerGroup: "all",
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
          <div className="sr-only" id="customer-filter-dialog-description">
            Dialog to filter customers by various criteria such as customer type, group, and order status.
          </div>
        </Dialog.Description>
        <Dialog.Content 
          className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none overflow-hidden"
          aria-describedby="customer-filter-dialog-description"
        >
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2 text-popover-foreground">
              <Filter className="h-5 w-5" />
              Filter Customers
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4 text-popover-foreground" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-6 overflow-y-auto" style={{ maxHeight: "calc(85vh - 60px)" }}>
            <div className="space-y-6">
              {/* Customer Type Filter */}
              <div className="space-y-2">
                <Label htmlFor="customerType" className="text-sm font-medium">
                  Customer Type
                </Label>
                <Select
                  value={filters.customerType}
                  onValueChange={(value) => setFilters({...filters, customerType: value})}
                >
                  <SelectTrigger id="customerType">
                    <SelectValue placeholder="Select customer type" />
                  </SelectTrigger>
                  <SelectContent>
                    {CUSTOMER_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Customer Group Filter */}
              <div className="space-y-2">
                <Label htmlFor="customerGroup" className="text-sm font-medium">
                  Customer Group
                </Label>
                <Select
                  value={filters.customerGroup}
                  onValueChange={(value) => setFilters({...filters, customerGroup: value})}
                >
                  <SelectTrigger id="customerGroup">
                    <SelectValue placeholder="Select customer group" />
                  </SelectTrigger>
                  <SelectContent>
                    {CUSTOMER_GROUPS.map((group) => (
                      <SelectItem key={group.value} value={group.value}>
                        {group.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Has Orders Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="hasOrders" 
                  checked={filters.hasOrders}
                  onCheckedChange={(checked) => 
                    setFilters({...filters, hasOrders: checked === true})
                  }
                />
                <Label htmlFor="hasOrders" className="text-sm font-medium">
                  Has Orders
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
