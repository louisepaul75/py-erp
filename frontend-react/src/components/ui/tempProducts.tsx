"use client"

// Next.js 15 - Inventory Management System

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Plus,
  Minus,
  FileText,
  Settings,
  Search,
  Eye,
  Menu,
  X,
  Filter,
  ArrowUpDown,
  MoreHorizontal,
  ChevronRight,
  ChevronLeft,
  Home,
  Package,
  BarChart2,
  Users,
  Database,
  Truck,
  ShoppingCart,
  Inbox,
  Bell,
  HelpCircle,
  Sun,
  Moon,
  Zap,
  Sliders,
  Bookmark,
  Tag,
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
  const [darkMode, setDarkMode] = useState(false)
  const [sidebarExpanded, setSidebarExpanded] = useState(true)

  const products = [
    { nummer: "307967", bezeichnung: "", status: "active" },
    { nummer: "132355", bezeichnung: "", status: "inactive" },
    { nummer: "-1", bezeichnung: "", status: "draft" },
    { nummer: "912859", bezeichnung: '"Adler"-Erste Eisenbahn', status: "active" },
    { nummer: "218300", bezeichnung: '"Adler"-Lock', status: "active" },
    { nummer: "310048", bezeichnung: '"Adler"-Tender', status: "active" },
    { nummer: "411430", bezeichnung: '"Adler"-Wagen', status: "active" },
    { nummer: "409129", bezeichnung: '"Adler"-Wagen-offen', status: "active" },
    { nummer: "300251", bezeichnung: '"Adler"-Wagen/Führer', status: "active" },
    { nummer: "922678", bezeichnung: "100-0", status: "inactive" },
    { nummer: "325473", bezeichnung: "100-0/3", status: "active" },
    { nummer: "530620", bezeichnung: "100-0/5", status: "active" },
    { nummer: "921063", bezeichnung: "1x Saugnapf für Glasscheibe Vitrine", status: "active" },
    { nummer: "903786", bezeichnung: "22 Zoll Display Sichtschutz Bildschirm", status: "active" },
    { nummer: "718205", bezeichnung: "27 Zoll Display Sichtschutz Bildschirm", status: "active" },
    { nummer: "701703", bezeichnung: "5x BelegDrucker Rollen", status: "active" },
    { nummer: "831738", bezeichnung: "7 miniatur Hasen in drei Teile", status: "active" },
    { nummer: "309069", bezeichnung: "7 Schwaben mit Hase", status: "active" },
    { nummer: "811140", bezeichnung: "80-2", status: "active" },
    { nummer: "304527", bezeichnung: "80-4", status: "active" },
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

  useEffect(() => {
    // Check system preference for dark mode
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setDarkMode(true)
      document.documentElement.classList.add("dark")
    }
  }, [])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50"
      case "inactive":
        return "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400 border-amber-200 dark:border-amber-900/50"
      case "draft":
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700"
      default:
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700"
    }
  }

  return (
    <div className={`min-h-screen ${darkMode ? "dark" : ""}`}>
      <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
        {/* Main Sidebar */}
        <div
          className={`${sidebarExpanded ? "w-64" : "w-20"} bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-all duration-300 ease-in-out z-20 ${showSidebar ? "" : "hidden md:flex"}`}
        >
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold mr-2">
                IM
              </div>
              {sidebarExpanded && <span className="font-semibold text-lg">Inventory</span>}
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              onClick={() => setSidebarExpanded(!sidebarExpanded)}
            >
              {sidebarExpanded ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto py-4">
            <div className="px-3 mb-6">
              <Button className="w-full justify-start gap-3 bg-blue-50 hover:bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 dark:text-blue-400 h-11 rounded-xl">
                <Package className="h-5 w-5" />
                {sidebarExpanded && <span>Produkte</span>}
              </Button>
            </div>
            <div className="px-3 space-y-1">
              {sidebarExpanded && (
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2 ml-3">MENÜ</p>
              )}
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <Home className="h-5 w-5" />
                {sidebarExpanded && <span>Dashboard</span>}
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <BarChart2 className="h-5 w-5" />
                {sidebarExpanded && <span>Berichte</span>}
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <Users className="h-5 w-5" />
                {sidebarExpanded && <span>Kunden</span>}
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <ShoppingCart className="h-5 w-5" />
                {sidebarExpanded && <span>Bestellungen</span>}
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <Truck className="h-5 w-5" />
                {sidebarExpanded && <span>Lieferungen</span>}
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
              >
                <Database className="h-5 w-5" />
                {sidebarExpanded && <span>Lager</span>}
              </Button>
            </div>
          </div>

          {/* User */}
          <div className="border-t border-slate-200 dark:border-slate-800 p-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                  JD
                </AvatarFallback>
              </Avatar>
              {sidebarExpanded && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">John Doe</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate">admin@example.com</p>
                </div>
              )}
              {sidebarExpanded && (
                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 lg:px-6">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden h-9 w-9 rounded-full"
                onClick={() => setShowSidebar(!showSidebar)}
              >
                {showSidebar ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              <h1 className="text-xl font-semibold hidden md:block">Produktverwaltung</h1>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative hidden md:block">
                <Input
                  className="w-64 pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
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
              <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full" onClick={toggleDarkMode}>
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
              <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500"></span>
              </Button>
              <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
                <HelpCircle className="h-5 w-5" />
              </Button>
              <Separator orientation="vertical" className="h-8 bg-slate-200 dark:bg-slate-700" />
              <Button className="rounded-full bg-blue-600 hover:bg-blue-700 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Neues Produkt
              </Button>
            </div>
          </header>

          {/* Main Content Area */}
          <div className="flex-1 flex">
            {/* Product List Sidebar */}
            {showSidebar && (
              <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
                {/* Search and Filters */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800">
                  <div className="relative md:hidden mb-4">
                    <Input
                      className="w-full pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
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
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-medium text-slate-900 dark:text-slate-100">Produkte</h2>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                        <Filter className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                        <ArrowUpDown className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                        <Sliders className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Product List */}
                <div className="flex-1 overflow-auto">
                  {filteredProducts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                      <Inbox className="h-12 w-12 text-slate-300 dark:text-slate-600 mb-2" />
                      <p className="text-sm text-slate-500 dark:text-slate-400">Keine Produkte gefunden</p>
                      <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                        Versuchen Sie, Ihre Suchkriterien zu ändern
                      </p>
                    </div>
                  ) : (
                    <div className="p-2">
                      {filteredProducts.map((product) => (
                        <div
                          key={product.nummer}
                          className={`p-3 my-1 rounded-xl cursor-pointer transition-all ${
                            selectedItem === product.nummer
                              ? "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500"
                              : "hover:bg-slate-50 dark:hover:bg-slate-800/50 border-l-4 border-transparent"
                          }`}
                          onClick={() => setSelectedItem(product.nummer)}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="font-medium">{product.nummer}</div>
                            <Badge
                              variant="outline"
                              className={`text-xs px-2 py-0 h-5 ${getStatusColor(product.status)}`}
                            >
                              {product.status === "active"
                                ? "Aktiv"
                                : product.status === "inactive"
                                  ? "Inaktiv"
                                  : "Entwurf"}
                            </Badge>
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400 truncate">
                            {product.bezeichnung || "—"}
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge
                              variant="secondary"
                              className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                            >
                              <Tag className="h-3 w-3 mr-1" />
                              Zinnfigur
                            </Badge>
                            <Badge
                              variant="secondary"
                              className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                            >
                              <Bookmark className="h-3 w-3 mr-1" />
                              Eisenbahn
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Product Detail */}
            <div className="flex-1 bg-slate-50 dark:bg-slate-950 flex flex-col">
              {/* Mutter/Varianten Tabs (Sticky Header for Detail Area) */}
              <div className="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 lg:px-6">
                <div className="flex items-center h-14">
                  <Button
                    variant={activeTab === "mutter" ? "default" : "ghost"}
                    className={`rounded-full ${activeTab === "mutter" ? "bg-blue-600 text-white hover:bg-blue-700" : ""}`}
                    onClick={() => setActiveTab("mutter")}
                  >
                    Mutter
                  </Button>
                  <Button
                    variant={activeTab === "varianten" ? "default" : "ghost"}
                    className={`rounded-full ml-2 ${activeTab === "varianten" ? "bg-blue-600 text-white hover:bg-blue-700" : ""}`}
                    onClick={() => setActiveTab("varianten")}
                  >
                    Varianten
                  </Button>
                  <div className="ml-auto flex items-center gap-2">
                    <Button variant="outline" size="sm" className="rounded-full">
                      <Eye className="h-4 w-4 mr-1" />
                      Vorschau
                    </Button>
                    <Button variant="outline" size="sm" className="rounded-full">
                      <FileText className="h-4 w-4 mr-1" />
                      Exportieren
                    </Button>
                    <Button variant="outline" size="sm" className="rounded-full">
                      <Settings className="h-4 w-4 mr-1" />
                      Einstellungen
                    </Button>
                  </div>
                </div>
              </div>

              {/* Tab Content - Wrapped in a new scrollable div */}
              <div className="flex-1 overflow-auto">
                {activeTab === "mutter" ? (
                  <div className="p-4 lg:p-6">
                    <div className="max-w-5xl mx-auto space-y-8">
                      {/* Header with Product Info */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-6">
                          <div className="h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">
                            AL
                          </div>
                          <div className="flex-1">
                            <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
                              <h1 className="text-2xl font-bold">"Adler"-Lock</h1>
                              <Badge className="w-fit bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50">
                                Aktiv
                              </Badge>
                            </div>
                            <p className="text-slate-500 dark:text-slate-400 mt-1">Artikelnummer: 218300</p>
                          </div>
                          <div className="flex flex-col sm:flex-row gap-2 md:justify-end">
                            <Button variant="outline" className="rounded-full">
                              <Minus className="h-4 w-4 mr-2" />
                              Löschen
                            </Button>
                            <Button className="rounded-full bg-blue-600 hover:bg-blue-700 text-white">
                              <Zap className="h-4 w-4 mr-2" />
                              Speichern
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Bezeichnung & Beschreibung */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <h2 className="text-lg font-semibold mb-4">Produktdetails</h2>
                        <div className="space-y-6">
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                              Bezeichnung
                            </label>
                            <div className="md:col-span-3">
                              <Input
                                defaultValue="&quot;Adler&quot;-Lock"
                                className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                              Beschreibung
                            </label>
                            <div className="md:col-span-3">
                              <textarea
                                className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-sm min-h-[150px] resize-none bg-slate-50 dark:bg-slate-800"
                                defaultValue="Erleben Sie die Eleganz und den Charme vergangener Zeiten mit dieser exquisiten Zinnfigur, inspiriert von den Anfängen der Eisenbahngeschichte. Perfekt für Sammler und Liebhaber von Nostalgie, zeigt diese Figur einen klassischen Lokführer, gekleidet in traditioneller Montur, der stolz seine Maschine lenkt. Ideal für jede Vitrine oder als geschmackvolles Geschenk. Eine Hommage an die Ingenieurskunst und das kulturelle Erbe."
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Maße */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between mb-4">
                          <h2 className="text-lg font-semibold">Maße & Eigenschaften</h2>
                          <Badge
                            variant="outline"
                            className="text-xs font-normal px-2 py-0.5 h-5 border-slate-200 dark:border-slate-700"
                          >
                            Einheit: mm
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Breite</label>
                            <Input
                              defaultValue="7"
                              className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            />
                          </div>
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Höhe</label>
                            <Input
                              defaultValue="7"
                              className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            />
                          </div>
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Tiefe</label>
                            <Input
                              defaultValue="0,7"
                              className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            />
                          </div>
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Gewicht (g)</label>
                            <Input
                              defaultValue="30"
                              className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
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
                        <div className="mt-6">
                          <div className="flex items-center gap-2">
                            <label className="text-sm font-medium text-slate-500 dark:text-slate-400 w-24">
                              Boxgröße
                            </label>
                            <Input
                              defaultValue="B5"
                              className="w-32 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Kategorien */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between mb-4">
                          <h2 className="text-lg font-semibold">Kategorien</h2>
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
                  <div className="p-4 lg:p-6">
                    <div className="max-w-5xl mx-auto space-y-8">
                      {/* Varianten Header */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div>
                            <h2 className="text-lg font-semibold">Varianten</h2>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                              Verwalten Sie verschiedene Ausführungen dieses Produkts
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm" className="h-9 rounded-full">
                              <Plus className="h-4 w-4 mr-1" />
                              <span>Hinzufügen</span>
                            </Button>
                            <Button variant="outline" size="sm" className="h-9 rounded-full">
                              <Minus className="h-4 w-4 mr-1" />
                              <span>Entfernen</span>
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Varianten Table */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
                        <div className="overflow-x-auto">
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
                      </div>

                      {/* Varianten Tabs */}
                      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
                        <Tabs
                          defaultValue="details"
                          value={variantenActiveTab}
                          onValueChange={setVariantenActiveTab}
                          className="w-full"
                        >
                          <div className="border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
                            <TabsList className="bg-slate-50 dark:bg-slate-800/50 h-auto p-2 rounded-none flex-nowrap">
                              <TabsTrigger
                                value="details"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Details
                              </TabsTrigger>
                              <TabsTrigger
                                value="teile"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Teile
                              </TabsTrigger>
                              <TabsTrigger
                                value="bilder"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Bilder
                              </TabsTrigger>
                              <TabsTrigger
                                value="gewogen"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Gewogen
                              </TabsTrigger>
                              <TabsTrigger
                                value="lagerorte"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Lagerorte
                              </TabsTrigger>
                              <TabsTrigger
                                value="umsatze"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Umsätze
                              </TabsTrigger>
                              <TabsTrigger
                                value="bewegungen"
                                className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                              >
                                Bewegungen
                              </TabsTrigger>
                            </TabsList>
                          </div>

                          <TabsContent value="details" className="p-0 m-0">
                            <div className="p-6">
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                                <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                                  <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                    <CardTitle className="text-sm font-medium">Tags</CardTitle>
                                  </CardHeader>
                                  <CardContent className="p-0">
                                    <div className="p-4">
                                      <div className="flex flex-wrap gap-2 mb-4">
                                        <Badge
                                          variant="secondary"
                                          className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                                        >
                                          <Tag className="h-3 w-3 mr-1" />
                                          Zinnfigur
                                        </Badge>
                                        <Badge
                                          variant="secondary"
                                          className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                                        >
                                          <Tag className="h-3 w-3 mr-1" />
                                          Eisenbahn
                                        </Badge>
                                        <Badge
                                          variant="secondary"
                                          className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                                        >
                                          <Tag className="h-3 w-3 mr-1" />
                                          Sammler
                                        </Badge>
                                      </div>
                                      <Button variant="outline" size="sm" className="w-full rounded-lg">
                                        <Plus className="h-3.5 w-3.5 mr-1" />
                                        Tag hinzufügen
                                      </Button>
                                    </div>
                                  </CardContent>
                                </Card>

                                <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                                  <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                    <CardTitle className="text-sm font-medium">Publish</CardTitle>
                                  </CardHeader>
                                  <CardContent className="p-4">
                                    <div className="space-y-3">
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Status</span>
                                        <Badge className="bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                                          Aktiv
                                        </Badge>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Sichtbarkeit</span>
                                        <Badge className="bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                                          Öffentlich
                                        </Badge>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Erstellt am</span>
                                        <span className="text-sm">01.01.2023</span>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Aktualisiert am</span>
                                        <span className="text-sm">22.10.2024</span>
                                      </div>
                                    </div>
                                  </CardContent>
                                </Card>

                                <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                                  <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                    <CardTitle className="text-sm font-medium">Preise</CardTitle>
                                  </CardHeader>
                                  <CardContent className="p-4">
                                    <select className="w-full p-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 mb-3">
                                      <option>DE - 19% Germany</option>
                                    </select>
                                    <div className="space-y-3">
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Laden</span>
                                        <span className="text-sm font-medium">37,40 €</span>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Handel</span>
                                        <span className="text-sm font-medium">17,30 €</span>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Empf.</span>
                                        <span className="text-sm font-medium">29,50 €</span>
                                      </div>
                                      <div className="flex justify-between items-center">
                                        <span className="text-sm">Einkauf</span>
                                        <span className="text-sm font-medium">9,63 €</span>
                                      </div>
                                    </div>
                                  </CardContent>
                                </Card>
                              </div>

                              <Card className="border border-slate-200 dark:border-slate-700 shadow-sm mb-6">
                                <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                  <CardTitle className="text-sm font-medium">Preisänderungen</CardTitle>
                                </CardHeader>
                                <CardContent className="p-4">
                                  <textarea className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 h-24 resize-none bg-slate-50 dark:bg-slate-800"></textarea>
                                </CardContent>
                              </Card>

                              <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                                <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                                  <CardTitle className="text-sm font-medium">Zusätzliche Informationen</CardTitle>
                                </CardHeader>
                                <CardContent className="p-4">
                                  <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                                      <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                        Malgruppe
                                      </label>
                                      <div className="md:col-span-3">
                                        <Input className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg" />
                                      </div>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                                      <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                        Malkosten
                                      </label>
                                      <div className="md:col-span-3 flex gap-3">
                                        <Input
                                          defaultValue="0,00€"
                                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                                        />
                                        <Input
                                          defaultValue="0 CZK"
                                          className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                                        />
                                      </div>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                                      <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                        Selbstkosten
                                      </label>
                                      <div className="md:col-span-3">
                                        <Input className="w-full md:w-1/3 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg" />
                                      </div>
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
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
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

