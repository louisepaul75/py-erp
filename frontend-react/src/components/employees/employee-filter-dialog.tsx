"use client"
import { X, Filter } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { useState } from "react"

interface EmployeeFilterDialogProps {
  isOpen: boolean
  onClose: () => void
  onApplyFilters: (filters: EmployeeFilters) => void
  initialFilters: EmployeeFilters
}

export interface EmployeeFilters {
  isActive: boolean | null;
  isTerminated: boolean | null;
  employmentStatus: string;
}

const EMPLOYMENT_STATUS = [
  { value: "all", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "terminated", label: "Terminated" },
  { value: "present", label: "Present" },
]

export default function EmployeeFilterDialog({ 
  isOpen, 
  onClose, 
  onApplyFilters,
  initialFilters 
}: EmployeeFilterDialogProps) {
  const [filters, setFilters] = useState<EmployeeFilters>(initialFilters)

  const handleApplyFilters = () => {
    onApplyFilters(filters)
    onClose()
  }

  const handleResetFilters = () => {
    const resetFilters = {
      isActive: null,
      isTerminated: null,
      employmentStatus: "all",
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
          <div className="sr-only" id="employee-filter-dialog-description">
            Dialog to filter employees by various criteria such as active status, termination status, and employment status.
          </div>
        </Dialog.Description>
        <Dialog.Content 
          className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none overflow-hidden"
          aria-describedby="employee-filter-dialog-description"
        >
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2 text-popover-foreground">
              <Filter className="h-5 w-5" />
              Filter Employees
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4 text-popover-foreground" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-6 overflow-y-auto" style={{ maxHeight: "calc(85vh - 60px)" }}>
            <div className="space-y-6">
              {/* Employment Status Filter */}
              <div className="space-y-2">
                <Label htmlFor="employmentStatus" className="text-sm font-medium">
                  Employment Status
                </Label>
                <Select
                  value={filters.employmentStatus}
                  onValueChange={(value) => setFilters({...filters, employmentStatus: value})}
                >
                  <SelectTrigger id="employmentStatus">
                    <SelectValue placeholder="Select employment status" />
                  </SelectTrigger>
                  <SelectContent>
                    {EMPLOYMENT_STATUS.map((status) => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Active Status Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="activeOnly" 
                  checked={filters.isActive === true}
                  onCheckedChange={(checked) => 
                    setFilters({...filters, isActive: checked ? true : null})
                  }
                />
                <Label htmlFor="activeOnly" className="text-sm font-medium">
                  Active Employees Only
                </Label>
              </div>

              {/* Terminated Status Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="terminatedOnly" 
                  checked={filters.isTerminated === true}
                  onCheckedChange={(checked) => 
                    setFilters({...filters, isTerminated: checked ? true : null})
                  }
                />
                <Label htmlFor="terminatedOnly" className="text-sm font-medium">
                  Terminated Employees Only
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
