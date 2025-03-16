"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Plus,
  Minus,
  FileText,
  Settings,
  Search,
  Eye,
  ChevronDown,
  Menu,
  X,
  Filter,
  ArrowUpDown,
  MoreHorizontal,
} from "lucide-react"

export default function Products() {
  const [selectedItem, setSelectedItem] = useState<string | null>("218300")
  const [showSidebar, setShowSidebar] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredProducts, setFilteredProducts] = useState<any[]>([])

  const products = [
    { nummer: "307967", bezeichnung: "Product A" },
    { nummer: "132355", bezeichnung: "Product B" },
    { nummer: "912859", bezeichnung: '"Adler"-Erste Eisenbahn' },
    { nummer: "218300", bezeichnung: '"Adler"-Lock' },
    { nummer: "310048", bezeichnung: '"Adler"-Tender' },
    { nummer: "411430", bezeichnung: '"Adler"-Wagen' },
    { nummer: "409129", bezeichnung: '"Adler"-Wagen-offen' },
    { nummer: "300251", bezeichnung: '"Adler"-Wagen/Führer' },
    { nummer: "922678", bezeichnung: "100-0" },
    { nummer: "325473", bezeichnung: "100-0/3" },
    { nummer: "530620", bezeichnung: "100-0/5" },
    { nummer: "921063", bezeichnung: "1x Saugnapf für Glasscheibe Vitrine" },
    { nummer: "903786", bezeichnung: "22 Zoll Display Sichtschutz Bildschirm" },
    { nummer: "718205", bezeichnung: "27 Zoll Display Sichtschutz Bildschirm" },
    { nummer: "701703", bezeichnung: "5x BelegDrucker Rollen" },
    { nummer: "831738", bezeichnung: "7 miniatur Hasen in drei Teile" },
    { nummer: "309069", bezeichnung: "7 Schwaben mit Hase" },
    { nummer: "811140", bezeichnung: "80-2" },
    { nummer: "304527", bezeichnung: "80-4" },
  ]

  useEffect(() => {
    setFilteredProducts(
      products.filter(
        (product) =>
          product.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
          product.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase()),
      ),
    )
  }, [searchTerm])

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">Products</h1>
      
      <Card className="shadow-lg border-0 overflow-hidden rounded-xl">
        {/* Header/Toolbar */}
        <div className="p-3 sm:p-4 flex items-center gap-3 border-b bg-white dark:bg-slate-800 sticky top-0 z-10">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            {showSidebar ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" className="h-9 w-9 rounded-full">
              <Plus className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" className="h-9 w-9 rounded-full">
              <Minus className="h-4 w-4" />
            </Button>
          </div>

          <div className="relative flex-1 max-w-md">
            <Input
              className="pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-slate-400"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="absolute left-3 top-1/2 -translate-y-1/2">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            {searchTerm && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full"
                onClick={() => setSearchTerm("")}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>

          <div className="hidden sm:flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
              <FileText className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
              <Eye className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
              <Filter className="h-4 w-4" />
            </Button>
          </div>

          <div className="ml-auto">
            <Button className="h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white">Add Product</Button>
          </div>
        </div>

        <div className="flex flex-col md:flex-row">
          {/* Sidebar */}
          {showSidebar && (
            <div className="w-full md:w-1/3 lg:w-1/4 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
              <div className="border-b border-slate-200 dark:border-slate-700">
                <div className="max-h-[calc(100vh-220px)] overflow-auto">
                  <div className="p-3 flex items-center justify-between">
                    <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400">Products</h2>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7 rounded-full">
                        <ArrowUpDown className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 rounded-full">
                        <Filter className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                  <div className="px-2">
                    {filteredProducts.map((product) => (
                      <div
                        key={product.nummer}
                        className={`p-2 my-1 rounded-lg cursor-pointer transition-colors ${
                          selectedItem === product.nummer
                            ? "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500"
                            : "hover:bg-slate-100 dark:hover:bg-slate-700/50"
                        }`}
                        onClick={() => setSelectedItem(product.nummer)}
                      >
                        <div className="font-medium">{product.nummer}</div>
                        <div className="text-sm text-slate-500 dark:text-slate-400 truncate">
                          {product.bezeichnung || "—"}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className={`flex-1 ${!showSidebar ? "w-full" : ""}`}>
            {selectedItem ? (
              <div className="p-6 bg-white dark:bg-slate-800">
                <div className="space-y-8 max-w-5xl mx-auto">
                  {/* Product Details */}
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">Product Details</h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                      <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                        Product Name
                      </label>
                      <div className="md:col-span-3">
                        <Input
                          defaultValue={products.find(p => p.nummer === selectedItem)?.bezeichnung || ""}
                          className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                      <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                        Description
                      </label>
                      <div className="md:col-span-3">
                        <textarea
                          className="w-full border border-slate-200 dark:border-slate-700 rounded-md p-3 text-sm min-h-[150px] resize-none bg-slate-50 dark:bg-slate-800"
                          defaultValue="Product description goes here..."
                        />
                      </div>
                    </div>
                  </div>

                  <Separator className="bg-slate-200 dark:bg-slate-700" />

                  {/* Product Specifications */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200">Specifications</h3>
                      <Badge
                        variant="outline"
                        className="text-xs font-normal px-2 py-0.5 border-slate-200 dark:border-slate-700"
                      >
                        Optional
                      </Badge>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          SKU
                        </label>
                        <Input
                          defaultValue={selectedItem}
                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Price
                        </label>
                        <Input
                          type="number"
                          defaultValue="99.99"
                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Stock
                        </label>
                        <Input
                          type="number"
                          defaultValue="100"
                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Category
                        </label>
                        <Input
                          defaultValue="General"
                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 flex items-center justify-center h-full">
                <p className="text-slate-500 dark:text-slate-400">Select a product to view details</p>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
} 