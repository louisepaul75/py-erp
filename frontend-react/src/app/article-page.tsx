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

  const products = [
    { nummer: "307967", bezeichnung: "" },
    { nummer: "132355", bezeichnung: "" },
    { nummer: "-1", bezeichnung: "" },
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <div className="container mx-auto p-2 sm:p-4 max-w-[1600px]">
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
                  <div className="max-h-[calc(100vh-120px)] overflow-auto">
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
                <div className="bg-white dark:bg-slate-800">
                  {/* Varianten View */}
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">Varianten</h2>
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

                    <div className="flex flex-col lg:flex-row gap-6">
                      <div className="flex-1 overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                              <TableHead className="font-medium">Nummer</TableHead>
                              <TableHead className="font-medium">Bezeichnung</TableHead>
                              <TableHead className="font-medium">Ausprägung</TableHead>
                              <TableHead className="w-12 text-center font-medium">Prod.</TableHead>
                              <TableHead className="w-12 text-center font-medium">Vertr.</TableHead>
                              <TableHead className="w-12 text-center font-medium">VK Artikel</TableHead>
                              <TableHead className="font-medium">Releas</TableHead>
                              <TableHead className="w-10"></TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow>
                              <TableCell className="font-medium">501506</TableCell>
                              <TableCell>"Adler"-Lock</TableCell>
                              <TableCell>Blank</TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    checked
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell>11.02.2023</TableCell>
                              <TableCell>
                                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                            <TableRow className="bg-blue-50/50 dark:bg-blue-900/10">
                              <TableCell className="font-medium">100870</TableCell>
                              <TableCell>"Adler"-Lock</TableCell>
                              <TableCell>Bemalt</TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    checked
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    checked
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    checked
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell>01.01.2023</TableCell>
                              <TableCell>
                                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell className="font-medium">904743</TableCell>
                              <TableCell>"Adler"-Lock OX</TableCell>
                              <TableCell></TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <div className="flex justify-center">
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                                    readOnly
                                  />
                                </div>
                              </TableCell>
                              <TableCell>01.01.1999</TableCell>
                              <TableCell>
                                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </div>
                      <div className="w-full lg:w-64 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="bg-slate-50 dark:bg-slate-800/50 p-3 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="text-sm font-medium">Eigenschaften</h3>
                        </div>
                        <Table>
                          <TableHeader>
                            <TableRow className="hover:bg-transparent">
                              <TableHead className="font-medium">Property</TableHead>
                              <TableHead className="font-medium">Option</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow>
                              <TableCell>Ausprägung</TableCell>
                              <TableCell>Blank</TableCell>
                            </TableRow>
                            {[...Array(5)].map((_, i) => (
                              <TableRow key={i}>
                                <TableCell></TableCell>
                                <TableCell></TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  </div>

                  {/* Varianten Tabs */}
                  <div className="border-t border-slate-200 dark:border-slate-700">
                    <Tabs
                      defaultValue="details"
                      value={variantenActiveTab}
                      onValueChange={setVariantenActiveTab}
                      className="w-full"
                    >
                      <div className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
                        <TabsList className="bg-transparent h-auto p-0 rounded-none flex-nowrap">
                          <TabsTrigger
                            value="details"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Details
                          </TabsTrigger>
                          <TabsTrigger
                            value="teile"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Teile
                          </TabsTrigger>
                          <TabsTrigger
                            value="bilder"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Bilder
                          </TabsTrigger>
                          <TabsTrigger
                            value="gewogen"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Gewogen
                          </TabsTrigger>
                          <TabsTrigger
                            value="lagerorte"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Lagerorte
                          </TabsTrigger>
                          <TabsTrigger
                            value="umsatze"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Umsätze
                          </TabsTrigger>
                          <TabsTrigger
                            value="bewegungen"
                            className="px-6 py-3 rounded-none data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800 data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none whitespace-nowrap"
                          >
                            Bewegungen
                          </TabsTrigger>
                        </TabsList>
                      </div>

                      <TabsContent value="details" className="p-0 m-0">
                        <div className="p-6">
                          <div className="flex justify-between mb-6">
                            <div className="flex items-center">
                              <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200 mr-3">
                                Kategorien
                              </h3>
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
                            <div className="flex items-center">
                              <input
                                type="checkbox"
                                id="neuheit-var"
                                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600 mr-2"
                              />
                              <label htmlFor="neuheit-var" className="text-sm">
                                Neuheit
                              </label>
                            </div>
                          </div>

                          <div className="mb-8 overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
                            <table className="w-full border-collapse">
                              <thead className="bg-slate-50 dark:bg-slate-800/50">
                                <tr>
                                  <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                                    Home
                                  </th>
                                  <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                                    Sortiment
                                  </th>
                                  <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                                    Tradition
                                  </th>
                                  <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                                    Maschinerie
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3">Home</td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3">All Products</td>
                                </tr>
                                <tr>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                  <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                </tr>
                                <tr>
                                  <td className="p-3"></td>
                                  <td className="p-3"></td>
                                  <td className="p-3"></td>
                                  <td className="p-3"></td>
                                </tr>
                              </tbody>
                            </table>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                              <CardContent className="p-0">
                                <div className="p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
                                  <h4 className="text-sm font-medium">Tags</h4>
                                  <Button variant="ghost" size="icon" className="h-7 w-7 rounded-full">
                                    <ChevronDown className="h-3.5 w-3.5" />
                                  </Button>
                                </div>
                                <table className="w-full border-collapse">
                                  <thead>
                                    <tr>
                                      <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                                        Tags
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {[...Array(8)].map((_, i) => (
                                      <tr key={i}>
                                        <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </CardContent>
                            </Card>

                            <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                              <CardContent className="p-0">
                                <div className="p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                  <h4 className="text-sm font-medium">Publish</h4>
                                </div>
                                <table className="w-full border-collapse">
                                  <tbody>
                                    {[...Array(4)].map((_, i) => (
                                      <tr key={i}>
                                        <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                        <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </CardContent>
                            </Card>

                            <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                              <CardContent className="p-0">
                                <div className="p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                  <h4 className="text-sm font-medium">Preise</h4>
                                </div>
                                <div className="p-3">
                                  <select className="w-full p-2 text-sm rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 mb-3">
                                    <option>DE - 19% Germany</option>
                                  </select>
                                  <table className="w-full border-collapse">
                                    <thead>
                                      <tr>
                                        <th className="border border-slate-200 dark:border-slate-700 p-2 text-left font-medium">
                                          Art
                                        </th>
                                        <th className="border border-slate-200 dark:border-slate-700 p-2 text-left font-medium">
                                          €
                                        </th>
                                        <th className="border border-slate-200 dark:border-slate-700 p-2 text-left font-medium">
                                          VE
                                        </th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      <tr>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">Laden</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">37,40 €</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">1</td>
                                      </tr>
                                      <tr>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">Handel</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">17,30 €</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">1</td>
                                      </tr>
                                      <tr>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">Empf.</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">29,50 €</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">1</td>
                                      </tr>
                                      <tr>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">Einkauf</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">9,63 €</td>
                                        <td className="border border-slate-200 dark:border-slate-700 p-2">1</td>
                                      </tr>
                                    </tbody>
                                  </table>
                                </div>
                              </CardContent>
                            </Card>
                          </div>

                          <div className="mb-8">
                            <h4 className="text-sm font-medium mb-2">Preisänderungen:</h4>
                            <textarea className="w-full border border-slate-200 dark:border-slate-700 rounded-md p-3 h-24 resize-none bg-slate-50 dark:bg-slate-800"></textarea>
                          </div>

                          <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                Malgruppe
                              </label>
                              <div className="md:col-span-3">
                                <Input className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800" />
                              </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                Malkosten
                              </label>
                              <div className="md:col-span-3 flex gap-3">
                                <Input
                                  defaultValue="0,00€"
                                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                                />
                                <Input
                                  defaultValue="0 CZK"
                                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                                />
                              </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                Selbstkosten
                              </label>
                              <div className="md:col-span-3">
                                <Input className="w-full md:w-1/3 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800" />
                              </div>
                            </div>
                          </div>
                        </div>
                      </TabsContent>
                      <TabsContent value="teile" className="p-0 m-0">
                        <TeileTab />
                      </TabsContent>
                      <TabsContent value="bilder" className="p-0 m-0">
                        <BilderTab />
                      </TabsContent>
                      <TabsContent value="gewogen" className="p-0 m-0">
                        <GewogenTab />
                      </TabsContent>
                      <TabsContent value="lagerorte" className="p-0 m-0">
                        <LagerorteTab />
                      </TabsContent>
                      <TabsContent value="umsatze" className="p-0 m-0">
                        <UmsatzeTab />
                      </TabsContent>
                      <TabsContent value="bewegungen" className="p-0 m-0">
                        <BewegungenTab />
                      </TabsContent>
                    </Tabs>
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

