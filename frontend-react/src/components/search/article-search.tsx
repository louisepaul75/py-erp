"use client";

import React from "react";

import { useState, useRef, useEffect, useMemo } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Search, Loader2, ImageIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { useGlobalSearch, type SearchResult, type SearchResponse } from "@/hooks/useGlobalSearch"
import Image from 'next/image';

// Artikel-Typ
export interface Article {
  id: string
  currentArticleNumber: string
  oldArticleNumber?: string
  name: string
  description?: string
  price: number
  retail_price?: number | null
  wholesale_price?: number | null
  variant_code?: string | null
  unit?: string
  inStock?: number
  quantity?: number
  category?: string
}

// Define SearchResult with optional image URL (mirroring backend change)
interface SearchResultWithImage extends SearchResult {
  primary_image_thumbnail_url?: string | null;
}

// Update hook usage type - Use the imported SearchResponse
interface SearchResponseWithImage extends SearchResponse { 
  results: {
    customers: SearchResult[];
    sales_records: SearchResult[];
    parent_products: SearchResultWithImage[];
    variant_products: SearchResultWithImage[];
    box_slots: SearchResult[];
    storage_locations: SearchResult[];
  };
}

interface ArticleSearchProps {
  value: string
  onValueChange: (value: string) => void
  onArticleSelect: (article: Article) => void
  onTabNavigation?: () => void
  disabled?: boolean
  className?: string
  placeholder?: string
  inputRef?: React.RefObject<HTMLInputElement>
  autoOpenOnInput?: boolean
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
  autoOpenOnInput = false,
}: ArticleSearchProps) {
  const [open, setOpen] = useState(false)
  const {
    query: searchTerm,
    setQuery: setSearchTerm,
    results,
    isLoading,
    error,
    reset: resetSearch,
   } = useGlobalSearch() as {
     query: string;
     setQuery: (newQuery: string) => void;
     results: SearchResponseWithImage | null;
     isLoading: boolean;
     error: string | null;
     reset: () => void;
     getAllResults: () => SearchResult[]; // Assuming getAllResults exists and returns base SearchResult
   };

  const [highlightedIndex, setHighlightedIndex] = useState(0)
  const inputInnerRef = useRef<HTMLInputElement>(null)
  const commandRef = useRef<HTMLDivElement>(null)
  const popoverContentRef = useRef<HTMLDivElement>(null)

  const combinedRef = inputRef || inputInnerRef

  const filteredProducts = useMemo(() => {
    if (!results?.results) return []
    // Cast to SearchResultWithImage when filtering
    return [
      ...(results.results.parent_products || []),
      ...(results.results.variant_products || [])
    ].filter(p => p.type === 'parent_product' || p.type === 'variant_product') as SearchResultWithImage[];
  }, [results])

  useEffect(() => {
    setHighlightedIndex(0)
  }, [filteredProducts])

  const handleSelect = (product: SearchResultWithImage) => {
    const selectedArticle: Article = {
      id: product.id.toString(),
      currentArticleNumber: product.sku || '',
      oldArticleNumber: product.legacy_sku,
      name: product.name || 'Unknown Product',
      description: product.name,
      price: product.retail_price || 0,
      retail_price: product.retail_price,
      wholesale_price: product.wholesale_price,
      variant_code: product.variant_code,
      quantity: 1,
    }
    onArticleSelect(selectedArticle)
    onValueChange(selectedArticle.currentArticleNumber)
    setOpen(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return

    if (!open) {
      if (e.key === "ArrowDown" || e.key === "Enter") {
        e.preventDefault()
        setOpen(true)
        if (value) {
          setSearchTerm(value)
        }
        return
      }
      if (e.key === 'Tab') {
        onTabNavigation?.()
        return
      }
    }

    if (open && filteredProducts.length > 0) {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault()
          setHighlightedIndex((prevIndex) =>
            prevIndex < filteredProducts.length - 1 ? prevIndex + 1 : prevIndex
          )
          commandRef.current?.querySelector(`[data-rk-value="${filteredProducts[highlightedIndex + 1]?.id}"]`)?.scrollIntoView({ block: 'nearest' })
          break
        case "ArrowUp":
          e.preventDefault()
          setHighlightedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : 0))
          commandRef.current?.querySelector(`[data-rk-value="${filteredProducts[highlightedIndex - 1]?.id}"]`)?.scrollIntoView({ block: 'nearest' })
          break
        case "Enter":
          e.preventDefault()
          if (highlightedIndex >= 0 && highlightedIndex < filteredProducts.length) {
            handleSelect(filteredProducts[highlightedIndex])
          }
          break
        case "Tab":
          e.preventDefault()
          if (highlightedIndex >= 0 && highlightedIndex < filteredProducts.length) {
            handleSelect(filteredProducts[highlightedIndex])
          }
          onTabNavigation?.()
          break
        case "Escape":
          e.preventDefault()
          setOpen(false)
          break
      }
    } else if (open && e.key === 'Escape') {
      e.preventDefault()
      setOpen(false)
    }
  }

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
          setOpen(newOpen)
          if (!newOpen) {
          }
        }}
        modal={false}
      >
        <PopoverTrigger asChild onClick={(e) => e.stopPropagation()}>
          <div className="flex">
            <Input
              ref={combinedRef}
              value={value}
              onChange={(e) => {
                const newValue = e.target.value
                onValueChange(newValue)
                setSearchTerm(newValue)
                if (newValue && !open) {
                  setOpen(true)
                } else if (!newValue) {
                  setOpen(false)
                }
              }}
              onKeyDown={handleKeyDown}
              onClick={(e) => {
                e.stopPropagation()
                if (!disabled && !open) {
                  setOpen(true)
                  if (value) {
                    setSearchTerm(value)
                  }
                }
              }}
              onFocus={() => {
                if (!disabled && autoOpenOnInput) {
                  setOpen(true)
                  if (value) {
                    setSearchTerm(value)
                  }
                }
              }}
              placeholder={placeholder}
              disabled={disabled}
              className="w-full"
              autoComplete="off"
            />
            <Button
              variant="outline"
              size="icon"
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                if (!disabled) {
                  setOpen(!open)
                  if (!open && value) {
                    setSearchTerm(value)
                  }
                }
              }}
              disabled={disabled}
              className="ml-1"
              aria-label="Search articles"
            >
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </PopoverTrigger>
        <PopoverContent
          ref={popoverContentRef}
          className="p-0 w-[500px] max-h-[60vh] overflow-y-auto"
          align="start"
          sideOffset={5}
          onInteractOutside={(e) => {
            if (combinedRef.current?.contains(e.target as Node)) {
              e.preventDefault()
            }
          }}
          onCloseAutoFocus={(e) => e.preventDefault()}
        >
          <Command ref={commandRef} shouldFilter={false}>
            <CommandList>
              {isLoading && (
                <div className="p-4 flex items-center justify-center text-sm text-muted-foreground">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading...
                </div>
              )}
              {error && !isLoading && (
                <div className="p-4 text-center text-sm text-destructive">
                  Error: {error}
                </div>
              )}
              {!isLoading && !error && filteredProducts.length === 0 && searchTerm && (
                <CommandEmpty>Keine Artikel gefunden für "{searchTerm}"</CommandEmpty>
              )}
              {!isLoading && !error && filteredProducts.length === 0 && !searchTerm && (
                <CommandEmpty>Bitte Suchbegriff eingeben.</CommandEmpty>
              )}
              {!isLoading && !error && filteredProducts.length > 0 && (
                <CommandGroup heading="Artikel">
                  {filteredProducts.map((product, index) => (
                    <CommandItem
                      key={product.id}
                      value={product.id.toString()}
                      onSelect={() => handleSelect(product)}
                      className={cn("flex flex-row items-center gap-3 py-2 cursor-pointer data-[selected=true]:bg-accent", highlightedIndex === index ? "bg-accent" : "")}
                      data-rk-value={product.id}
                    >
                      <div className="flex-shrink-0 w-10 h-10 bg-muted rounded flex items-center justify-center overflow-hidden">
                        {product.primary_image_thumbnail_url ? (
                          <Image
                            src={product.primary_image_thumbnail_url}
                            alt={product.name || product.sku || 'Product Image'}
                            width={40}
                            height={40}
                            className="object-cover"
                            onError={(e) => { e.currentTarget.style.display = 'none'; }}
                          />
                        ) : (
                          <ImageIcon className="h-5 w-5 text-muted-foreground" />
                        )}
                      </div>
                      <div className="flex-grow flex flex-col overflow-hidden">
                        <div className="flex items-baseline">
                          <span className="font-medium truncate" title={product.sku || 'N/A'}>{product.sku || 'N/A'}</span>
                          {product.variant_code && (
                            <span className="ml-2 text-xs text-muted-foreground truncate" title={`Code: ${product.variant_code}`}>
                              (Code: {product.variant_code})
                            </span>
                          )}
                          {product.legacy_sku && (
                            <span className="ml-2 text-xs text-muted-foreground truncate" title={`(alt: ${product.legacy_sku})`}>
                              (alt: {product.legacy_sku})
                            </span>
                          )}
                        </div>
                        <span className="text-sm text-muted-foreground truncate" title={product.name || 'No Name'}>{product.name || 'No Name'}</span>
                        {(product.retail_price || product.wholesale_price) && (
                          <div className="text-xs text-muted-foreground flex gap-2 mt-0.5">
                            {product.retail_price && (
                              <span title={`Retail: ${formatCurrency(product.retail_price)}`}>
                                VK: {formatCurrency(product.retail_price)}
                              </span>
                            )}
                            {product.wholesale_price && (
                              <span title={`Wholesale: ${formatCurrency(product.wholesale_price)}`}>
                                EK: {formatCurrency(product.wholesale_price)}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
} 