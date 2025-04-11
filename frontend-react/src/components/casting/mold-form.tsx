"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { Article, Mold } from "@/types/casting/mold"
import { v4 as uuidv4 } from "uuid"
import { Plus, Trash2 } from "lucide-react"
import Image from "next/image"

interface MoldFormProps {
  onSubmit: (mold: Mold) => void
  onCancel: () => void
}

// Mock articles for demo purposes
const mockArticles: Article[] = [
  {
    id: "art1",
    number: "A1001",
    name: "Zinnfigur Ritter",
    imageUrl: "/placeholder.svg",
  },
  {
    id: "art2",
    number: "A1002",
    name: "Zinnfigur Drache",
    imageUrl: "/placeholder.svg",
  },
  {
    id: "art3",
    number: "A1003",
    name: "Zinnfigur Burg",
    imageUrl: "/placeholder.svg",
  },
]

export default function MoldForm({ onSubmit, onCancel }: MoldFormProps) {
  const [moldNumber, setMoldNumber] = useState("")
  const [articles, setArticles] = useState<Article[]>([])
  
  const handleSelectArticle = (article: Article) => {
    // Check if article is already in the list
    if (!articles.some((a) => a.id === article.id)) {
      setArticles((prev) => [...prev, article])
    }
  }
  
  const handleRemoveArticle = (articleId: string) => {
    setArticles((prev) => prev.filter((a) => a.id !== articleId))
  }
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!moldNumber || articles.length === 0) return
    
    const newMold: Mold = {
      id: uuidv4(),
      number: moldNumber,
      articles: articles,
      castCount: 0,
    }
    
    onSubmit(newMold)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="mold-number">Formnummer</Label>
        <Input
          id="mold-number"
          value={moldNumber}
          onChange={(e) => setMoldNumber(e.target.value)}
          placeholder="z.B. F2001"
          required
        />
      </div>
      
      <div className="border rounded-md p-4">
        <Label className="mb-2 block">Artikel in dieser Form</Label>
        
        {articles.length > 0 ? (
          <div className="space-y-2 mb-4">
            {articles.map((article) => (
              <div key={article.id} className="flex items-center justify-between bg-muted/20 p-2 rounded">
                <div className="flex items-center">
                  <div className="relative w-10 h-10 mr-2 bg-white rounded overflow-hidden">
                    <Image
                      src={article.imageUrl || "/placeholder.svg"}
                      alt={article.name}
                      fill
                      className="object-contain"
                    />
                  </div>
                  <div>
                    <div className="font-medium text-sm">{article.name}</div>
                    <div className="text-xs text-muted-foreground">{article.number}</div>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveArticle(article.id)}
                  className="text-destructive hover:text-destructive/90 hover:bg-destructive/10"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-muted-foreground text-sm mb-4">
            Keine Artikel ausgewählt
          </div>
        )}
        
        <div className="space-y-2">
          <Label className="mb-1 block text-sm">Artikel hinzufügen:</Label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {mockArticles.map((article) => (
              <Button
                key={article.id}
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleSelectArticle(article)}
                disabled={articles.some((a) => a.id === article.id)}
                className="flex justify-start"
              >
                <Plus className="h-4 w-4 mr-2 flex-shrink-0" />
                <div className="text-left overflow-hidden text-ellipsis whitespace-nowrap">
                  {article.number}: {article.name}
                </div>
              </Button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
        <Button 
          type="submit" 
          disabled={!moldNumber || articles.length === 0}
        >
          Form hinzufügen
        </Button>
      </div>
    </form>
  )
} 