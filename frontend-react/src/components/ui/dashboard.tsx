"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
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
  ChevronRight,
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
import { authService, csrfService } from '../../lib/auth/authService'
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
      className="fixed top-1/2 -translate-y-1/2 left-0 z-[60] h-12 w-8 rounded-r-lg shadow-md bg-background border-l-0 hover:bg-accent transition-all duration-200"
      onClick={toggleSidebar}
      style={{ transform: `translateY(-50%) translateX(${isCollapsed ? '0' : '-100%'})` }}
    >
      <ChevronRight className="h-5 w-5" />
      <span className="sr-only">Show Sidebar</span>
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
            <div className="h-6 w-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center draggable-handle">
              <Grip className="h-3 w-3" />
            </div>
          </div>
        )}
        
        {title && (
          <div className={isEditMode ? "draggable-handle" : ""}>
            <h2 className="text-xl font-bold tracking-tight mb-2 pr-8">{title}</h2>
          </div>
        )}
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
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recentOrders, setRecentOrders] = useState<Order[]>([])
  const [quickLinks, setQuickLinks] = useState<QuickLink[]>([])
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [layouts, setLayouts] = useState<Layouts>({
    lg: [
      { w: 16, h: 11, x: 0, y: 0, i: "menu-tiles", moved: false, static: false },
      { w: 8, h: 12, x: 0, y: 11, i: "quick-links", moved: false, static: false },
      { w: 8, h: 12, x: 8, y: 11, i: "news-pinboard", moved: false, static: false }
    ],
    md: [
      { i: "menu-tiles", x: 0, y: 0, w: 20, h: 12, title: "Menü" },
      { i: "quick-links", x: 0, y: 12, w: 10, h: 6, title: "Schnellzugriff" },
      { i: "news-pinboard", x: 10, y: 12, w: 10, h: 6, title: "Pinnwand" }
    ],
    sm: [
      { i: "menu-tiles", x: 0, y: 0, w: 12, h: 14, title: "Menü" },
      { i: "quick-links", x: 0, y: 14, w: 12, h: 6, title: "Schnellzugriff" },
      { i: "news-pinboard", x: 0, y: 20, w: 12, h: 6, title: "Pinnwand" }
    ]
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
    { id: "picklist", name: "Picklist", icon: Package, favorited: false },
    { id: "support", name: "Support", icon: Users, favorited: false },
    { id: "documents", name: "Dokumente", icon: Package, favorited: false },
    { id: "dashboard", name: "Dashboard", icon: Home, favorited: false },
  ])

  // Recent orders data
  const recentOrdersData: Order[] = [
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
  const quickLinksData: QuickLink[] = [
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
  const newsItemsData: NewsItem[] = [
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

  // Memoize the handleLayoutChange function to prevent unnecessary re-renders
  const handleLayoutChange = useCallback((currentLayout: Layout[], allLayouts: any) => {
    // Update the layouts state with the new positions and sizes
    setLayouts(allLayouts)
    
    // Save to localStorage
    try {
      localStorage.setItem("dashboard-grid-layout", JSON.stringify(allLayouts))
    } catch (error) {
      console.error("Failed to save layout", error)
    }
  }, [])

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
      
      // Get JWT token from auth service cookie storage
      const token = authService.getToken();
      
      if (!token) {
        console.error("JWT token not found. User may not be authenticated.");
        return;
      }
      
      // Get or fetch CSRF token
      let csrfToken = csrfService.getToken();
      if (!csrfToken) {
        console.log("No CSRF token found, fetching a new one");
        csrfToken = await csrfService.fetchToken();
      }
      
      // Proceed with the API call to save the layout
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": `Bearer ${token}`
      };
      
      // Add CSRF token if available
      if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
      }
      
      console.log("Saving layout to API with headers:", headers);
      
      // Construct the correct API endpoint URL
      const dashboardSummaryUrl = `${API_URL}/v1/dashboard/summary/`;
      
      const response = await fetch(dashboardSummaryUrl, {
        method: "PATCH",
        headers,
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
        
        // If it's a CSRF error, try one more time with a fresh token
        if (response.status === 403 && (errorText.includes("CSRF") || errorText.includes("csrf"))) {
          try {
            console.log("CSRF validation failed, trying with a fresh token");
            const freshToken = await csrfService.fetchToken();
            
            if (freshToken) {
              console.log("Retrying with fresh CSRF token");
              
              const retryHeaders = {
                ...headers,
                "X-CSRFToken": freshToken
              };
              
              const retryResponse = await fetch(dashboardSummaryUrl, {
                method: "PATCH",
                headers: retryHeaders,
                credentials: "include",
                body: JSON.stringify({
                  grid_layout: layouts
                })
              });
              
              if (retryResponse.ok) {
                console.log("Layout successfully saved to server on retry");
                setIsEditMode(false);
                return;
              } else {
                console.error("Retry with fresh CSRF token also failed");
              }
            }
          } catch (retryError) {
            console.error("Error during retry with fresh CSRF token:", retryError);
          }
        }
        
        // Display error message to user
        alert("Fehler beim Speichern des Layouts. Bitte versuchen Sie es später erneut.");
      }
    } catch (error) {
      console.error("Failed to save layout", error);
      alert("Fehler beim Speichern des Layouts. Bitte versuchen Sie es später erneut.");
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
      setIsLoading(true);
      setError(null);
      
      try {
        // Use hardcoded data instead of API calls for now
        // The following API endpoints are not implemented yet:
        // - /api/orders/recent
        // - /api/menu/tiles
        // - /api/quick-links
        // - /api/news
        
        // Comment out API calls that are resulting in 404 errors
        /*
        const [ordersResponse, tilesResponse, linksResponse, newsResponse] = await Promise.allSettled([
          fetch('/api/orders/recent'),
          fetch('/api/menu/tiles'),
          fetch('/api/quick-links'),
          fetch('/api/news')
        ]);

        // Initialize data with defaults
        let orders: Order[] = [];
        let tiles: MenuTile[] = [];
        let links: QuickLink[] = [];
        let news: NewsItem[] = [];

        // Handle each response
        if (ordersResponse.status === 'fulfilled' && ordersResponse.value.ok) {
          orders = await ordersResponse.value.json();
        }
        if (tilesResponse.status === 'fulfilled' && tilesResponse.value.ok) {
          tiles = await tilesResponse.value.json();
        }
        if (linksResponse.status === 'fulfilled' && linksResponse.value.ok) {
          links = await linksResponse.value.json();
        }
        if (newsResponse.status === 'fulfilled' && newsResponse.value.ok) {
          news = await newsResponse.value.json();
        }
        */
        
        // Use the existing hardcoded data directly
        setRecentOrders(recentOrdersData);
        // Only update menuTiles if there's no existing data (preserves any runtime changes)
        if (menuTiles.length === 0) {
          setMenuTiles([
            { id: "customers", name: "Kunden", icon: Users, favorited: false },
            { id: "orders", name: "Aufträge", icon: ShoppingCart, favorited: false },
            { id: "products", name: "Produkte", icon: Package, favorited: false },
            { id: "reports", name: "Berichte", icon: BarChart3, favorited: false },
            { id: "settings", name: "Einstellungen", icon: Settings, favorited: false },
            { id: "users", name: "Benutzer", icon: Users, favorited: false },
            { id: "finance", name: "Finanzen", icon: BarChart3, favorited: false },
            { id: "inventory", name: "Lager", icon: Package, favorited: false },
            { id: "picklist", name: "Picklist", icon: Package, favorited: false },
            { id: "support", name: "Support", icon: Users, favorited: false },
            { id: "documents", name: "Dokumente", icon: Package, favorited: false },
            { id: "dashboard", name: "Dashboard", icon: Home, favorited: false },
          ]);
        }
        setQuickLinks(quickLinksData);
        setNewsItems(newsItemsData);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Update the width calculation with adjustment for sidebar
  useEffect(() => {
    if (!isLoading) {
      const updateWidth = () => {
        const sidebar = document.querySelector('.sidebar');
        const sidebarWidth = sidebar?.getBoundingClientRect().width || 0;
        const mainContentWidth = window.innerWidth - sidebarWidth;
        
        // Set width to full window width minus sidebar width
        setWidth(mainContentWidth);
      }

      // Initial width calculation
      updateWidth();

      // Update width on window resize
      window.addEventListener('resize', updateWidth);

      // Update width when sidebar state changes
      const sidebarObserver = new ResizeObserver(() => {
        updateWidth();
      });

      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebarObserver.observe(sidebar);
      }

      // Cleanup
      return () => {
        window.removeEventListener('resize', updateWidth);
        sidebarObserver.disconnect();
      }
    }
  }, [isLoading]);

  // Find the title for a widget based on its ID
  const getWidgetTitle = (id: string): string | null => {
    const layout = layouts.lg.find(item => item.i === id)
    return layout?.title || null
  }

  // Render widget content based on ID
  const renderWidgetContent = (widgetId: string) => {
    // Add null checks for all data before rendering
    if (!recentOrders || !menuTiles || !quickLinks || !newsItems) {
      return <div>Loading widget content...</div>
    }

    switch (widgetId) {
      case "recent-orders":
        return (
          <div className="space-y-8">
            {recentOrders.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bestellnummer</TableHead>
                    <TableHead>Kunde</TableHead>
                    <TableHead>Datum</TableHead>
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
            ) : (
              <div className="text-center py-4">Keine Bestellungen gefunden</div>
            )}
          </div>
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

  // Memoize the actual layout that will be rendered to prevent unnecessary re-calculations
  const currentLayouts = useMemo(() => layouts, [layouts]);

  // Add loading state check at the beginning of the render
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-destructive">{error}</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen">
      <Sidebar className="border-r fixed h-full z-[5] sidebar">
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
              open={!!(showResults && (isLoading || (results && typeof results === 'object' && 'total_count' in results && (results as any).total_count > 0)))}
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
        <div className="relative w-full h-full">
          <AlwaysVisibleSidebarToggle />
          <div className="absolute inset-0 top-[60px] z-[1]">
            <div className="h-[calc(100vh-180px)] w-full">
              <div className="w-full h-full">
                <ResponsiveGridLayout
                  className="layout"
                  layouts={layouts}
                  breakpoints={gridBreakpoints}
                  cols={gridCols}
                  rowHeight={gridRowHeight}
                  width={width}
                  margin={[10, 10]}
                  containerPadding={[20, 0]}
                  onLayoutChange={handleLayoutChange}
                  isDraggable={isEditMode}
                  isResizable={isEditMode}
                  draggableHandle=".draggable-handle"
                  compactType="vertical"
                  useCSSTransforms={true}
                  preventCollision={false}
                >
                  {layoutKeys.map((key) => (
                    <div key={key} className="relative bg-card p-4 rounded-lg overflow-hidden shadow-sm border">
                      <DashboardWidget
                        id={key}
                        title={getWidgetTitle(key)}
                        isEditMode={isEditMode}
                        onRemove={isEditMode ? handleRemoveWidget : undefined}
                      >
                        {renderWidgetContent(key)}
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

  // Use memoized values for grid layout props to prevent unnecessary re-renders
  const gridBreakpoints = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 };
  const gridCols = { lg: 24, md: 20, sm: 12, xs: 6, xxs: 4 };
  const gridRowHeight = 30;
  const gridMargin = useMemo<[number, number]>(() => [16, 16], [])
  
  // Generate a stable list of layout IDs to prevent re-renders
  const layoutKeys = useMemo(() => {
    if (!layouts || !layouts.lg) return [];
    return layouts.lg.map(item => item.i);
  }, [layouts]);

  return (
    <div className="flex h-screen">
      <Sidebar className="border-r fixed h-full z-[5] sidebar">
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
              open={!!(showResults && (isLoading || (results && typeof results === 'object' && 'total_count' in results && (results as any).total_count > 0)))}
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
        <div className="relative w-full h-full">
          <AlwaysVisibleSidebarToggle />
          <div className="absolute inset-0 top-[60px] z-[1]">
            <div className="h-[calc(100vh-180px)] w-full">
              <div className="w-full h-full">
                <ResponsiveGridLayout
                  className="layout"
                  layouts={layouts}
                  breakpoints={gridBreakpoints}
                  cols={gridCols}
                  rowHeight={gridRowHeight}
                  width={width}
                  margin={[10, 10]}
                  containerPadding={[20, 0]}
                  onLayoutChange={handleLayoutChange}
                  isDraggable={isEditMode}
                  isResizable={isEditMode}
                  draggableHandle=".draggable-handle"
                  compactType="vertical"
                  useCSSTransforms={true}
                  preventCollision={false}
                >
                  {layoutKeys.map((key) => (
                    <div key={key} className="relative bg-card p-4 rounded-lg overflow-hidden shadow-sm border">
                      <DashboardWidget
                        id={key}
                        title={getWidgetTitle(key)}
                        isEditMode={isEditMode}
                        onRemove={isEditMode ? handleRemoveWidget : undefined}
                      >
                        {renderWidgetContent(key)}
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

