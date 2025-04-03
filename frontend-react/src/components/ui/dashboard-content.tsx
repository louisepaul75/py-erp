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
  LayoutPanelLeft,
} from "lucide-react"
import { Responsive as ResponsiveGridLayout, Layout } from "react-grid-layout"
import "react-grid-layout/css/styles.css"
import "react-resizable/css/styles.css"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useRouter } from "next/navigation"
import { DashboardSidebar, SavedLayout } from "./dashboard-sidebar"
import { 
  fetchDashboardConfig, 
  saveGridLayout, 
  saveNewLayout, 
  updateLayout, 
  deleteLayout, 
  activateLayout,
  GridLayouts 
} from "@/lib/dashboard-service"
import { v4 as uuidv4 } from "uuid"
import { toast } from "@/components/ui/use-toast"

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
            <h2 className="text-xl font-bold tracking-tight mb-2 pr-8 text-primary">{title}</h2>
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
    // Default layout just as a fallback - the real layout will be loaded from API
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
  const [savedLayouts, setSavedLayouts] = useState<SavedLayout[]>([])
  const [activeLayoutId, setActiveLayoutId] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

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
    // Load data function
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Load dashboard configuration from API
        try {
          const dashboardConfig = await fetchDashboardConfig();
          
          if (dashboardConfig.grid_layout && Object.keys(dashboardConfig.grid_layout).length > 0) {
            setLayouts(dashboardConfig.grid_layout);
          }
          
          if (dashboardConfig.saved_layouts && dashboardConfig.saved_layouts.length > 0) {
            // Convert API format to the format needed by the sidebar
            const formattedLayouts = dashboardConfig.saved_layouts.map(layout => ({
              id: layout.id,
              name: layout.name,
              layouts: layout.grid_layout,
              isActive: layout.id === dashboardConfig.active_layout_id
            }));
            setSavedLayouts(formattedLayouts);
          }
          
          setActiveLayoutId(dashboardConfig.active_layout_id);
        } catch (apiError) {
          console.error("Failed to load dashboard configuration from API:", apiError);
          // Continue with the current layout - no need to show error to user
          // The dashboard will just use the default layout
        }
        
        // Load sample data and favorites
        setTimeout(() => {
          setRecentOrders(recentOrdersData);
          setQuickLinks(quickLinksData);
          setNewsItems(newsItemsData);
          
          // Load favorites from localStorage
          if (typeof window !== 'undefined') {
            const savedFavorites = localStorage.getItem('dashboard-favorites');
            if (savedFavorites) {
              try {
                const favoritesData = JSON.parse(savedFavorites);
                // Map the icon names back to components
                const fullTiles = menuTiles.map(tile => {
                  // Find matching saved tile (if any)
                  const savedTile = favoritesData.find((item: any) => item.id === tile.id);
                  return savedTile ? { 
                    ...tile, 
                    favorited: savedTile.favorited 
                  } : tile;
                });
                setMenuTiles(fullTiles);
              } catch (error) {
                console.error('Failed to parse favorites data:', error);
              }
            }
          }
          
          setIsLoading(false);
        }, 1000);
      } catch (err) {
        console.error("Dashboard data loading error:", err);
        setError("Failed to load dashboard data. Please try refreshing the page.");
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

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
  const saveLayout = async () => {
    try {
      // If we have an active layout, update it
      if (activeLayoutId) {
        const layoutToUpdate = savedLayouts.find(layout => layout.id === activeLayoutId)
        if (layoutToUpdate) {
          const result = await updateLayout(activeLayoutId, layoutToUpdate.name, layouts as GridLayouts)
          // Preserve existing layouts if none are returned
          setSavedLayouts(prevLayouts => {
            const resultLayouts = Array.isArray(result.saved_layouts) ? result.saved_layouts : [];
            return resultLayouts.length > 0 
              ? resultLayouts.map(layout => ({
                  id: layout.id,
                  name: layout.name,
                  layouts: layout.grid_layout,
                  isActive: layout.id === result.active_layout_id
                }))
              : prevLayouts.map(layout => ({
                  ...layout,
                  layouts: layout.id === activeLayoutId ? layouts : layout.layouts,
                  isActive: layout.id === activeLayoutId
                }));
          });
          toast({
            title: "Layout updated",
            description: `"${layoutToUpdate.name}" has been updated`,
            duration: 3000,
          })
        }
      } else {
        // Otherwise just save the current layout to the database
        await saveGridLayout(layouts as GridLayouts)
        toast({
          title: "Layout saved",
          description: "Dashboard layout has been saved",
          duration: 3000,
        })
      }
      setIsEditMode(false)
    } catch (error) {
      console.error("Error saving layout:", error)
      toast({
        title: "Error",
        description: "Failed to save layout. Please try again.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  // Function to save a new named layout
  const handleSaveNewLayout = async (name: string) => {
    try {
      const result = await saveNewLayout(name, layouts as GridLayouts)
      // Add safeguard to ensure saved_layouts is an array and preserve existing layouts
      setSavedLayouts(prevLayouts => {
        const resultLayouts = Array.isArray(result.saved_layouts) ? result.saved_layouts : [];
        if (resultLayouts.length > 0) {
          return resultLayouts.map(layout => ({
            id: layout.id,
            name: layout.name,
            layouts: layout.grid_layout,
            isActive: layout.id === result.active_layout_id
          }));
        } else {
          // If no layouts returned, create a new one with generated ID and add to existing
          const newLayoutId = result.active_layout_id || `layout-${Date.now()}`;
          const newLayout = {
            id: newLayoutId,
            name: name,
            layouts: layouts,
            isActive: true
          };
          return [...prevLayouts.map(l => ({...l, isActive: false})), newLayout];
        }
      });
      
      setActiveLayoutId(result.active_layout_id || null)
      toast({
        title: "New layout saved",
        description: `"${name}" has been created and activated`,
        duration: 3000,
      })
    } catch (error) {
      console.error("Error saving new layout:", error)
      toast({
        title: "Error",
        description: "Failed to save new layout. Please try again.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  // Function to update an existing layout
  const handleUpdateLayout = async (layout: SavedLayout) => {
    try {
      const result = await updateLayout(layout.id, layout.name, layout.layouts as GridLayouts)
      // Preserve existing layouts if none are returned
      setSavedLayouts(prevLayouts => {
        const resultLayouts = Array.isArray(result.saved_layouts) ? result.saved_layouts : [];
        return resultLayouts.length > 0 
          ? resultLayouts.map(layout => ({
              id: layout.id,
              name: layout.name,
              layouts: layout.grid_layout,
              isActive: layout.id === result.active_layout_id
            }))
          : prevLayouts.map(l => ({
              ...l,
              name: l.id === layout.id ? layout.name : l.name,
              layouts: l.id === layout.id ? layout.layouts : l.layouts
            }));
      });
      toast({
        title: "Layout updated",
        description: `"${layout.name}" has been updated`,
        duration: 3000,
      })
    } catch (error) {
      console.error("Error updating layout:", error)
      toast({
        title: "Error",
        description: "Failed to update layout. Please try again.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  // Function to delete a layout
  const handleDeleteLayout = async (layoutId: string) => {
    try {
      const result = await deleteLayout(layoutId)
      // Preserve existing layouts if none are returned, but remove the deleted one
      setSavedLayouts(prevLayouts => {
        const resultLayouts = Array.isArray(result.saved_layouts) ? result.saved_layouts : [];
        if (resultLayouts.length > 0) {
          return resultLayouts.map(layout => ({
            id: layout.id,
            name: layout.name,
            layouts: layout.grid_layout,
            isActive: layout.id === result.active_layout_id
          }));
        } else {
          // Filter out the deleted layout
          return prevLayouts.filter(layout => layout.id !== layoutId);
        }
      });
      
      // Update active layout ID
      setActiveLayoutId(result.active_layout_id || savedLayouts.find(l => l.id !== layoutId)?.id || null)
      
      // If the active layout was deleted, update the layouts state
      if (result.grid_layout && Object.keys(result.grid_layout).length > 0) {
        setLayouts(result.grid_layout)
      }
      
      toast({
        title: "Layout deleted",
        description: "The layout has been deleted",
        duration: 3000,
      })
    } catch (error) {
      console.error("Error deleting layout:", error)
      toast({
        title: "Error",
        description: "Failed to delete layout. Please try again.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  // Function to select a layout
  const handleLayoutSelect = async (layoutId: string) => {
    try {
      const result = await activateLayout(layoutId)
      // Preserve existing layouts if none are returned
      setSavedLayouts(prevLayouts => {
        const resultLayouts = Array.isArray(result.saved_layouts) ? result.saved_layouts : [];
        return resultLayouts.length > 0 
          ? resultLayouts.map(layout => ({
              id: layout.id,
              name: layout.name,
              layouts: layout.grid_layout,
              isActive: layout.id === result.active_layout_id
            }))
          : prevLayouts.map(layout => ({
              ...layout,
              isActive: layout.id === layoutId
            }));
      });
      
      setActiveLayoutId(result.active_layout_id || layoutId)
      
      if (result.grid_layout && Object.keys(result.grid_layout).length > 0) {
        setLayouts(result.grid_layout)
      }
      
      toast({
        title: "Layout activated",
        description: "The selected layout has been activated",
        duration: 3000,
      })
    } catch (error) {
      console.error("Error selecting layout:", error)
      toast({
        title: "Error",
        description: "Failed to activate layout. Please try again.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  // Function to remove a widget
  const handleRemoveWidget = (id: string) => {
    // Remove the widget from all layouts
    const newLayouts = { ...layouts }
    
    Object.keys(newLayouts).forEach((breakpoint) => {
      newLayouts[breakpoint] = newLayouts[breakpoint].filter((item) => item.i !== id)
    })
    
    setLayouts(newLayouts)
    // No need to save to localStorage - will be saved when user clicks Save
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
    
    // Auto-save is handled when user clicks "Save" explicitly now
    // No need to save to API on every small change
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
                    <span className="text-sm font-medium text-foreground">{tile.name}</span>
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
                <Button variant="ghost" className="w-full justify-start text-sm text-foreground hover:text-primary">
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
                  <CardTitle className="text-sm font-medium text-primary">{item.title}</CardTitle>
                  <p className="text-xs text-muted-foreground">{item.date}</p>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <p className="text-xs text-foreground">{item.content}</p>
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
        <h1 className="text-3xl font-bold tracking-tight text-primary">Dashboard</h1>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={() => setIsSidebarOpen(true)}
            className="border-primary text-primary hover:bg-primary/10"
          >
            <LayoutPanelLeft className="mr-2 h-4 w-4" />
            Layouts
          </Button>
        </div>
      </div>

      <DashboardSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        isEditMode={isEditMode}
        toggleEditMode={toggleEditMode}
        saveLayout={saveLayout}
        savedLayouts={savedLayouts}
        activeLayoutId={activeLayoutId}
        onLayoutSelect={handleLayoutSelect}
        onSaveNewLayout={handleSaveNewLayout}
        onUpdateLayout={handleUpdateLayout}
        onDeleteLayout={handleDeleteLayout}
      />

      {error && (
        <div className="mt-4 p-4 border border-red-400 bg-red-50 text-red-800 rounded-md">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-2 text-sm font-medium text-red-800 hover:text-red-600 underline"
              >
                Refresh page
              </button>
            </div>
          </div>
        </div>
      )}

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