"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"

interface PicklistSearchProps {
  searchQuery: string
  setSearchQuery: (query: string) => void
}

export function PicklistSearch({ searchQuery, setSearchQuery }: PicklistSearchProps) {
  return (
    <div className="relative w-full md:w-[300px]">
      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input
        type="search"
        placeholder="Suche nach Auftrag, Kunde..."
        className="pl-8"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
    </div>
  )
}

