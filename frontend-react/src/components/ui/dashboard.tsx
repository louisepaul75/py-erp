"use client"

import { useEffect, useRef, useState, MouseEvent, DragEvent } from "react"
import Link from "next/link"
import {
  BarChart3,
  Bell,
  Edit,
  Grip,
  Home,
  Menu,
  Package,
  Save,
  Settings,
  ShoppingCart,
  Star,
  Users,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Custom sidebar toggle that's always visible
const AlwaysVisibleSidebarToggle = () => {
  const { state, toggleSidebar } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <Button
      variant="outline"
      size="icon"
      className="fixed top-4 left-4 z-50 h-10 w-10 rounded-full shadow-md bg-background"
      onClick={toggleSidebar}
      style={{ display: isCollapsed ? "flex" : "none" }}
    >
      <Menu className="h-4 w-4" />
      <span className="sr-only">Seitenleiste einblenden</span>
    </Button>
  )
}

interface WidgetSize {
  width: number;
  height: number;
}

interface DashboardWidgetProps {
  id: string;
  title: string | null;
  children: React.ReactNode;
  isEditMode: boolean;
  onDragStart: (e: DragEvent<HTMLDivElement>, id: string) => void;
  onDragOver: (e: DragEvent<HTMLDivElement>) => void;
  onDrop: (e: DragEvent<HTMLDivElement>, id: string) => void;
  onResizeStart?: (id: string) => void;
  onResizeMove?: (id: string, size: WidgetSize) => void;
  onResizeEnd?: (id: string, size: WidgetSize) => void;
}

// Dashboard widget component
const DashboardWidget = ({
  id,
  title,
  children,
  isEditMode,
  onDragStart,
  onDragOver,
  onDrop,
  onResizeStart,
  onResizeMove,
  onResizeEnd,
}: DashboardWidgetProps) => {
  const [isResizing, setIsResizing] = useState(false)
  const widgetRef = useRef<HTMLDivElement | null>(null)
  const resizeStartPos = useRef({ x: 0, y: 0 })
  const originalSize = useRef({ width: 0, height: 0 })

  const handleResizeStart = (e: MouseEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsResizing(true)
    resizeStartPos.current = { x: e.clientX, y: e.clientY }
    if (widgetRef.current) {
      originalSize.current = {
        width: widgetRef.current.offsetWidth,
        height: widgetRef.current.offsetHeight,
      }
    }
    onResizeStart && onResizeStart(id)

    // Add event listeners for resize
    document.addEventListener("mousemove", handleResizeMove)
    document.addEventListener("mouseup", handleResizeEnd)
  }

  const handleResizeMove = (e: MouseEvent | any) => {
    if (!isResizing) return

    const deltaX = e.clientX - resizeStartPos.current.x
    const deltaY = e.clientY - resizeStartPos.current.y

    const newWidth = originalSize.current.width + deltaX
    const newHeight = originalSize.current.height + deltaY

    if (widgetRef.current) {
      widgetRef.current.style.width = `${newWidth}px`
      widgetRef.current.style.height = `${newHeight}px`
    }

    onResizeMove && onResizeMove(id, { width: newWidth, height: newHeight })
  }

  const handleResizeEnd = () => {
    setIsResizing(false)
    if (widgetRef.current && onResizeEnd) {
      onResizeEnd(id, {
        width: widgetRef.current.offsetWidth,
        height: widgetRef.current.offsetHeight,
      })
    }

    // Remove event listeners
    document.removeEventListener("mousemove", handleResizeMove)
    document.removeEventListener("mouseup", handleResizeEnd)
  }

  useEffect(() => {
    return () => {
      document.removeEventListener("mousemove", handleResizeMove)
      document.removeEventListener("mouseup", handleResizeEnd)
    }
  }, [])

  return (
    <div
      ref={widgetRef}
      id={id}
      className={`relative mb-6 transition-all ${isEditMode ? "border-2 border-dashed border-primary cursor-move" : ""}`}
      draggable={isEditMode}
      onDragStart={(e) => onDragStart(e, id)}
      onDragOver={(e) => onDragOver(e)}
      onDrop={(e) => onDrop(e, id)}
    >
      {isEditMode && (
        <div className="absolute -top-3 -left-3 bg-primary text-primary-foreground rounded-full p-1 z-10">
          <Grip className="h-4 w-4" />
        </div>
      )}

      {title && <h2 className="text-2xl font-bold tracking-tight mb-4">{title}</h2>}
      {children}

      {isEditMode && (
        <div
          className="absolute bottom-0 right-0 w-6 h-6 bg-primary cursor-se-resize z-10"
          onMouseDown={handleResizeStart}
        />
      )}
    </div>
  )
}

// Define types for menu tiles
interface MenuTile {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  favorited: boolean;
}

// Define types for orders
interface Order {
  id: string;
  customer: string;
  date: string;
  status: string;
  amount: string;
}

// Define types for recent accessed items
interface RecentItem {
  id: string;
  name: string;
  type: string;
}

// Define types for quick links
interface QuickLink {
  name: string;
  url: string;
}

// Define types for news items
interface NewsItem {
  title: string;
  date: string;
  content: string;
}

// Define types for widgets
interface Widget {
  id: string;
  order: number;
  title: string | null;
}

export default function Dashboard() {
  const [isEditMode, setIsEditMode] = useState(false)
  const [widgets, setWidgets] = useState<Widget[]>([
    { id: "recent-orders", order: 1, title: "Letzte Bestellungen nach Liefertermin" },
    { id: "menu-tiles", order: 2, title: "Menü" },
    { id: "quick-links", order: 3, title: null },
    { id: "news-pinboard", order: 4, title: null },
  ])
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null)

  // Recent orders data
  const recentOrders: Order[] = [
    { id: "ORD-7352", customer: "Müller GmbH", date: "2025-03-20", status: "Pending", amount: "€1,240.00" },
    { id: "ORD-7351", customer: "Schmidt AG", date: "2025-03-18", status: "Processing", amount: "€2,156.00" },
    { id: "ORD-7350", customer: "Weber KG", date: "2025-03-17", status: "Shipped", amount: "€865.50" },
    { id: "ORD-7349", customer: "Becker & Co.", date: "2025-03-15", status: "Delivered", amount: "€1,790.25" },
    { id: "ORD-7348", customer: "Fischer GmbH", date: "2025-03-12", status: "Delivered", amount: "€3,450.00" },
  ]

  // Recent accessed items
  const recentAccessed: RecentItem[] = [
    { id: "KD-1234", name: "Müller GmbH", type: "Kunde" },
    { id: "ORD-7345", name: "Auftrag #7345", type: "Auftrag" },
    { id: "KD-1156", name: "Schmidt AG", type: "Kunde" },
    { id: "ORD-7340", name: "Auftrag #7340", type: "Auftrag" },
    { id: "KD-1089", name: "Weber KG", type: "Kunde" },
  ]

  const [menuTiles, setMenuTiles] = useState<MenuTile[]>([
    { id: "customers", name: "Kunden", icon: Users, favorited: false },
    { id: "orders", name: "Aufträge", icon: ShoppingCart, favorited: false },
    { id: "products", name: "Produkte", icon: Package, favorited: false },
    { id: "reports", name: "Berichte", icon: BarChart3, favorited: false },
    { id: "settings", name: "Einstellungen", icon: Settings, favorited: false },
    { id: "users", name: "Benutzer", icon: Users, favorited: false },
    { id: "finance", name: "Finanzen", icon: BarChart3, favorited: false },
    { id: "inventory", name: "Lager", icon: Package, favorited: false },
    { id: "marketing", name: "Marketing", icon: Bell, favorited: false },
    { id: "support", name: "Support", icon: Users, favorited: false },
    { id: "documents", name: "Dokumente", icon: Package, favorited: false },
    { id: "dashboard", name: "Dashboard", icon: Home, favorited: false },
  ])

  // Quick links
  const quickLinks: QuickLink[] = [
    { name: "Handbuch", url: "#" },
    { name: "Support-Ticket erstellen", url: "#" },
    { name: "Schulungsvideos", url: "#" },
    { name: "FAQ", url: "#" },
    { name: "Kontakt", url: "#" },
    { name: "Systemstatus", url: "#" },
    { name: "Updates", url: "#" },
    { name: "Lizenzinformationen", url: "#" },
    { name: "Datenschutz", url: "#" },
    { name: "Impressum", url: "#" },
  ]

  // News items
  const newsItems: NewsItem[] = [
    {
      title: "Neue Funktionen im ERP-System",
      date: "15.03.2025",
      content: "Wir haben neue Funktionen für die Berichterstellung hinzugefügt.",
    },
    {
      title: "Wartungsarbeiten am 25.03",
      date: "12.03.2025",
      content: "Das System wird von 22:00 bis 23:00 Uhr nicht verfügbar sein.",
    },
    {
      title: "Neue Schulungsvideos verfügbar",
      date: "10.03.2025",
      content: "Schauen Sie sich unsere neuen Schulungsvideos an.",
    },
  ]

  // Handle drag and drop
  const handleDragStart = (e: DragEvent<HTMLDivElement>, id: string) => {
    setDraggedWidget(id)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>, targetId: string) => {
    e.preventDefault()

    if (draggedWidget === targetId) return

    const updatedWidgets = [...widgets]
    const draggedWidgetIndex = updatedWidgets.findIndex((w) => w.id === draggedWidget)
    const targetWidgetIndex = updatedWidgets.findIndex((w) => w.id === targetId)

    // Swap the order values
    const draggedOrder = updatedWidgets[draggedWidgetIndex].order
    updatedWidgets[draggedWidgetIndex].order = updatedWidgets[targetWidgetIndex].order
    updatedWidgets[targetWidgetIndex].order = draggedOrder

    // Sort by order
    updatedWidgets.sort((a, b) => a.order - b.order)

    setWidgets(updatedWidgets)
    setDraggedWidget(null)
  }

  // Handle resize
  const handleResizeStart = (id: string) => {
    // Could add specific logic here if needed
  }

  const handleResizeMove = (id: string, size: WidgetSize) => {
    // Could update state in real-time if needed
  }

  const handleResizeEnd = (id: string, size: WidgetSize) => {
    // Save the new size to localStorage or state
    console.log(`Widget ${id} resized to:`, size)
  }

  // Toggle edit mode
  const toggleEditMode = () => {
    setIsEditMode(!isEditMode)
  }

  // Save layout
  const saveLayout = () => {
    // Here you would typically save the layout to localStorage or a backend
    localStorage.setItem("dashboard-layout", JSON.stringify(widgets))
    setIsEditMode(false)
  }

  const toggleFavorite = (id: string) => {
    const updatedTiles = menuTiles.map((tile) => (tile.id === id ? { ...tile, favorited: !tile.favorited } : tile))
    setMenuTiles(updatedTiles)
    localStorage.setItem("dashboard-favorites", JSON.stringify(updatedTiles))
  }

  // Load saved layout on initial render
  useEffect(() => {
    const savedLayout = localStorage.getItem("dashboard-layout")
    if (savedLayout) {
      try {
        const parsedLayout = JSON.parse(savedLayout)
        setWidgets(parsedLayout)
      } catch (error) {
        console.error("Failed to parse saved layout", error)
      }
    }

    const savedFavorites = localStorage.getItem("dashboard-favorites")
    if (savedFavorites) {
      try {
        const parsedFavorites = JSON.parse(savedFavorites)
        setMenuTiles(parsedFavorites)
      } catch (error) {
        console.error("Failed to parse saved favorites", error)
      }
    }
  }, [])

  // Render widget content based on ID
  const renderWidgetContent = (widgetId: string) => {
    switch (widgetId) {
      case "recent-orders":
        return (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bestellung</TableHead>
                    <TableHead>Kunde</TableHead>
                    <TableHead>Liefertermin</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Betrag</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentOrders.map((order) => (
                    <TableRow key={order.id}>
                      <TableCell className="font-medium">{order.id}</TableCell>
                      <TableCell>{order.customer}</TableCell>
                      <TableCell>{order.date}</TableCell>
                      <TableCell>{order.status}</TableCell>
                      <TableCell className="text-right">{order.amount}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )

      case "menu-tiles":
        return (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {menuTiles.map((tile) => (
              <Card key={tile.id} className="hover:bg-muted/50 transition-colors cursor-pointer relative">
                <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                  <tile.icon className="h-8 w-8 mb-2" />
                  <span className="text-sm font-medium">{tile.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(tile.id)
                    }}
                    className="absolute top-2 right-2 text-muted-foreground hover:text-yellow-400"
                  >
                    <Star className={`h-4 w-4 ${tile.favorited ? "fill-yellow-400 text-yellow-400" : ""}`} />
                    <span className="sr-only">Zu Favoriten {tile.favorited ? "entfernen" : "hinzufügen"}</span>
                  </button>
                </CardContent>
              </Card>
            ))}
          </div>
        )

      case "quick-links":
        return (
          <Card>
            <CardHeader>
              <CardTitle>Schnellzugriff</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {quickLinks.map((link, index) => (
                  <Link key={index} href={link.url} className="text-sm text-primary hover:underline">
                    {link.name}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )

      case "news-pinboard":
        return (
          <Card>
            <CardHeader>
              <CardTitle>Pinnwand</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="news">
                <TabsList className="mb-4">
                  <TabsTrigger value="news">News</TabsTrigger>
                  <TabsTrigger value="notes">Notizen</TabsTrigger>
                </TabsList>
                <TabsContent value="news">
                  <div className="space-y-4">
                    {newsItems.map((item, index) => (
                      <div key={index} className="border-b pb-3 last:border-0 last:pb-0">
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="font-medium">{item.title}</h3>
                          <span className="text-xs text-muted-foreground">{item.date}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </TabsContent>
                <TabsContent value="notes">
                  <div className="flex flex-col gap-2">
                    <p className="text-sm text-muted-foreground">
                      Hier können Sie Ihre persönlichen Notizen hinzufügen.
                    </p>
                    <textarea
                      className="min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="Notiz hinzufügen..."
                    />
                    <Button className="self-end">Speichern</Button>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen flex-col">
        <div className="flex flex-1 relative">
          {/* Custom always-visible sidebar toggle */}
          <AlwaysVisibleSidebarToggle />

          {/* Sidebar */}
          <Sidebar>
            <SidebarHeader>
              <div className="flex items-center justify-between px-2 py-2">
                <div className="flex items-center gap-2">
                  <SidebarTrigger className="flex md:flex" />
                  <Link href="#" className="flex items-center gap-2 font-semibold">
                    <Package className="h-6 w-6" />
                    <span>ERP System</span>
                  </Link>
                </div>
              </div>
              <div className="px-2 pb-2">
                <Input type="search" placeholder="Suchen..." className="h-9" />
              </div>
            </SidebarHeader>

            <SidebarContent>
              <SidebarGroup>
                <SidebarGroupLabel>Favoriten</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {menuTiles.filter((tile) => tile.favorited).length > 0 ? (
                      menuTiles
                        .filter((tile) => tile.favorited)
                        .map((item) => (
                          <SidebarMenuItem key={item.id}>
                            <SidebarMenuButton asChild>
                              <Link href="#">
                                <item.icon className="h-4 w-4" />
                                <span>{item.name}</span>
                              </Link>
                            </SidebarMenuButton>
                          </SidebarMenuItem>
                        ))
                    ) : (
                      <div className="px-2 py-1 text-sm text-muted-foreground">
                        Keine Favoriten vorhanden. Klicken Sie auf den Stern bei einem Menüpunkt, um ihn zu den
                        Favoriten hinzuzufügen.
                      </div>
                    )}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>

              <SidebarGroup>
                <SidebarGroupLabel>Zuletzt aufgerufen</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {recentAccessed.map((item) => (
                      <SidebarMenuItem key={item.id}>
                        <SidebarMenuButton asChild>
                          <Link href="#">
                            {item.type === "Kunde" ? (
                              <Users className="h-4 w-4" />
                            ) : (
                              <ShoppingCart className="h-4 w-4" />
                            )}
                            <span>{item.name}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            </SidebarContent>

            <SidebarFooter>
              <div className="p-2">
                <Button variant="outline" className="w-full">
                  <Settings className="mr-2 h-4 w-4" />
                  Einstellungen
                </Button>
              </div>
            </SidebarFooter>
          </Sidebar>

          {/* Main Content */}
          <main className="flex-1 overflow-auto p-4 md:p-6 relative">
            {/* Floating Edit Button */}
            <div className="absolute top-4 right-4 z-10 flex gap-2">
              {isEditMode ? (
                <>
                  <Button variant="outline" size="sm" onClick={saveLayout}>
                    <Save className="h-4 w-4 mr-2" />
                    Speichern
                  </Button>
                  <Button variant="ghost" size="sm" onClick={toggleEditMode}>
                    <X className="h-4 w-4 mr-2" />
                    Abbrechen
                  </Button>
                </>
              ) : (
                <Button variant="outline" size="sm" onClick={toggleEditMode}>
                  <Edit className="h-4 w-4 mr-2" />
                  Bearbeiten
                </Button>
              )}
            </div>

            <div className="grid gap-6 pt-10">
              {/* Render widgets in their order */}
              {widgets
                .sort((a, b) => a.order - b.order)
                .map((widget) => (
                  <DashboardWidget
                    key={widget.id}
                    id={widget.id}
                    title={widget.title}
                    isEditMode={isEditMode}
                    onDragStart={handleDragStart}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    onResizeStart={handleResizeStart}
                    onResizeMove={handleResizeMove}
                    onResizeEnd={handleResizeEnd}
                  >
                    {renderWidgetContent(widget.id)}
                  </DashboardWidget>
                ))}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}

