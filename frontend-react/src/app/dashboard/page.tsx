"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import {
  BarChart3,
  Bell,
  ChevronDown,
  Edit,
  Globe,
  Grip,
  Home,
  Menu,
  Package,
  Save,
  Search,
  Settings,
  ShoppingCart,
  Star,
  Users,
  X,
} from "lucide-react"
import axios from "axios"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
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
  SidebarSeparator,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"

// API client setup
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050/api',
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Only run in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

interface WidgetProps {
  id: string;
  title: string | null;
  children: React.ReactNode;
  isEditMode: boolean;
  onDragStart: (e: React.DragEvent, id: string) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent, id: string) => void;
  onResizeStart: (id: string) => void;
  onResizeMove: (id: string, size: { width: number; height: number }) => void;
  onResizeEnd: (id: string, size: { width: number; height: number }) => void;
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
}: WidgetProps) => {
  const [isResizing, setIsResizing] = useState(false)
  const widgetRef = useRef<HTMLDivElement>(null)
  const resizeStartPos = useRef({ x: 0, y: 0 })
  const originalSize = useRef({ width: 0, height: 0 })

  const handleResizeStart = (e: React.MouseEvent) => {
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

  const handleResizeMove = (e: MouseEvent) => {
    if (!isResizing || !widgetRef.current) return

    const deltaX = e.clientX - resizeStartPos.current.x
    const deltaY = e.clientY - resizeStartPos.current.y

    const newWidth = originalSize.current.width + deltaX
    const newHeight = originalSize.current.height + deltaY

    widgetRef.current.style.width = `${newWidth}px`
    widgetRef.current.style.height = `${newHeight}px`

    onResizeMove && onResizeMove(id, { width: newWidth, height: newHeight })
  }

  const handleResizeEnd = () => {
    setIsResizing(false)
    if (widgetRef.current) {
      onResizeEnd &&
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

interface Widget {
  id: string;
  order: number;
  title: string | null;
}

interface RecentOrder {
  id: string;
  customer: string;
  date: string;
  status: string;
  amount: string;
}

interface RecentItem {
  id: string;
  name: string;
  type: string;
}

interface NewsItem {
  title: string;
  date: string;
  content: string;
}

export default function Dashboard() {
  const [language, setLanguage] = useState("Deutsch")
  const [isEditMode, setIsEditMode] = useState(false)
  const [widgets, setWidgets] = useState<Widget[]>([
    { id: "recent-orders", order: 1, title: "Letzte Bestellungen nach Liefertermin" },
    { id: "menu-tiles", order: 2, title: "Menü" },
    { id: "quick-links", order: 3, title: null },
    { id: "news-pinboard", order: 4, title: null },
  ])
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Recent orders data - will be fetched from API
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([])
  
  // Recent accessed items - will be fetched from API
  const [recentAccessed, setRecentAccessed] = useState<RecentItem[]>([])
  
  // Favorites - will be fetched from API
  const [favorites, setFavorites] = useState<RecentItem[]>([])

  // Menu tiles
  const menuTiles = [
    { name: "Kunden", icon: Users, route: "/customers" },
    { name: "Aufträge", icon: ShoppingCart, route: "/orders" },
    { name: "Produkte", icon: Package, route: "/products" },
    { name: "Berichte", icon: BarChart3, route: "/reports" },
    { name: "Einstellungen", icon: Settings, route: "/settings" },
    { name: "Benutzer", icon: Users, route: "/users" },
    { name: "Finanzen", icon: BarChart3, route: "/finance" },
    { name: "Lager", icon: Package, route: "/inventory" },
    { name: "Marketing", icon: Bell, route: "/marketing" },
    { name: "Support", icon: Users, route: "/support" },
    { name: "Dokumente", icon: Package, route: "/documents" },
    { name: "Dashboard", icon: Home, route: "/dashboard" },
  ]

  // Quick links
  const quickLinks = [
    { name: "Handbuch", url: "/manual" },
    { name: "Support-Ticket erstellen", url: "/support/new" },
    { name: "Schulungsvideos", url: "/training" },
    { name: "FAQ", url: "/faq" },
    { name: "Kontakt", url: "/contact" },
    { name: "Systemstatus", url: "/system-status" },
    { name: "Updates", url: "/updates" },
    { name: "Lizenzinformationen", url: "/license" },
    { name: "Datenschutz", url: "/privacy" },
    { name: "Impressum", url: "/imprint" },
  ]

  // News items - will be fetched from API
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [notes, setNotes] = useState("")

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // Kommentiere die API-Aufrufe aus, da sie noch nicht existieren
        /*
        // Fetch dashboard configuration
        const dashboardResponse = await api.get('/dashboard/');
        if (dashboardResponse.data && dashboardResponse.data.dashboard_modules) {
          setWidgets(dashboardResponse.data.dashboard_modules);
        }
        
        // Fetch recent orders
        const ordersResponse = await api.get('/sales/orders/', { params: { limit: 5 } });
        if (ordersResponse.data) {
          setRecentOrders(ordersResponse.data.map((order: any) => ({
            id: order.id,
            customer: order.customer_name,
            date: order.delivery_date,
            status: order.status,
            amount: `€${order.total.toFixed(2)}`
          })));
        }
        
        // Fetch recent accessed items
        const recentResponse = await api.get('/recent-items/');
        if (recentResponse.data) {
          setRecentAccessed(recentResponse.data);
        }
        
        // Fetch favorites
        const favoritesResponse = await api.get('/favorites/');
        if (favoritesResponse.data) {
          setFavorites(favoritesResponse.data);
        }
        
        // Fetch news items
        const newsResponse = await api.get('/news/');
        if (newsResponse.data) {
          setNewsItems(newsResponse.data);
        }
        
        // Fetch user notes
        const notesResponse = await api.get('/notes/');
        if (notesResponse.data && notesResponse.data.content) {
          setNotes(notesResponse.data.content);
        }
        */
        
        // Verwende direkt die Fallback-Daten
        setRecentOrders([
          { id: "ORD-7352", customer: "Müller GmbH", date: "2025-03-20", status: "Pending", amount: "€1,240.00" },
          { id: "ORD-7351", customer: "Schmidt AG", date: "2025-03-18", status: "Processing", amount: "€2,156.00" },
          { id: "ORD-7350", customer: "Weber KG", date: "2025-03-17", status: "Shipped", amount: "€865.50" },
          { id: "ORD-7349", customer: "Becker & Co.", date: "2025-03-15", status: "Delivered", amount: "€1,790.25" },
          { id: "ORD-7348", customer: "Fischer GmbH", date: "2025-03-12", status: "Delivered", amount: "€3,450.00" },
        ]);
        
        setRecentAccessed([
          { id: "KD-1234", name: "Müller GmbH", type: "Kunde" },
          { id: "ORD-7345", name: "Auftrag #7345", type: "Auftrag" },
          { id: "KD-1156", name: "Schmidt AG", type: "Kunde" },
          { id: "ORD-7340", name: "Auftrag #7340", type: "Auftrag" },
          { id: "KD-1089", name: "Weber KG", type: "Kunde" },
        ]);
        
        setFavorites([
          { id: "KD-1234", name: "Müller GmbH", type: "Kunde" },
          { id: "KD-1156", name: "Schmidt AG", type: "Kunde" },
          { id: "ORD-7340", name: "Auftrag #7340", type: "Auftrag" },
        ]);
        
        setNewsItems([
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
        ]);
        
        // Entferne den Fehler, da wir jetzt Daten haben
        setError(null);
        
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Save notes
  const saveNotes = async () => {
    try {
      await api.post('/notes/', { content: notes });
      // Show success message
    } catch (error) {
      console.error('Failed to save notes:', error);
      // Show error message
    }
  };

  // Handle drag and drop
  const handleDragStart = (e: React.DragEvent, id: string) => {
    setDraggedWidget(id)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent, targetId: string) => {
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

  const handleResizeMove = (id: string, size: { width: number; height: number }) => {
    // Could update state in real-time if needed
  }

  const handleResizeEnd = (id: string, size: { width: number; height: number }) => {
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
  }, [])

  // Render widget content based on ID
  const renderWidgetContent = (widgetId: string) => {
    switch (widgetId) {
      case "recent-orders":
        return (
          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center items-center p-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
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
              )}
            </CardContent>
          </Card>
        )

      case "menu-tiles":
        return (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {menuTiles.map((tile, index) => (
              <Link href={tile.route} key={index}>
                <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                  <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                    <tile.icon className="h-8 w-8 mb-2" />
                    <span className="text-sm font-medium">{tile.name}</span>
                  </CardContent>
                </Card>
              </Link>
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
                  {isLoading ? (
                    <div className="flex justify-center items-center p-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  ) : (
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
                  )}
                </TabsContent>
                <TabsContent value="notes">
                  <div className="flex flex-col gap-2">
                    <p className="text-sm text-muted-foreground">
                      Hier können Sie Ihre persönlichen Notizen hinzufügen.
                    </p>
                    <Textarea
                      className="min-h-[120px]"
                      placeholder="Notiz hinzufügen..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                    <Button className="self-end" onClick={saveNotes}>Speichern</Button>
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
      <div className="flex h-screen overflow-hidden">
        <Sidebar>
          <SidebarHeader>
            <div className="flex items-center gap-2 px-4">
              <Globe className="h-6 w-6" />
              <span className="font-bold">pyERP</span>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive>
                  <Link href="/dashboard">
                    <Home className="h-4 w-4 mr-2" />
                    Dashboard
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/customers">
                    <Users className="h-4 w-4 mr-2" />
                    Kunden
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/orders">
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Aufträge
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/products">
                    <Package className="h-4 w-4 mr-2" />
                    Produkte
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/reports">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Berichte
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/settings">
                    <Settings className="h-4 w-4 mr-2" />
                    Einstellungen
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>

            <SidebarSeparator />

            <SidebarGroup>
              <SidebarGroupLabel>Favoriten</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {favorites.map((item) => (
                    <SidebarMenuItem key={item.id}>
                      <SidebarMenuButton asChild>
                        <Link href="#">
                          <Star className="h-4 w-4 mr-2 text-yellow-400" />
                          {item.name}
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
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
                            <Users className="h-4 w-4 mr-2" />
                          ) : (
                            <ShoppingCart className="h-4 w-4 mr-2" />
                          )}
                          {item.name}
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarFooter>
            <div className="px-4 py-2 text-xs text-muted-foreground">
              pyERP v1.0.0
            </div>
          </SidebarFooter>
        </Sidebar>

        <div className="flex-1 overflow-auto">
          <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-6">
            <SidebarTrigger />
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Suchen..."
                  className="w-full max-w-[400px] pl-8"
                />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="icon">
                <Bell className="h-4 w-4" />
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="gap-2">
                    {language}
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setLanguage("Deutsch")}>
                    Deutsch
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLanguage("English")}>
                    English
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </header>

          <main className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
              <div className="flex gap-2">
                {isEditMode ? (
                  <>
                    <Button variant="outline" onClick={toggleEditMode}>
                      <X className="h-4 w-4 mr-2" />
                      Abbrechen
                    </Button>
                    <Button onClick={saveLayout}>
                      <Save className="h-4 w-4 mr-2" />
                      Speichern
                    </Button>
                  </>
                ) : (
                  <Button variant="outline" onClick={toggleEditMode}>
                    <Edit className="h-4 w-4 mr-2" />
                    Anpassen
                  </Button>
                )}
              </div>
            </div>

            {error && (
              <div className="bg-destructive/15 text-destructive px-4 py-3 rounded-md mb-6">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 gap-6">
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

