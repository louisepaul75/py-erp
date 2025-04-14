import React from "react";
"use client"

import { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent } from "@/components/ui/popover"
import { Search } from "lucide-react"
import { cn } from "@/lib/utils"

// Artikel-Typ
export interface Article {
  id: string
  currentArticleNumber: string
  oldArticleNumber?: string
  name: string
  description?: string
  price: number
  unit?: string
  inStock?: number
  category?: string
}

// Mock-Artikel für die Demo
const mockArticles: Article[] = [
  {
    id: "1",
    currentArticleNumber: "A1001",
    oldArticleNumber: "10-001",
    name: "Premium Bürostuhl",
    price: 299.99,
    inStock: 15,
    category: "Büromöbel",
  },
  {
    id: "2",
    currentArticleNumber: "A1002",
    oldArticleNumber: "10-002",
    name: "Schreibtisch Executive",
    price: 599.99,
    inStock: 8,
    category: "Büromöbel",
  },
  {
    id: "3",
    currentArticleNumber: "A1003",
    name: "Monitorständer",
    price: 59.99,
    inStock: 25,
    category: "Bürozubehör",
  },
  {
    id: "4",
    currentArticleNumber: "A2001",
    oldArticleNumber: "20-001",
    name: "Wireless Tastatur",
    price: 49.99,
    inStock: 30,
    category: "Hardware",
  },
  {
    id: "5",
    currentArticleNumber: "A2002",
    name: "Wireless Maus",
    price: 39.99,
    inStock: 35,
    category: "Hardware",
  },
  {
    id: "6",
    currentArticleNumber: "A3001",
    name: "Monitorkabel HDMI",
    price: 12.99,
    inStock: 50,
    category: "Kabel",
  },
  {
    id: "7",
    currentArticleNumber: "A3002",
    name: "USB-Hub 4-Port",
    price: 29.99,
    inStock: 18,
    category: "Hardware",
  },
  {
    id: "8",
    currentArticleNumber: "A4001",
    name: "Höhenverstellbarer Schreibtisch",
    price: 399.99,
    inStock: 5,
    category: "Büromöbel",
  },
  {
    id: "9",
    currentArticleNumber: "A5001",
    name: "Dokumentenablage",
    price: 14.99,
    inStock: 40,
    category: "Bürozubehör",
  },
  {
    id: "10",
    currentArticleNumber: "A6001",
    name: "Laptop Computer",
    price: 1299.99,
    inStock: 12,
    category: "Hardware",
  },
]

interface ArticleSearchProps {
  value: string
  onValueChange: (value: string) => void
  onArticleSelect: (article: Article) => void
  onTabNavigation?: () => void
  disabled?: boolean
  className?: string
  placeholder?: string
  inputRef?: React.RefObject<HTMLInputElement>
  autoOpenOnInput?: boolean // Neue Prop hinzufügen
}

export function ArticleSearch({
  value,
  onValueChange,
  onArticleSelect,
  onTabNavigation,
  disabled = false,
  className,
  placeholder = "Artikelnummer",
  inputRef,
  autoOpenOnInput = false, // Standardwert hinzufügen
}: ArticleSearchProps) {
  const [open, setOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredArticles, setFilteredArticles] = useState<Article[]>([])
  const [highlightedIndex, setHighlightedIndex] = useState(0)
  const inputInnerRef = useRef<HTMLInputElement>(null)
  const commandRef = useRef<HTMLDivElement>(null)

  // Kombiniere den externen Ref mit unserem internen Ref
  const combinedRef = inputRef || inputInnerRef

  // Automatisch öffnen, wenn der Wert nicht leer ist
  useEffect(() => {
    if (value && value.length > 0) {
      setOpen(true)
      setSearchTerm(value)
    }
  }, [value])

  // Öffne das Popover automatisch, wenn sich der Wert ändert und autoOpenOnInput aktiviert ist
  useEffect(() => {
    if (autoOpenOnInput && value && value.length > 0 && !open) {
      setOpen(true)
      setSearchTerm(value)
    }
  }, [value, autoOpenOnInput, open])

  // Artikel filtern basierend auf Suchbegriff
  useEffect(() => {
    if (searchTerm) {
      const lowercaseSearch = searchTerm.toLowerCase()
      const filtered = mockArticles.filter(
        (article) =>
          article.currentArticleNumber.toLowerCase().includes(lowercaseSearch) ||
          (article.oldArticleNumber && article.oldArticleNumber.toLowerCase().includes(lowercaseSearch)) ||
          article.name.toLowerCase().includes(lowercaseSearch) ||
          (article.description && article.description.toLowerCase().includes(lowercaseSearch)),
      )
      setFilteredArticles(filtered)
      setHighlightedIndex(0) // Reset highlighted index when search changes
    } else {
      setFilteredArticles(mockArticles)
    }
  }, [searchTerm])

  // Artikel auswählen
  const handleSelect = (article: Article) => {
    onArticleSelect(article)
    onValueChange(article.currentArticleNumber)
    setOpen(false)
    setSearchTerm("")
  }

  // Tastaturnavigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (e.key === "ArrowDown" || e.key === "Enter") {
        e.preventDefault()
        setOpen(true)
        return
      }
    }

    if (open) {
      // Navigiere durch die Liste mit Pfeiltasten
      if (e.key === "ArrowDown") {
        e.preventDefault()
        setHighlightedIndex((prevIndex) => (prevIndex < filteredArticles.length - 1 ? prevIndex + 1 : prevIndex))
      } else if (e.key === "ArrowUp") {
        e.preventDefault()
        setHighlightedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : 0))
      } else if (e.key === "Enter" && filteredArticles.length > 0) {
        e.preventDefault()
        handleSelect(filteredArticles[highlightedIndex])
      } else if (e.key === "Tab") {
        e.preventDefault()
        if (filteredArticles.length > 0) {
          handleSelect(filteredArticles[highlightedIndex])
        }
        onTabNavigation?.()
      } else if (e.key === "Escape") {
        e.preventDefault()
        setOpen(false)
      }
    }
  }

  // Bestandsfarbe basierend auf Menge
  const getStockColor = (stock?: number) => {
    if (!stock) return "text-gray-500"
    if (stock > 20) return "text-green-600"
    if (stock > 5) return "text-orange-500"
    return "text-red-600"
  }

  // Formatieren von Währungsbeträgen
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("de-DE", {
      style: "currency",
      currency: "EUR",
    }).format(amount)
  }

  return (
    <div className={cn("relative", className)}>
      <Popover
        open={open}
        onOpenChange={(newOpen) => {
          // Wenn das Popover geschlossen wird, setzen wir den Fokus zurück auf das Eingabefeld
          if (!newOpen && combinedRef.current) {
            // Kurze Verzögerung, um sicherzustellen, dass das Popover vollständig geschlossen ist
            setTimeout(() => {
              combinedRef.current?.focus()
            }, 10)
          }
          setOpen(newOpen)
        }}
      >
        <div className="flex" onClick={(e) => e.stopPropagation()}>
          <Input
            ref={combinedRef}
            value={value}
            onChange={(e) => {
              const newValue = e.target.value
              onValueChange(newValue)
              setSearchTerm(newValue)

              // Immer das Popover öffnen, wenn etwas eingegeben wird
              if (newValue.length > 0) {
                setOpen(true)
              }
            }}
            onKeyDown={handleKeyDown}
            onClick={(e) => {
              e.stopPropagation()
              // Öffne das Popover beim Klicken und behalte den Fokus
              if (!disabled) {
                setOpen(true)
              }
            }}
            onFocus={() => {
              if (!disabled) {
                setOpen(true)
              }
            }}
            placeholder={placeholder}
            disabled={disabled}
            className="w-full"
          />
          <Button
            variant="outline"
            size="icon"
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              setOpen(!open)
            }}
            disabled={disabled}
            className="ml-1"
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>
        <PopoverContent
          className="p-0 w-[400px]"
          align="start"
          sideOffset={5}
          onInteractOutside={(e) => {
            // Verhindern, dass das Popover geschlossen wird, wenn auf das Eingabefeld geklickt wird
            if (combinedRef.current?.contains(e.target as Node)) {
              e.preventDefault()
            }
          }}
        >
          <Command ref={commandRef}>
            <div className="flex items-center border-b px-3">
              <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Suche nach Artikelnummer oder Beschreibung..."
                autoFocus
              />
            </div>
            <CommandList>
              <CommandEmpty>Keine Artikel gefunden</CommandEmpty>
              <CommandGroup heading="Artikel">
                {filteredArticles.map((article, index) => (
                  <CommandItem
                    key={article.id}
                    onSelect={() => handleSelect(article)}
                    className={cn("flex flex-col items-start py-2", highlightedIndex === index ? "bg-accent" : "")}
                  >
                    <div className="flex w-full justify-between">
                      <div className="flex flex-col">
                        <div className="flex items-center">
                          <span className="font-medium">{article.currentArticleNumber}</span>
                          {article.oldArticleNumber && (
                            <span className="ml-2 text-xs text-muted-foreground">
                              (alt: {article.oldArticleNumber})
                            </span>
                          )}
                        </div>
                        <span>{article.name}</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="font-medium">{formatCurrency(article.price)}</span>
                        <span className={getStockColor(article.inStock)}>Bestand: {article.inStock} Stück</span>
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
} 