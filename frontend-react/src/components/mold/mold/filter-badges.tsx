"use client"

import type React from "react"

import { Badge } from "@/components/ui/badge"
import { X, TagIcon } from "lucide-react"
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die FilterBadges Komponente
 */
interface FilterBadgesProps {
  filters: {
    technology: string[]
    alloy: string[]
    tags: string[]
    isActive: boolean | null | "mixed"
    moldSize: string[]
  }
  setFilters: React.Dispatch<
    React.SetStateAction<{
      technology: string[]
      alloy: string[]
      tags: string[]
      isActive: boolean | null | "mixed"
      moldSize: string[]
    }>
  >
}

/**
 * Komponente zur Anzeige der aktiven Filter als Badges
 */
export function FilterBadges({ filters, setFilters }: FilterBadgesProps) {
  // Zählt die aktiven Filter
  const getActiveFilterCount = () => {
    let count = 0
    if (filters.technology.length > 0) count++
    if (filters.alloy.length > 0) count++
    if (filters.tags.length > 0) count++
    if (filters.isActive !== null) count++
    if (filters.moldSize.length > 0) count++
    return count
  }

   const { t } = useAppTranslation("mold");

  if (getActiveFilterCount() === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2">
      {filters.technology.map((tech) => (
        <Badge key={`tech-${tech}`} variant="secondary" className="flex items-center gap-1">
          {tech}
          <X
            className="h-3 w-3 ml-1 cursor-pointer"
            onClick={() =>
              setFilters({
                ...filters,
                technology: filters.technology.filter((t) => t !== tech),
              })
            }
          />
        </Badge>
      ))}
      {filters.alloy.map((alloy) => (
        <Badge key={`alloy-${alloy}`} variant="secondary" className="flex items-center gap-1">
          {alloy}
          <X
            className="h-3 w-3 ml-1 cursor-pointer"
            onClick={() =>
              setFilters({
                ...filters,
                alloy: filters.alloy.filter((a) => a !== alloy),
              })
            }
          />
        </Badge>
      ))}
      {filters.moldSize.map((size) => (
        <Badge key={`size-${size}`} variant="secondary" className="flex items-center gap-1">
          {size}
          <X
            className="h-3 w-3 ml-1 cursor-pointer"
            onClick={() =>
              setFilters({
                ...filters,
                moldSize: filters.moldSize.filter((s) => s !== size),
              })
            }
          />
        </Badge>
      ))}
      {filters.tags.map((tag) => (
        <Badge key={`tag-${tag}`} variant="secondary" className="flex items-center gap-1">
          <TagIcon className="h-3 w-3" />
          {tag}
          <X
            className="h-3 w-3 ml-1 cursor-pointer"
            onClick={() =>
              setFilters({
                ...filters,
                tags: filters.tags.filter((t) => t !== tag),
              })
            }
          />
        </Badge>
      ))}
      {filters.isActive !== null && (
        <Badge variant="secondary" className="flex items-center gap-1">
          {filters.isActive === true ? "Active" : filters.isActive === false ? "Inactive" : "Mixed"}
          <X
            className="h-3 w-3 ml-1 cursor-pointer"
            onClick={() =>
              setFilters({
                ...filters,
                isActive: null,
              })
            }
          />
        </Badge>
      )}
    </div>
  )
}

