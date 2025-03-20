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
import BilderTab from "@/components/bilder-tab"
import GewogenTab from "@/components/gewogen-tab"
import LagerorteTab from "@/components/lagerorte-tab"
import UmsatzeTab from "@/components/umsatze-tab"
import BewegungenTab from "@/components/bewegungen-tab"
import TeileTab from "@/components/teile-tab"

export default function InventoryManagement() {
  const [selectedItem, setSelectedItem] = useState<string | null>("218300")
  const [activeTab, setActiveTab] = useState("mutter")
  const [variantenActiveTab, setVariantenActiveTab] = useState("details")
  const [showSidebar, setShowSidebar] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredProducts, setFilteredProducts] = useState<any[]>([])
  const [allProducts, setAllProducts] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Use mock data instead of API call
  useEffect(() => {
    // Mock product data
    const mockProducts = [
      { id: 1, nummer: "218300", bezeichnung: "Zinnfigur Hirte mit Schaf", description: "Handgefertigte Zinnfigur" },
      { id: 2, nummer: "218301", bezeichnung: "Zinnfigur Engel", description: "Handgefertigte Zinnfigur" },
      { id: 3, nummer: "218302", bezeichnung: "Zinnfigur Krippe", description: "Handgefertigte Zinnfigur" },
    ]
    setAllProducts(mockProducts)
    setFilteredProducts(mockProducts)
  }, [])

  // Filter products based on search term
  useEffect(() => {
    if (allProducts.length > 0) {
      if (searchTerm) {
        const filtered = allProducts.filter(
          (product) =>
            product.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
            product.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredProducts(filtered);
      } else {
        setFilteredProducts(allProducts);
      }
    }
  }, [searchTerm, allProducts]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-slate-600 dark:text-slate-400">Loading products...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-slate-800 dark:text-slate-200 font-medium">{error}</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <div className="container mx-auto p-2 sm:p-4 max-w-[1600px]">
        <Card className="shadow-lg border-0 overflow-hidden rounded-xl">
          {/* Header/Toolbar */}
          <div className="p-3 sm:p-4 flex items-center gap-3 border-b bg-white dark:bg-slate-800 sticky top-16 z-10">
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
                placeholder="Suchen..."
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
              <Button className="h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white">Artikel übernehmen</Button>
            </div>
          </div>

          <div className="flex flex-col md:flex-row">
            {/* Sidebar */}
            {showSidebar && (
              <div className="w-full md:w-1/3 lg:w-1/4 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <div className="border-b border-slate-200 dark:border-slate-700">
                  <div className="max-h-[calc(100vh-220px)] overflow-auto">
                    <div className="p-3 flex items-center justify-between">
                      <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400">Produkte</h2>
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
                          <div className="font-medium flex items-center">
                            {product.nummer}
                            {product.nummer === "218300" && (
                              <span className="ml-2 px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                                Parent
                              </span>
                            )}
                            {(product.nummer === "310048" || product.nummer === "411430" || product.nummer === "409129") && (
                              <span className="ml-2 px-1.5 py-0.5 text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded">
                                Variant
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400 truncate">
                            {product.bezeichnung || "—"}
                          </div>
                          {(product.nummer === "310048" || product.nummer === "411430" || product.nummer === "409129") && (
                            <div className="text-xs text-slate-400 dark:text-slate-500 mt-1 flex items-center">
                              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                                <path d="M5 12h14" />
                                <path d="M12 5v14" />
                              </svg>
                              Parent: 218300
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Main Content */}
            <div className={`flex-1 ${!showSidebar ? "w-full" : ""}`}>
              {/* Mutter/Varianten Tabs */}
              <div className="flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                <button
                  className={`px-6 py-4 text-sm font-medium transition-colors relative ${
                    activeTab === "mutter"
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                  }`}
                  onClick={() => setActiveTab("mutter")}
                >
                  Mutter
                  {activeTab === "mutter" && (
                    <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500"></span>
                  )}
                </button>
                <button
                  className={`px-6 py-4 text-sm font-medium transition-colors relative ${
                    activeTab === "varianten"
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                  }`}
                  onClick={() => setActiveTab("varianten")}
                >
                  Varianten
                  {activeTab === "varianten" && (
                    <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500"></span>
                  )}
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === "mutter" ? (
                <div className="p-6 bg-white dark:bg-slate-800">
                  {/* Parent/Variant Switcher */}
                  <div className="mb-6 flex items-center">
                    <label className="text-sm font-medium text-slate-500 dark:text-slate-400 mr-3">
                      Produkttyp:
                    </label>
                    <div className="relative inline-block">
                      <select
                        className="appearance-none bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md py-2 pl-3 pr-10 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        value={selectedItem === "218300" ? "parent" : "variant"}
                        onChange={(e) => {
                          if (e.target.value === "parent") {
                            setSelectedItem("218300"); // Parent product
                          } else {
                            setSelectedItem("310048"); // Example variant
                          }
                        }}
                      >
                        <option value="parent">Hauptprodukt</option>
                        <option value="variant">Variante</option>
                      </select>
                      <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                        <ChevronDown className="h-4 w-4 text-slate-400" />
                      </div>
                    </div>
                    
                    <div className="ml-6">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-xs"
                        onClick={() => {
                          // Toggle between parent and variant
                          if (selectedItem === "218300") {
                            setSelectedItem("310048"); // Switch to variant
                          } else {
                            setSelectedItem("218300"); // Switch to parent
                          }
                        }}
                      >
                        {selectedItem === "218300" ? "Als Variante anzeigen" : "Als Hauptprodukt anzeigen"}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-8 max-w-5xl mx-auto">
                    {/* Bezeichnung & Beschreibung */}
                    <div className="space-y-4">
                      <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">Produktdetails</h2>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                          Bezeichnung
                        </label>
                        <div className="md:col-span-3">
                          <Input
                            defaultValue="&quot;Adler&quot;-Lock"
                            className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                          Beschreibung
                        </label>
                        <div className="md:col-span-3">
                          <textarea
                            className="w-full border border-slate-200 dark:border-slate-700 rounded-md p-3 text-sm min-h-[150px] resize-none bg-slate-50 dark:bg-slate-800"
                            defaultValue="Erleben Sie die Eleganz und den Charme vergangener Zeiten mit dieser exquisiten Zinnfigur, inspiriert von den Anfängen der Eisenbahngeschichte. Perfekt für Sammler und Liebhaber von Nostalgie, zeigt diese Figur einen klassischen Lokführer, gekleidet in traditioneller Montur, der stolz seine Maschine lenkt. Ideal für jede Vitrine oder als geschmackvolles Geschenk. Eine Hommage an die Ingenieurskunst und das kulturelle Erbe."
                          />
                        </div>
                      </div>
                    </div>

                    <Separator className="bg-slate-200 dark:bg-slate-700" />

                    {/* Maße */}
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200">Maße</h3>
                        <Badge
                          variant="outline"
                          className="text-xs font-normal px-2 py-0.5 border-slate-200 dark:border-slate-700"
                        >
                          Einheit: mm
                        </Badge>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Breite</label>
                          <Input
                            defaultValue="7"
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Höhe</label>
                          <Input
                            defaultValue="7"
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Tiefe</label>
                          <Input
                            defaultValue="0,7"
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Gewicht (g)</label>
                          <Input
                            defaultValue="30"
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="hangend"
                            className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          />
                          <label htmlFor="hangend" className="text-sm">
                            Hängend
                          </label>
                        </div>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="einseitig"
                            className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          />
                          <label htmlFor="einseitig" className="text-sm">
                            Einseitig
                          </label>
                        </div>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="neuheit"
                            className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          />
                          <label htmlFor="neuheit" className="text-sm">
                            Neuheit
                          </label>
                        </div>
                      </div>
                      <div className="mt-4">
                        <div className="flex items-center gap-2">
                          <label className="text-sm font-medium text-slate-500 dark:text-slate-400 w-24">
                            Boxgröße
                          </label>
                          <Input
                            defaultValue="B5"
                            className="w-32 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator className="bg-slate-200 dark:bg-slate-700" />

                    {/* Kategorien */}
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200">Kategorien</h3>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="h-8 rounded-full">
                            <Plus className="h-3.5 w-3.5 mr-1" />
                            <span className="text-xs">Hinzufügen</span>
                          </Button>
                          <Button variant="outline" size="sm" className="h-8 rounded-full">
                            <Minus className="h-3.5 w-3.5 mr-1" />
                            <span className="text-xs">Entfernen</span>
                          </Button>
                        </div>
                      </div>
                      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                              <TableHead className="font-medium">Home</TableHead>
                              <TableHead className="font-medium">Sortiment</TableHead>
                              <TableHead className="font-medium">Tradition</TableHead>
                              <TableHead className="font-medium">Maschinerie</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow>
                              <TableCell>Home</TableCell>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                              <TableCell>All Products</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                              <TableCell></TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-6 bg-white dark:bg-slate-800">
                  {/* Varianten Tab Content */}
                  <div className="space-y-6">
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">Produktvarianten</h2>
                      <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                        <Plus className="h-4 w-4 mr-2" />
                        Neue Variante
                      </Button>
                    </div>

                    {/* Variants List */}
                    <div className="border rounded-lg overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-[100px]">Nummer</TableHead>
                            <TableHead>Bezeichnung</TableHead>
                            <TableHead className="w-[150px]">Typ</TableHead>
                            <TableHead className="w-[100px]">Bestand</TableHead>
                            <TableHead className="w-[100px]">Status</TableHead>
                            <TableHead className="w-[80px]"></TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {selectedItem === "218300" ? (
                            // Show variants of the parent product
                            <>
                              <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                                <TableCell className="font-medium">310048</TableCell>
                                <TableCell>"Adler"-Tender</TableCell>
                                <TableCell>Variante</TableCell>
                                <TableCell>23</TableCell>
                                <TableCell>
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                    Aktiv
                                  </span>
                                </TableCell>
                                <TableCell>
                                  <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </TableCell>
                              </TableRow>
                              <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                                <TableCell className="font-medium">411430</TableCell>
                                <TableCell>"Adler"-Wagen</TableCell>
                                <TableCell>Variante</TableCell>
                                <TableCell>15</TableCell>
                                <TableCell>
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                    Aktiv
                                  </span>
                                </TableCell>
                                <TableCell>
                                  <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </TableCell>
                              </TableRow>
                              <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                                <TableCell className="font-medium">409129</TableCell>
                                <TableCell>"Adler"-Wagen-offen</TableCell>
                                <TableCell>Variante</TableCell>
                                <TableCell>8</TableCell>
                                <TableCell>
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                    Aktiv
                                  </span>
                                </TableCell>
                                <TableCell>
                                  <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </TableCell>
                              </TableRow>
                            </>
                          ) : (
                            // Show message when a variant is selected
                            <TableRow>
                              <TableCell colSpan={6} className="text-center py-8 text-slate-500 dark:text-slate-400">
                                <div className="flex flex-col items-center justify-center">
                                  <div className="mb-2 p-2 rounded-full bg-slate-100 dark:bg-slate-800">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400">
                                      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                                      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                                      <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                                      <line x1="2" x2="22" y1="2" y2="22" />
                                    </svg>
                                  </div>
                                  <p>Dies ist bereits eine Variante. Bitte wählen Sie ein Hauptprodukt, um dessen Varianten anzuzeigen.</p>
                                  <Button 
                                    variant="outline" 
                                    size="sm" 
                                    className="mt-4"
                                    onClick={() => setSelectedItem("218300")}
                                  >
                                    Zum Hauptprodukt wechseln
                                  </Button>
                                </div>
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

