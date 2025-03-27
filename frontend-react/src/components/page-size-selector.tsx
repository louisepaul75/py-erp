"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface PageSizeSelectorProps {
  pageSize: number
  setPageSize: (size: number) => void
  totalItems: number
}

export function PageSizeSelector({ pageSize, setPageSize, totalItems }: PageSizeSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground whitespace-nowrap">Zeige</span>
      <Select
        value={pageSize === 0 ? "all" : pageSize.toString()}
        onValueChange={(value) => setPageSize(value === "all" ? 0 : Number.parseInt(value))}
      >
        <SelectTrigger className="w-[100px]">
          <SelectValue placeholder="100" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="100">100</SelectItem>
          <SelectItem value="250">250</SelectItem>
          <SelectItem value="500">500</SelectItem>
          <SelectItem value="all">Alle ({totalItems})</SelectItem>
        </SelectContent>
      </Select>
      <span className="text-sm text-muted-foreground whitespace-nowrap">Einträge</span>
    </div>
  )
}

