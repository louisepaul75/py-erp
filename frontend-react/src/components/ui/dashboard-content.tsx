"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  X,
  Search,
  RotateCcw,
  Eye,
  Plus,
  ChevronDown,
  ChevronUp,
  Maximize,
  Minimize,
  Star,
  Edit,
  Grip,
  Save,
  Home,
  ShoppingCart,
  Package,
  BarChart3,
  Settings,
  Users,
} from "lucide-react"
import { Responsive as ResponsiveGridLayout, Layout } from "react-grid-layout"
import "react-grid-layout/css/styles.css"
import "react-resizable/css/styles.css"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useRouter } from "next/navigation"

// Define types for menu tiles
interface MenuTile {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  iconName: string;
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
  const [layouts, setLayouts] = useState<Layouts>(() => {
    // Try to load saved layout from localStorage
    if (typeof window !== 'undefined') {
      const savedLayout = localStorage.getItem('dashboard-layout')
      if (savedLayout) {
        try {
          return JSON.parse(savedLayout)
        } catch (e) {
          console.error('Failed to parse saved layout:', e)
        }
      }
    }
    // Default layout if no saved layout exists
    return {
      lg: [
        {
          w: 28,
          h: 13,
          x: 0,
          y: 0,
          i: "menu-tiles",
          moved: false,
          static: false
        },
        {
          w: 14,
          h: 12,
          x: 0,
          y: 13,
          i: "quick-links",
          moved: false,
          static: false
        },
        {
          w: 14,
          h: 12,
          x: 14,
          y: 13,
          i: "news-pinboard",
          moved: false,
          static: false
        }
      ],
      md: [
        {
          i: "menu-tiles",
          x: 0,
          y: 0,
          w: 24,
          h: 12,
          title: "Menü"
        },
        {
          i: "quick-links",
          x: 0,
          y: 12,
          w: 12,
          h: 6,
          title: "Schnellzugriff"
        },
        {
          i: "news-pinboard",
          x: 12,
          y: 12,
          w: 12,
          h: 6,
          title: "Pinnwand"
        }
      ],
      sm: [
        {
          i: "menu-tiles",
          x: 0,
          y: 0,
          w: 24,
          h: 14,
          title: "Menü"
        },
        {
          i: "quick-links",
          x: 0,
          y: 14,
          w: 24,
          h: 6,
          title: "Schnellzugriff"
        },
        {
          i: "news-pinboard",
          x: 0,
          y: 20,
          w: 24,
          h: 6,
          title: "Pinnwand"
        }
      ]
    }
  })

  const [menuTiles, setMenuTiles] = useState<MenuTile[]>([
    { id: "customers", name: "Kunden", icon: Users, iconName: "Users", favorited: false },
    { id: "orders", name: "Aufträge", icon: ShoppingCart, iconName: "ShoppingCart", favorited: false },
    { id: "products", name: "Produkte", icon: Package, iconName: "Package", favorited: false },
    { id: "reports", name: "Berichte", icon: BarChart3, iconName: "BarChart3", favorited: false },
    { id: "settings", name: "Einstellungen", icon: Settings, iconName: "Settings", favorited: false },
    { id: "users", name: "Benutzer", icon: Users, iconName: "Users", favorited: false },
    { id: "finance", name: "Finanzen", icon: BarChart3, iconName: "BarChart3", favorited: false },
    { id: "inventory", name: "Lager", icon: Package, iconName: "Package", favorited: false },
    { id: "picklist", name: "Picklist", icon: Package, iconName: "Package", favorited: false },
    { id: "support", name: "Support", icon: Users, iconName: "Users", favorited: false },
    { id: "documents", name: "Dokumente", icon: Package, iconName: "Package", favorited: false },
    { id: "dashboard", name: "Dashboard", icon: Home, iconName: "Home", favorited: false },
  ])

  // Quick links
  const quickLinksData: QuickLink[] = [
    { name: "Handbuch", url: "#" },
    { name: "Support-Ticket erstellen", url: "#" },
    { name: "Schulungsvideos", url: "#" },
    { name: "FAQ", url: "#" },
    { name: "Kontakt", url: "#" },
    { name: "Systemstatus", url: "#" },
    { name: "Updates", url: "#" },
  ]

  // News items
  const newsItemsData: NewsItem[] = [
    { 
      title: "Neues Update verfügbar", 
      date: "2025-03-15", 
      content: "Version 2.5 ist jetzt verfügbar. Dieses Update enthält wichtige Sicherheitsverbesserungen und neue Funktionen." 
    },
    { 
      title: "Wartungsarbeiten", 
      date: "2025-03-18", 
      content: "Am 18. März von 22:00 bis 23:00 Uhr werden Wartungsarbeiten durchgeführt." 
    },
    { 
      title: "Neuer Schulungskurs", 
      date: "2025-03-20", 
      content: "Ein neuer Online-Schulungskurs zur Bestandsverwaltung ist jetzt verfügbar." 
    },
  ]

  // Recent orders data
  const recentOrdersData: Order[] = [
    { id: "ORD-7352", customer: "Müller GmbH", date: "2025-03-20", status: "Pending", amount: "€1,240.00" },
    { id: "ORD-7351", customer: "Schmidt AG", date: "2025-03-18", status: "Processing", amount: "€2,156.00" },
    { id: "ORD-7350", customer: "Weber KG", date: "2025-03-17", status: "Shipped", amount: "€865.50" },
    { id: "ORD-7349", customer: "Becker & Co.", date: "2025-03-15", status: "Delivered", amount: "€1,790.25" },
    { id: "ORD-7348", customer: "Fischer GmbH", date: "2025-03-12", status: "Delivered", amount: "€3,450.00" },
  ]

  // Effect to load data
  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      try {
        // In a real app, you would fetch data from an API here
        setTimeout(() => {
          setRecentOrders(recentOrdersData)
          setQuickLinks(quickLinksData)
          setNewsItems(newsItemsData)
          
          // Load favorites from localStorage
          if (typeof window !== 'undefined') {
            const savedFavorites = localStorage.getItem('dashboard-favorites')
            if (savedFavorites) {
              try {
                const favoritesData = JSON.parse(savedFavorites)
                // Map the icon names back to components
                const fullTiles = menuTiles.map(tile => {
                  // Find matching saved tile (if any)
                  const savedTile = favoritesData.find((item: any) => item.id === tile.id)
                  return savedTile ? { 
                    ...tile, 
                    favorited: savedTile.favorited 
                  } : tile
                })
                setMenuTiles(fullTiles)
              } catch (error) {
                console.error('Failed to parse favorites data:', error)
              }
            }
          }
          
          setIsLoading(false)
        }, 1000)
      } catch (err) {
        setError("Failed to load dashboard data")
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  // Update width on window resize
  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth)
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // Function to toggle edit mode
  const toggleEditMode = () => {
    setIsEditMode(!isEditMode)
  }

  // Function to save layout changes
  const saveLayout = () => {
    // Save the current layout to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('dashboard-layout', JSON.stringify(layouts))
    }
    setIsEditMode(false)
  }

  // Function to remove a widget
  const handleRemoveWidget = (id: string) => {
    // Remove the widget from all layouts
    const newLayouts = { ...layouts }
    
    Object.keys(newLayouts).forEach((breakpoint) => {
      newLayouts[breakpoint] = newLayouts[breakpoint].filter((item) => item.i !== id)
    })
    
    setLayouts(newLayouts)
    // Save to localStorage after removing widget
    if (typeof window !== 'undefined') {
      localStorage.setItem('dashboard-layout', JSON.stringify(newLayouts))
    }
  }

  // Function to toggle favorite status for menu tiles
  const toggleFavorite = (id: string) => {
    const updatedTiles = menuTiles.map((tile) => 
      tile.id === id ? { ...tile, favorited: !tile.favorited } : tile
    )
    setMenuTiles(updatedTiles)
    
    // Save to localStorage with serializable data
    if (typeof window !== 'undefined') {
      // Create a simplified version of the tiles that's serializable
      const simplifiedTiles = updatedTiles.map(tile => ({
        id: tile.id,
        name: tile.name,
        iconName: tile.iconName,
        favorited: tile.favorited
      }))
      
      localStorage.setItem('dashboard-favorites', JSON.stringify(simplifiedTiles))
      
      // Dispatch a custom event to notify other components about the change
      window.dispatchEvent(new CustomEvent('favoritesChanged', {
        detail: { favorites: simplifiedTiles }
      }))
    }
  }

  // Handle layout changes
  const handleLayoutChange = (currentLayout: Layout[], allLayouts: Layouts) => {
    setLayouts(allLayouts)
    // Save to localStorage whenever layout changes
    if (typeof window !== 'undefined') {
      localStorage.setItem('dashboard-layout', JSON.stringify(allLayouts))
    }
  }

  // Function to get widget title based on id
  const getWidgetTitle = (id: string): string | null => {
    // First check in current layout for the title
    const currentBreakpoint = width >= 1200 ? "lg" : width >= 996 ? "md" : "sm"
    const layoutItem = layouts[currentBreakpoint]?.find((item) => item.i === id)
    
    if (layoutItem?.title) {
      return layoutItem.title
    }
    
    // Default titles if not found in layout
    switch (id) {
      case "menu-tiles":
        return "Menü"
      case "quick-links":
        return "Schnellzugriff"
      case "news-pinboard":
        return "Pinnwand"
      default:
        return null
    }
  }

  // Function to render widget content based on id
  const renderWidgetContent = (id: string) => {
    switch (id) {
      case "menu-tiles":
        return (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
            {menuTiles.map((tile) => {
              const IconComponent = tile.icon
              return (
                <Card 
                  key={tile.id} 
                  className="relative group cursor-pointer" 
                  onClick={() => handleMenuClick(tile.id)}
                >
                  <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(tile.id)
                      }}
                    >
                      <Star
                        className={`h-4 w-4 ${tile.favorited ? "fill-yellow-400 text-yellow-400" : ""}`}
                      />
                    </Button>
                    <div className="mb-2 mt-2 p-2 bg-primary/10 rounded-full">
                      <IconComponent className="h-6 w-6 text-primary" />
                    </div>
                    <span className="text-sm font-medium">{tile.name}</span>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )
      case "quick-links":
        return (
          <div className="space-y-3">
            {quickLinks.map((link, index) => (
              <Link key={index} href={link.url}>
                <Button variant="ghost" className="w-full justify-start text-sm">
                  {link.name}
                </Button>
              </Link>
            ))}
          </div>
        )
      case "news-pinboard":
        return (
          <div className="space-y-4 overflow-auto max-h-full">
            {newsItems.map((item, index) => (
              <Card key={index}>
                <CardHeader className="p-3">
                  <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
                  <p className="text-xs text-muted-foreground">{item.date}</p>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <p className="text-xs">{item.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )
      default:
        return <div>Unknown widget: {id}</div>
    }
  }

  // Use memoized values for grid layout props to prevent unnecessary re-renders
  const gridBreakpoints = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 };
  const gridCols = { lg: 48, md: 40, sm: 24, xs: 12, xxs: 8 };
  const gridRowHeight = 30;
  const gridMargin = useMemo<[number, number]>(() => [8, 8], [])

  const router = useRouter()

  const handleMenuClick = (id: string) => {
    // Navigate based on the clicked menu item
    switch(id) {
      case "dashboard":
        router.push("/dashboard");
        break;
      case "customers":
        router.push("/customers");
        break;
      case "orders":
        router.push("/orders");
        break;
      case "products":
        router.push("/products");
        break;
      case "reports":
        router.push("/reports");
        break;
      case "settings":
        router.push("/settings");
        break;
      case "users":
        router.push("/users");
        break;
      case "finance":
        router.push("/finance");
        break;
      case "inventory":
        router.push("/warehouse");
        break;
      case "picklist":
        router.push("/picklist");
        break;
      case "support":
        router.push("/support");
        break;
      case "documents":
        router.push("/documents");
        break;
      default:
        // For other menu items that don't have routes yet
        console.log(`Clicked on menu item: ${id}`);
        break;
    }
  };

  // Get current layout based on breakpoints
  const currentBreakpoint = width >= 1200 ? "lg" : width >= 996 ? "md" : "sm"
  const currentLayouts = layouts
  const layoutKeys = Array.from(new Set(Object.values(layouts).flatMap(layouts => layouts.map(layout => layout.i))))

  return (
    <div className="w-full max-w-screen-xl mx-auto py-10 px-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <div className="flex items-center gap-2">
          {isEditMode ? (
            <>
              <Button variant="outline" onClick={toggleEditMode}>
                <X className="mr-2 h-4 w-4" />
                Abbrechen
              </Button>
              <Button onClick={saveLayout}>
                <Save className="mr-2 h-4 w-4" />
                Speichern
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={toggleEditMode}>
              <Edit className="mr-2 h-4 w-4" />
              Layout bearbeiten
            </Button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="dashboard-grid-container w-full">
          <ResponsiveGridLayout
            className="layout"
            layouts={layouts}
            breakpoints={gridBreakpoints}
            cols={gridCols}
            rowHeight={gridRowHeight}
            width={width}
            margin={gridMargin}
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
      )}
    </div>
  )
}

export default Dashboard 