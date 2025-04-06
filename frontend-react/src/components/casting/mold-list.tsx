"use client"

import { Button } from "@/components/ui/button"
import { Hash, Trash2 } from "lucide-react"
import Image from "next/image"
import type { Mold } from "@/types/casting/mold"

interface MoldListProps {
  molds: Mold[]
  onRemoveMold: (moldId: string) => void
}

export default function MoldList({ molds, onRemoveMold }: MoldListProps) {
  if (molds.length === 0) {
    return (
      <div className="text-center py-8 bg-muted/20 rounded-lg border border-dashed">
        <div className="text-muted-foreground">Keine Formen hinzugefügt</div>
        <div className="text-sm text-muted-foreground mt-1">
          Fügen Sie mindestens eine Form hinzu, um den Gießprozess zu starten.
        </div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {molds.map((mold) => {
        // Display the first article as representative
        const representativeArticle = mold.articles[0]
        
        return (
          <div key={mold.id} className="bg-white rounded-lg border shadow-sm overflow-hidden">
            <div className="p-3 border-b bg-muted/20 flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Hash className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Form: {mold.number}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onRemoveMold(mold.id)}
                className="h-8 w-8 p-0 text-destructive hover:text-destructive/90 hover:bg-destructive/10"
              >
                <Trash2 className="h-4 w-4" />
                <span className="sr-only">Entfernen</span>
              </Button>
            </div>
            
            <div className="p-3">
              <div className="flex items-center">
                <div className="relative w-12 h-12 mr-3 bg-muted/10 rounded overflow-hidden">
                  <Image
                    src={representativeArticle.imageUrl || "/placeholder.svg"}
                    alt={representativeArticle.name}
                    fill
                    className="object-contain"
                  />
                </div>
                <div>
                  <div className="font-medium line-clamp-1">{representativeArticle.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {mold.articles.length > 1 
                      ? `${mold.articles.length} Artikel in dieser Form`
                      : "1 Artikel in dieser Form"
                    }
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
} 