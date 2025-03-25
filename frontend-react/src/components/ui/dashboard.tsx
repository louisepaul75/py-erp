"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import {
  Calendar,
  Mail,
  User,
  Home,
  BarChart,
  Users,
  X,
  Search,
  RotateCcw,
  Eye,
  Plus,
  ChevronDown,
  ChevronUp,
  Maximize,
  Minimize,
  ShoppingCart,
  Package,
  BarChart3,
  Settings,
  Bell,
  Star,
  Edit,
  Menu,
  Grip,
  Save,
} from "lucide-react"
import { Responsive as ResponsiveGridLayout, Layout } from "react-grid-layout"
import "react-grid-layout/css/styles.css"
import "react-resizable/css/styles.css"

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
import { authService } from '../../lib/auth/authService'
import { API_URL } from '@/lib/config'
import { useGlobalSearch, SearchResult } from "@/hooks/useGlobalSearch"
import { SearchResultsDropdown } from "./search-results-dropdown"
import { useRouter } from "next/navigation"

// Custom sidebar toggle that's always visible
const AlwaysVisibleSidebarToggle = () => {
  

  const { state, toggleSidebar } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <Button
      variant="outline"
      size="icon"
      className="fixed top-20 left-4 z-[5] h-10 w-10 rounded-full shadow-md bg-background"
      onClick={toggleSidebar}
      style={{ display: isCollapsed ? "flex" : "none" }}
    >
      <Menu className="h-4 w-4" />
      <span className="sr-only">Seitenleiste einblenden</span>
    </Button>
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

// Define types for widgets with extended layout properties
interface CustomLayout extends Layout {
  title?: string | null;
}

// Define types for layouts
interface Layouts {
  lg: CustomLayout[];
  md: CustomLayout[];
  sm: CustomLayout[];
  [key: string]: CustomLayout[];
}

// Dashboard widget component
const DashboardWidget = ({
  id,
  title,
  children,
  isEditMode,
  onRemove,
}: {
  id: string;
  title: string | null;
  children: React.ReactNode;
  isEditMode: boolean;
  onRemove?: (id: string) => void;
}) => {
  return (
    <div className={`h-full w-full overflow-auto ${isEditMode ? "border-2 border-dashed border-primary" : ""}`}>
      <div className="h-full flex flex-col">
        {isEditMode && (
          <div className="absolute top-0 right-0 p-1 z-10 flex gap-1">
            {onRemove && (
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-6 w-6 bg-destructive text-destructive-foreground rounded-full hover:bg-destructive/90"
                onClick={() => onRemove(id)}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
            <div className="h-6 w-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center">
              <Grip className="h-3 w-3" />
            </div>
          </div>
        )}
        
        {title && <h2 className="text-xl font-bold tracking-tight mb-2 pr-8">{title}</h2>}
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const [isEditMode, setIsEditMode] = useState(false)
  const [width, setWidth] = useState(1200) // Default width for SSR
  const [layouts, setLayouts] = useState<Layouts>({
    lg: [
      { i: "recent-orders", x: 0, y: 0, w: 12, h: 8, title: "Letzte Bestellungen nach Liefertermin" },
      { i: "menu-tiles", x: 0, y: 8, w: 12, h: 10, title: "Menü" },
      { i: "quick-links", x: 0, y: 18, w: 6, h: 6, title: "Schnellzugriff" },
      { i: "news-pinboard", x: 6, y: 18, w: 6, h: 6, title: "Pinnwand" },
    ],
    md: [
      { i: "recent-orders", x: 0, y: 0, w: 12, h: 8, title: "Letzte Bestellungen nach Liefertermin" },
      { i: "menu-tiles", x: 0, y: 8, w: 12, h: 12, title: "Menü" },
      { i: "quick-links", x: 0, y: 20, w: 6, h: 6, title: "Schnellzugriff" },
      { i: "news-pinboard", x: 6, y: 20, w: 6, h: 6, title: "Pinnwand" },
    ],
    sm: [
      { i: "recent-orders", x: 0, y: 0, w: 12, h: 8, title: "Letzte Bestellungen nach Liefertermin" },
      { i: "menu-tiles", x: 0, y: 8, w: 12, h: 14, title: "Menü" },
      { i: "quick-links", x: 0, y: 22, w: 12, h: 6, title: "Schnellzugriff" },
      { i: "news-pinboard", x: 0, y: 28, w: 12, h: 6, title: "Pinnwand" },
    ],
  })

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

  const handleLayoutChange = (currentLayout: Layout[], allLayouts: any) => {
    // Update the layouts state with the new positions and sizes
    setLayouts(allLayouts)
    
    // Save to localStorage
    try {
      localStorage.setItem("dashboard-grid-layout", JSON.stringify(allLayouts))
    } catch (error) {
      console.error("Failed to save layout", error)
    }
  }

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode)
  }

  // Add a useEffect to debug CSRF token on component mount
  useEffect(() => {
    // Debug CSRF token sources
    const cookieToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    // Type-safe access to window.DJANGO_SETTINGS if it exists
    const settingsToken = (window as any).DJANGO_SETTINGS?.CSRF_TOKEN;
    
    console.log('CSRF Debug:');
    console.log('- Cookie:', cookieToken);
    console.log('- Meta tag:', metaToken);
    console.log('- Settings:', settingsToken);
    console.log('- window.DJANGO_SETTINGS:', (window as any).DJANGO_SETTINGS);
  }, []);
  
  const saveLayout = async () => {
    try {
      console.log('Saving layout:', layouts);
      
      // Get CSRF token from cookies
      const getCookie = (name: string) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
          const part = parts.pop();
          return part ? part.split(';').shift() || null : null;
        }
        return null;
      };
      
      // Try multiple sources for the CSRF token
      const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      const csrfToken = getCookie('csrftoken') || (window as any).DJANGO_SETTINGS?.CSRF_TOKEN || metaToken;
      console.log("CSRF Token:", csrfToken); // Log token for debugging
      
      if (!csrfToken) {
        console.error("CSRF token is missing or invalid");
        return;
      }
      
      // Make sure the token doesn't have any whitespace
      const cleanToken = csrfToken.trim();
      
      // Save to backend API
      try {
        console.log("Saving layout to API...");
        
        // Get JWT token from auth service cookie storage
        const token = authService.getToken();
        
        if (!token) {
          console.error("JWT token not found. User may not be authenticated.");
          return;
        }
        
        const response = await fetch(`${API_URL}/dashboard/summary/`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": `Bearer ${token}`,
            // Keep CSRF token for session auth fallback
            "X-Csrftoken": cleanToken,
          },
          credentials: "include", // Include cookies for session auth fallback
          body: JSON.stringify({
            grid_layout: layouts
          })
        });
        
        if (response.ok) {
          console.log("Layout successfully saved to server");
        } else {
          const errorText = await response.text();
          console.error(`Failed to save layout to server: ${response.status} ${response.statusText}`);
          console.error("Error details:", errorText);
        }
      } catch (apiError) {
        console.error("API error when saving layout:", apiError);
      }
    } catch (error) {
      console.error("Failed to save layout", error);
    }
    setIsEditMode(false);
  }

  const toggleFavorite = (id: string) => {
    setMenuTiles((prev) => {
      const updatedTiles = prev.map((tile) =>
        tile.id === id ? { ...tile, favorited: !tile.favorited } : tile
      )
      
      // Save updated favorites to localStorage
      try {
        localStorage.setItem("dashboard-favorites", JSON.stringify(updatedTiles))
      } catch (error) {
        console.error("Failed to save favorites", error)
      }
      
      return updatedTiles
    })
  }

  const handleRemoveWidget = (id: string) => {
    setLayouts((prevLayouts: Layouts) => {
      const updatedLayouts = { ...prevLayouts };
      Object.keys(updatedLayouts).forEach((breakpoint) => {
        updatedLayouts[breakpoint] = updatedLayouts[breakpoint].filter((item) => item.i !== id);
      });
      
      try {
        localStorage.setItem("dashboard-grid-layout", JSON.stringify(updatedLayouts));
      } catch (error) {
        console.error("Failed to save layout after removing widget", error);
      }
      
      return updatedLayouts;
    });
  }

  // Load saved layout on initial render
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Try to fetch from API first
        console.log("Fetching dashboard data from API...");
        
        // Get JWT token from auth service cookie storage
        const token = authService.getToken();
        
        if (!token) {
          console.log("JWT token not found. User may not be authenticated. Falling back to localStorage.");
          const savedLayout = localStorage.getItem("dashboard-grid-layout");
          if (savedLayout) setLayouts(JSON.parse(savedLayout));
          return;
        }
        
        // Use the API_URL from config instead of relative path
        const response = await fetch(`${API_URL}/dashboard/summary/`, {
          headers: {
            "Accept": "application/json",
            "Authorization": `Bearer ${token}`
          },
          credentials: "include" // Include cookies for session auth fallback
        });
        
        if (response.ok) {
          console.log("API response successful");
          const data = await response.json();
          
          // If grid_layout exists in the API response, use it
          if (data.grid_layout && Object.keys(data.grid_layout).length > 0) {
            console.log("Using grid layout from API");
            setLayouts(data.grid_layout);
            return;
          } else {
            console.log("No grid layout in API response, falling back to localStorage");
          }
        } else {
          console.error(`API request failed: ${response.status} ${response.statusText}`);
        }
      } catch (apiError) {
        console.error("API error when fetching dashboard layout:", apiError);
      }
      
      // Fallback to localStorage if API fails or doesn't have grid_layout
      console.log("Falling back to localStorage for dashboard layout");
      const savedLayout = localStorage.getItem("dashboard-grid-layout");
      if (savedLayout) setLayouts(JSON.parse(savedLayout));
    };

    fetchDashboardData();

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

  // Update the width calculation in useEffect
  useEffect(() => {
    const updateWidth = () => {
      // Get the container width instead of using fixed width
      const container = document.querySelector('.dashboard-grid-container');
      if (container) {
        setWidth(container.clientWidth);
      }
    }

    // Set initial width
    updateWidth();

    // Add event listener for resize
    window.addEventListener('resize', updateWidth);

    // Cleanup
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  // Find the title for a widget based on its ID
  const getWidgetTitle = (id: string): string | null => {
    const layout = layouts.lg.find(item => item.i === id)
    return layout?.title || null
  }

  // Render widget content based on ID
  const renderWidgetContent = (widgetId: string) => {
    switch (widgetId) {
      case "recent-orders":
        return (
          <Card className="h-full border-0 shadow-none">
            <CardContent className="p-0 h-full">
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
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 h-full">
            {menuTiles.map((tile) => (
              <Card key={tile.id} className="hover:bg-muted/50 transition-colors cursor-pointer relative">
                <CardContent className="p-3 flex flex-col items-center justify-center text-center h-full">
                  <div className="flex items-center justify-center">
                    <tile.icon className="h-6 w-6 mb-1" />
                  </div>
                  <span className="text-sm font-medium">{tile.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(tile.id)
                    }}
                    className="absolute top-1 right-1 text-muted-foreground hover:text-yellow-400"
                  >
                    <Star className={`h-3 w-3 ${tile.favorited ? "fill-yellow-400 text-yellow-400" : ""}`} />
                    <span className="sr-only">Zu Favoriten {tile.favorited ? "entfernen" : "hinzufügen"}</span>
                  </button>
                </CardContent>
              </Card>
            ))}
          </div>
        )

      case "quick-links":
        return (
          <Card className="h-full border-0 shadow-none">
            <CardContent className="h-full p-3">
              <div className="grid grid-cols-1 gap-1 h-full overflow-auto">
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
          <Card className="h-full border-0 shadow-none">
            <CardContent className="p-2 h-full">
              <Tabs defaultValue="news" className="h-full flex flex-col">
                <TabsList className="mb-2">
                  <TabsTrigger value="news">News</TabsTrigger>
                  <TabsTrigger value="notes">Notizen</TabsTrigger>
                </TabsList>
                <div className="flex-1 overflow-auto">
                  <TabsContent value="news" className="m-0 h-full">
                    <div className="space-y-2 overflow-auto">
                      {newsItems.map((item, index) => (
                        <div key={index} className="border-b pb-2 last:border-0">
                          <div className="flex justify-between items-start mb-1">
                            <h3 className="font-medium text-sm">{item.title}</h3>
                            <span className="text-xs text-muted-foreground">{item.date}</span>
                          </div>
                          <p className="text-xs text-muted-foreground">{item.content}</p>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  <TabsContent value="notes" className="m-0 h-full flex flex-col">
                    <div className="flex flex-col gap-2 h-full">
                      <p className="text-xs text-muted-foreground">
                        Hier können Sie Ihre persönlichen Notizen hinzufügen.
                      </p>
                      <textarea
                        className="min-h-[80px] flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1"
                        placeholder="Notiz hinzufügen..."
                      />
                      <Button size="sm" className="self-end text-xs py-1 px-2 h-7">Speichern</Button>
                    </div>
                  </TabsContent>
                </div>
              </Tabs>
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <SidebarProvider defaultOpen={true}>
      <DashboardContent 
        isEditMode={isEditMode}
        width={width}
        layouts={layouts}
        setLayouts={setLayouts}
        menuTiles={menuTiles}
        setMenuTiles={setMenuTiles}
        toggleEditMode={toggleEditMode}
        saveLayout={saveLayout}
        handleRemoveWidget={handleRemoveWidget}
        toggleFavorite={toggleFavorite}
        recentAccessed={recentAccessed}
        handleLayoutChange={handleLayoutChange}
        getWidgetTitle={getWidgetTitle}
        renderWidgetContent={renderWidgetContent}
        recentOrders={recentOrders}
        quickLinks={quickLinks}
        newsItems={newsItems}
      />
    </SidebarProvider>
  )
}

// Separate component for the dashboard content
const DashboardContent = ({
  isEditMode,
  width,
  layouts,
  setLayouts,
  menuTiles,
  setMenuTiles,
  toggleEditMode,
  saveLayout,
  handleRemoveWidget,
  toggleFavorite,
  recentAccessed,
  handleLayoutChange,
  getWidgetTitle,
  renderWidgetContent,
  recentOrders,
  quickLinks,
  newsItems,
}: {
  isEditMode: boolean
  width: number
  layouts: Layouts
  setLayouts: React.Dispatch<React.SetStateAction<Layouts>>
  menuTiles: MenuTile[]
  setMenuTiles: React.Dispatch<React.SetStateAction<MenuTile[]>>
  toggleEditMode: () => void
  saveLayout: () => void
  handleRemoveWidget: (id: string) => void
  toggleFavorite: (id: string) => void
  recentAccessed: RecentItem[]
  handleLayoutChange: (currentLayout: Layout[], allLayouts: any) => void
  getWidgetTitle: (id: string) => string | null
  renderWidgetContent: (widgetId: string) => React.ReactNode
  recentOrders: Order[]
  quickLinks: QuickLink[]
  newsItems: NewsItem[]
}) => {

  const { state: sidebarState } = useSidebar()
  const { query, setQuery, results, isLoading, error, reset, getAllResults } = useGlobalSearch()
  const [showResults, setShowResults] = useState(false)
  const router = useRouter()

  const handleMenuClick = (id: string) => {
    // Navigate based on the clicked menu item
    switch(id) {
      case "inventory":
        router.push("/warehouse");  // Navigate to the inventory route
        break;
      // You can add more cases here for other menu items
      default:
        break;
    }
  };
  
  const handleInputFocus = () => {
    setShowResults(true)
  }

  const handleInputBlur = () => {
    // Delay hiding results to allow for click events
    setTimeout(() => setShowResults(false), 200)
  }

  const handleSearchResultSelect = (result: SearchResult) => {
    // Handle navigation based on result type
    switch (result.type) {
      case "customer":
        router.push(`/customers/${result.id}`)
        break
      case "sales_record":
        router.push(`/sales/${result.id}`)
        break
      case "parent_product":
        router.push(`/products/parent/${result.id}`)
        break
      case "variant_product":
        router.push(`/products/variant/${result.id}`)
        break
      case "box_slot":
        router.push(`/inventory/boxes/${result.id}`)
        break
      case "storage_location":
        router.push(`/inventory/locations/${result.id}`)
        break
      default:
        console.warn(`Unknown result type: ${result.type}`)
    }
    reset()
  }

  return (
    <div className="flex h-screen">
      <Sidebar className="border-r fixed h-full z-[5]">
        <SidebarHeader>
          <div className="flex items-center justify-between px-2 py-2 mt-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="flex md:flex" />
            </div>
          </div>
          <div className="px-2 pb-2 mt-2 relative">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                type="search" 
                placeholder="Suchen..." 
                className="h-9 pl-8 pr-8"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={handleInputFocus}
                onBlur={handleInputBlur}
              />
              {query && (
                <button 
                  className="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    reset()
                    setShowResults(false)
                  }}
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            {error && (
              <div className="mt-1 text-xs text-red-500">
                Fehler beim Suchen. Bitte versuchen Sie es später erneut.
              </div>
            )}
            <SearchResultsDropdown
              results={getAllResults()}
              isLoading={isLoading}
              open={!!(showResults && (isLoading || (results && results.total_count > 0)))}
              onSelect={handleSearchResultSelect}
            />
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
                          <Link href="#" onClick={() => handleMenuClick(item.id)}>
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
      </Sidebar>
      <div className="w-full h-full">
        <div className="relative">
          <div className="fixed inset-0 top-[60px] z-[1]" style={{ left: "50px" }}>
            <div className="h-[calc(100vh-180px)] bg-muted/20 rounded-lg w-full px-4">
              <div className="dashboard-grid-container w-full h-full">
                <ResponsiveGridLayout
                  className="layout"
                  layouts={layouts}
                  breakpoints={{ lg: 1200, md: 996, sm: 768 }}
                  cols={{ lg: 12, md: 12, sm: 12 }}
                  rowHeight={50}
                  width={width}
                  isDraggable={isEditMode}
                  isResizable={isEditMode}
                  onLayoutChange={(layout, layouts) => handleLayoutChange(layout, layouts)}
                  draggableHandle=".bg-primary"
                  margin={[16, 16]}
                  containerPadding={[16, 16]}
                  useCSSTransforms={true}
                  autoSize={true}
                >
                  {layouts.lg.map((item) => (
                    <div key={item.i} className="bg-background p-4 rounded-lg shadow-sm">
                      <DashboardWidget
                        id={item.i}
                        title={getWidgetTitle(item.i)}
                        isEditMode={isEditMode}
                        onRemove={handleRemoveWidget}
                      >
                        {renderWidgetContent(item.i)}
                      </DashboardWidget>
                    </div>
                  ))}
                </ResponsiveGridLayout>
              </div>
            </div>
          </div>
        </div>
        
        <div className="fixed bottom-24 right-6 z-30">
          {isEditMode ? (
            <div className="flex items-center gap-2">
              <Button size="sm" onClick={saveLayout}>
                <Save className="h-4 w-4 mr-2" />
                Speichern
              </Button>
              <Button variant="outline" size="sm" onClick={toggleEditMode}>
                <X className="h-4 w-4 mr-2" />
                Abbrechen
              </Button>
            </div>
          ) : (
            <Button variant="outline" size="sm" onClick={toggleEditMode} className="bg-background shadow-md">
              <Edit className="h-4 w-4 mr-2" />
              Bearbeiten
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

