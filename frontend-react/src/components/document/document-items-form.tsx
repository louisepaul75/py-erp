"use client"

import React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { PlusCircle, Trash2, Search, ArrowDown, ArrowUp, HelpCircle } from "lucide-react"
import type { DocumentItem } from "@/types/document/document"
import { Badge } from "@/components/ui/badge"
import { ArticleSearch, type Article } from "@/components/articles/article-search"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

/**
 * Props for the DocumentItemsForm component
 */
interface DocumentItemsFormProps {
  items: DocumentItem[]
  setItems: (items: DocumentItem[]) => void
  onBack: () => void
  onSubmit: () => void
  isSubmitting: boolean
  shippingCost: number
  setShippingCost: (value: number) => void
  handlingFee: number
  setHandlingFee: (value: number) => void
  taxRate: number
  taxIncluded: boolean
}

/**
 * DocumentItemsForm component that displays a form for adding and editing document items
 * Redesigned to work better with the fullscreen edit view
 */
export function DocumentItemsForm(props: DocumentItemsFormProps) {
  const { items, setItems, onBack, onSubmit, isSubmitting } = props

  // State for the new item being added
  const [newItem, setNewItem] = useState<Partial<DocumentItem>>({
    productId: "",
    description: "",
    quantity: 1,
    price: 0,
  })

  // State for search term
  const [searchTerm, setSearchTerm] = useState("")

  // State for sort configuration
  const [sortConfig, setSortConfig] = useState<{
    key: keyof DocumentItem | null
    direction: "ascending" | "descending"
  }>({
    key: null,
    direction: "ascending",
  })

  // Refs für die Inputs der letzten Zeile
  const lastRowRefs = useRef<{
    productId: React.RefObject<HTMLInputElement>
    description: HTMLInputElement | null
    quantity: HTMLInputElement | null
    price: HTMLInputElement | null
  }>({
    productId: React.createRef<HTMLInputElement>(),
    description: null,
    quantity: null,
    price: null,
  })

  // Add a new item to the list
  const addItem = () => {
    if (!newItem.productId || !newItem.description || newItem.quantity <= 0 || newItem.price <= 0) {
      return
    }

    setItems([
      ...items,
      {
        id: `temp-${Date.now()}`,
        ...(newItem as DocumentItem),
      },
    ])

    // Reset the new item form
    setNewItem({
      productId: "",
      description: "",
      quantity: 1,
      price: 0,
    })

    // Fokus auf das erste Feld der neuen Zeile setzen (verzögert, damit die Zeile gerendert wird)
    setTimeout(() => {
      if (lastRowRefs.current.productId && lastRowRefs.current.productId.current) {
        lastRowRefs.current.productId.current.focus()
      }
    }, 100)
  }

  // Remove an item from the list
  const removeItem = (id: string) => {
    setItems(items.filter((item) => item.id !== id))
  }

  // Handle article selection
  const handleArticleSelect = (item: DocumentItem, article: Article) => {
    setItems(
      items.map((existingItem) => {
        if (existingItem.id === item.id) {
          return {
            ...existingItem,
            productId: article.currentArticleNumber,
            description: article.name,
            price: article.price,
            quantity: article.quantity || existingItem.quantity,
          }
        }
        return existingItem
      }),
    )
  }

  // Handle article selection for new item
  const handleNewArticleSelect = (article: Article) => {
    setNewItem({
      ...newItem,
      productId: article.currentArticleNumber,
      description: article.name,
      price: article.price,
      quantity: article.quantity || 1,
    })
  }

  // Calculate the total amount
  const subtotal = items.reduce((total, item) => total + item.quantity * item.price, 0)
  const shippingCost = props.shippingCost || 0
  const handlingFee = props.handlingFee || 0
  const taxRate = props.taxRate || 0
  const taxIncluded = props.taxIncluded

  const totalBeforeTax = subtotal + shippingCost + handlingFee
  let taxAmount = 0
  let totalAmount = 0

  if (taxIncluded) {
    // Wenn MwSt. bereits enthalten ist, berechnen wir den Nettobetrag und die MwSt.
    taxAmount = totalBeforeTax - totalBeforeTax / (1 + taxRate / 100)
    totalAmount = totalBeforeTax
  } else {
    // Wenn MwSt. nicht enthalten ist, addieren wir sie zum Nettobetrag
    taxAmount = totalBeforeTax * (taxRate / 100)
    totalAmount = totalBeforeTax + taxAmount
  }

  // Handle sorting
  const requestSort = (key: keyof DocumentItem) => {
    let direction: "ascending" | "descending" = "ascending"

    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending"
    }

    setSortConfig({ key, direction })
  }

  // Apply sorting and filtering
  const getSortedItems = () => {
    let sortableItems = [...items]

    // Apply search filter
    if (searchTerm) {
      const lowerCaseSearch = searchTerm.toLowerCase()
      sortableItems = sortableItems.filter(
        (item) =>
          item.productId.toLowerCase().includes(lowerCaseSearch) ||
          item.description.toLowerCase().includes(lowerCaseSearch),
      )
    }

    // Apply sorting
    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        if (a[sortConfig.key!] < b[sortConfig.key!]) {
          return sortConfig.direction === "ascending" ? -1 : 1
        }
        if (a[sortConfig.key!] > b[sortConfig.key!]) {
          return sortConfig.direction === "ascending" ? 1 : -1
        }
        return 0
      })
    }

    return sortableItems
  }

  // Get sorted and filtered items
  const sortedItems = getSortedItems()

  // Render sort indicator
  const renderSortIndicator = (key: keyof DocumentItem) => {
    if (sortConfig.key !== key) {
      return null
    }
    return sortConfig.direction === "ascending" ? (
      <ArrowUp className="h-3 w-3 ml-1" />
    ) : (
      <ArrowDown className="h-3 w-3 ml-1" />
    )
  }

  // Tastaturnavigation
  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    itemId: string,
    field: keyof DocumentItem,
    rowIndex: number,
    isLastRow: boolean,
  ) => {
    // Enter-Taste
    if (e.key === "Enter") {
      e.preventDefault()

      // Wenn es die letzte Zeile ist und mindestens ein Feld ausgefüllt ist, neue Zeile hinzufügen
      if (isLastRow && (items[rowIndex].productId || items[rowIndex].description)) {
        addItem()
      } else {
        // Sonst zum nächsten Feld in der aktuellen Zeile navigieren
        const nextField = getNextField(field)
        const currentRowRefs = isLastRow ? lastRowRefs.current : null

        if (currentRowRefs && nextField && currentRowRefs[nextField as keyof typeof currentRowRefs]) {
          currentRowRefs[nextField as keyof typeof currentRowRefs]?.focus()
        }
      }
    }

    // Pfeiltasten für Navigation zwischen Zeilen
    if (e.key === "ArrowUp" && rowIndex > 0) {
      e.preventDefault()
      // Fokus auf das gleiche Feld in der vorherigen Zeile setzen
      const prevRowInput = document.getElementById(`${field}-${items[rowIndex - 1].id}`)
      prevRowInput?.focus()
    }

    if (e.key === "ArrowDown" && rowIndex < items.length - 1) {
      e.preventDefault()
      // Fokus auf das gleiche Feld in der nächsten Zeile setzen
      const nextRowInput = document.getElementById(`${field}-${items[rowIndex + 1].id}`)
      nextRowInput?.focus()
    }
  }

  // Bestimmt das nächste Feld in der Tabulatorreihenfolge
  const getNextField = (currentField: keyof DocumentItem): keyof DocumentItem | null => {
    const fieldOrder: (keyof DocumentItem)[] = ["productId", "description", "quantity", "price"]
    const currentIndex = fieldOrder.indexOf(currentField)

    if (currentIndex < fieldOrder.length - 1) {
      return fieldOrder[currentIndex + 1]
    }

    return null
  }

  // Formatieren von Währungsbeträgen
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("de-DE", {
      style: "currency",
      currency: "EUR",
    }).format(amount)
  }

  return (
    <div className="space-y-6">
      {/* Tastaturhilfe-Karte */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center">
              <HelpCircle className="h-4 w-4 mr-2" />
              Tastaturnavigation
            </CardTitle>
          </div>
          <CardDescription>Schnellere Eingabe mit Tastaturkürzeln</CardDescription>
        </CardHeader>
        <CardContent className="text-sm">
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <li className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-muted rounded text-xs">Tab</kbd>
              <span>Zum nächsten Feld navigieren</span>
            </li>
            <li className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-muted rounded text-xs">Shift + Tab</kbd>
              <span>Zum vorherigen Feld navigieren</span>
            </li>
            <li className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-muted rounded text-xs">Enter</kbd>
              <span>Zum nächsten Feld oder neue Zeile hinzufügen</span>
            </li>
            <li className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-muted rounded text-xs">↑</kbd>
              <span>Zum gleichen Feld in der Zeile darüber</span>
            </li>
            <li className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-muted rounded text-xs">↓</kbd>
              <span>Zum gleichen Feld in der Zeile darunter</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Add New Item Section */}
      <div className="bg-white p-6 rounded-lg border shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <div className="text-primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M11 12H3" />
              <path d="M16 6H3" />
              <path d="M16 18H3" />
              <path d="M18 9v6" />
              <path d="M21 12h-6" />
            </svg>
          </div>
          <h3 className="text-lg font-medium">Neue Position hinzufügen</h3>
        </div>

        <div className="grid grid-cols-12 gap-3">
          <div className="col-span-12 sm:col-span-3">
            <div
              onClick={(e) => {
                // Verhindern, dass das Event weitergeleitet wird
                e.stopPropagation()
              }}
            >
              <ArticleSearch
                value={newItem.productId || ""}
                onValueChange={(value) => {
                  setNewItem({ ...newItem, productId: value })
                  // Keine zusätzliche Logik hier nötig, da die Komponente selbst das Öffnen handhabt
                }}
                onArticleSelect={handleNewArticleSelect}
                placeholder="Artikel-Nr."
                className="w-full"
              />
            </div>
          </div>
          <div className="col-span-12 sm:col-span-4">
            <Input
              placeholder="Beschreibung"
              value={newItem.description || ""}
              onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
            />
          </div>
          <div className="col-span-6 sm:col-span-2">
            <Input
              type="number"
              placeholder="Menge"
              min={1}
              value={newItem.quantity || 1}
              onChange={(e) => setNewItem({ ...newItem, quantity: Number.parseInt(e.target.value) || 1 })}
            />
          </div>
          <div className="col-span-6 sm:col-span-2">
            <Input
              type="number"
              placeholder="Preis"
              step="0.01"
              min={0}
              value={newItem.price || 0}
              onChange={(e) => setNewItem({ ...newItem, price: Number.parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div className="col-span-12 sm:col-span-1">
            <Button type="button" className="w-full" onClick={addItem}>
              <PlusCircle className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Hinzufügen</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Items List Section */}
      <div className="bg-white p-6 rounded-lg border shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <div className="text-primary">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="8" y1="6" x2="21" y2="6" />
                <line x1="8" y1="12" x2="21" y2="12" />
                <line x1="8" y1="18" x2="21" y2="18" />
                <line x1="3" y1="6" x2="3.01" y2="6" />
                <line x1="3" y1="12" x2="3.01" y2="12" />
                <line x1="3" y1="18" x2="3.01" y2="18" />
              </svg>
            </div>
            <h3 className="text-lg font-medium">Positionen</h3>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Suchen..."
                className="pl-8 w-[200px]"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Badge variant="outline">{sortedItems.length} Positionen</Badge>
          </div>
        </div>

        {sortedItems.length > 0 ? (
          <div className="border rounded-md overflow-hidden">
            <div className="max-h-[calc(95vh-350px)] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="cursor-pointer" onClick={() => requestSort("productId")}>
                      <div className="flex items-center">
                        Artikel-Nr.
                        {renderSortIndicator("productId")}
                      </div>
                    </TableHead>
                    <TableHead className="cursor-pointer" onClick={() => requestSort("description")}>
                      <div className="flex items-center">
                        Beschreibung
                        {renderSortIndicator("description")}
                      </div>
                    </TableHead>
                    <TableHead className="text-right cursor-pointer" onClick={() => requestSort("quantity")}>
                      <div className="flex items-center justify-end">
                        Menge
                        {renderSortIndicator("quantity")}
                      </div>
                    </TableHead>
                    <TableHead className="text-right cursor-pointer" onClick={() => requestSort("price")}>
                      <div className="flex items-center justify-end">
                        Preis
                        {renderSortIndicator("price")}
                      </div>
                    </TableHead>
                    <TableHead className="text-right">Gesamt</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedItems.map((item, index) => {
                    const isLastRow = index === sortedItems.length - 1
                    return (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div
                            onClick={(e) => {
                              // Verhindern, dass das Event weitergeleitet wird
                              e.stopPropagation()
                            }}
                          >
                            <ArticleSearch
                              value={item.productId}
                              onValueChange={(value) => {
                                setItems(items.map((i) => (i.id === item.id ? { ...i, productId: value } : i)))
                                // Keine zusätzliche Logik hier nötig, da die Komponente selbst das Öffnen handhabt
                              }}
                              onArticleSelect={(article) => handleArticleSelect(item, article)}
                              onTabNavigation={() => {
                                // Fokus auf das Beschreibungsfeld setzen
                                const descriptionInput = document.getElementById(`description-${item.id}`)
                                if (descriptionInput) {
                                  descriptionInput.focus()
                                }
                              }}
                              inputRef={isLastRow ? lastRowRefs.current.productId : undefined}
                              className="min-w-[120px]"
                            />
                          </div>
                        </TableCell>
                        <TableCell>
                          <Input
                            id={`description-${item.id}`}
                            value={item.description}
                            onChange={(e) => {
                              setItems(items.map((i) => (i.id === item.id ? { ...i, description: e.target.value } : i)))
                            }}
                            onKeyDown={(e) => handleKeyDown(e, item.id, "description", index, isLastRow)}
                            placeholder="Beschreibung"
                            ref={
                              isLastRow
                                ? (el) => {
                                    lastRowRefs.current.description = el
                                  }
                                : undefined
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            id={`quantity-${item.id}`}
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) => {
                              setItems(
                                items.map((i) =>
                                  i.id === item.id ? { ...i, quantity: Number(e.target.value) || 1 } : i,
                                ),
                              )
                            }}
                            onKeyDown={(e) => handleKeyDown(e, item.id, "quantity", index, isLastRow)}
                            className="text-right"
                            ref={
                              isLastRow
                                ? (el) => {
                                    lastRowRefs.current.quantity = el
                                  }
                                : undefined
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            id={`price-${item.id}`}
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.price}
                            onChange={(e) => {
                              setItems(
                                items.map((i) => (i.id === item.id ? { ...i, price: Number(e.target.value) || 0 } : i)),
                              )
                            }}
                            onKeyDown={(e) => handleKeyDown(e, item.id, "price", index, isLastRow)}
                            className="text-right"
                            ref={
                              isLastRow
                                ? (el) => {
                                    lastRowRefs.current.price = el
                                  }
                                : undefined
                            }
                          />
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(item.quantity * item.price)}
                        </TableCell>
                        <TableCell>
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => removeItem(item.id)}
                                  disabled={items.length <= 1}
                                >
                                  <Trash2 className="h-4 w-4 text-muted-foreground" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Position löschen</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  <TableRow>
                    <TableCell colSpan={4} className="text-right font-medium">
                      Zwischensumme:
                    </TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(subtotal)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={3} className="text-right font-medium">
                      Versandkosten:
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end">
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          value={props.shippingCost}
                          onChange={(e) => props.setShippingCost(Number.parseFloat(e.target.value) || 0)}
                          className="w-28 h-8 text-right border rounded-md px-2"
                        />
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(props.shippingCost)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={3} className="text-right font-medium">
                      Bearbeitungsgebühr:
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end">
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          value={props.handlingFee}
                          onChange={(e) => props.setHandlingFee(Number.parseFloat(e.target.value) || 0)}
                          className="w-28 h-8 text-right border rounded-md px-2"
                        />
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(props.handlingFee)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={4} className="text-right font-medium">
                      MwSt. ({taxRate}%):
                    </TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(taxAmount)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                  <TableRow className="bg-muted/20">
                    <TableCell colSpan={4} className="text-right font-bold">
                      Gesamtbetrag:
                    </TableCell>
                    <TableCell className="text-right font-bold">{formatCurrency(totalAmount)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>
        ) : (
          <div className="border rounded-md p-8 text-center text-muted-foreground">
            Keine Positionen vorhanden. Fügen Sie Positionen über das Formular oben hinzu.
          </div>
        )}
      </div>

      {/* Button zum Hinzufügen einer neuen Position */}
      <Button type="button" variant="outline" onClick={addItem} className="mt-2">
        <PlusCircle className="mr-2 h-4 w-4" />
        Position hinzufügen
      </Button>
    </div>
  )
}
