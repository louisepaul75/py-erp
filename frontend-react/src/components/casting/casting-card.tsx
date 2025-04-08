"use client"

import { Button } from "@/components/ui/button"
import { Plus, Hash } from "lucide-react"
import Image from "next/image"
import type { Mold } from "@/types/casting/mold"

interface CastingCardProps {
  mold: Mold
  castCount: number
  onIncrementCast: () => void
  disabled?: boolean
}

export default function CastingCard({ mold, castCount, onIncrementCast, disabled = false }: CastingCardProps) {
  // Find the selected article or default to the first one
  const selectedArticle = mold.articles.find((a) => a.id === mold.selectedArticleId) || mold.articles[0]

  return (
    <div className="bg-white rounded-lg border shadow-sm h-full flex flex-col overflow-hidden">
      <div className="p-4 border-b bg-muted/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Hash className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">Form: {mold.number}</span>
          </div>
          <div className="text-sm font-medium">
            Abgüsse: {castCount}
          </div>
        </div>
      </div>

      <div className="relative h-48 bg-muted/10 flex items-center justify-center overflow-hidden">
        <Image
          src={selectedArticle.imageUrl || "/placeholder.svg"}
          alt={selectedArticle.name}
          fill
          className="object-contain p-4"
        />
      </div>

      <div className="p-4 flex-grow">
        <div className="font-medium mb-1">{selectedArticle.name}</div>
        <div className="text-sm text-muted-foreground">Artikelnr.: {selectedArticle.number}</div>
      </div>

      <div className="p-4 pt-0">
        <Button 
          onClick={onIncrementCast} 
          disabled={disabled}
          className="w-full"
        >
          <Plus className="mr-2 h-4 w-4" />
          Abguss hinzufügen
        </Button>
      </div>
    </div>
  )
} 