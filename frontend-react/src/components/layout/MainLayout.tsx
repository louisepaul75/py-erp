"use client"

import { usePathname, useRouter } from 'next/navigation'
import { Navbar } from '../Navbar'
import {
  Sidebar,
  SidebarContent,
  SidebarProvider,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  useSidebar,
  SidebarHeader,
  SidebarFooter,
} from '@/components/ui/sidebar'
import {
  Home,
  Package,
  BarChart2,
  Users,
  ShoppingCart,
  Truck,
  Database,
  ChevronRight,
  X,
  Search,
  Settings,
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useGlobalSearch, SearchResult } from "@/hooks/useGlobalSearch"
import { SearchResultsDropdown } from "@/components/ui/search-results-dropdown"
import { useState, useEffect } from 'react'

// Custom sidebar toggle that's always visible
const AlwaysVisibleSidebarToggle = () => {
  const { state, toggleSidebar } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <Button
      variant="outline"
      size="icon"
      className="absolute top-1/2 -translate-y-1/2 z-30 h-12 w-8 rounded-r-lg shadow-md bg-background border-l-0 hover:bg-accent transition-all duration-300"
      style={{
        left: isCollapsed ? '0' : 'var(--sidebar-width)',
        marginLeft: isCollapsed ? '0' : '-1px' // Slight adjustment for border overlap
      }}
      onClick={toggleSidebar}
    >
      <ChevronRight className={`h-5 w-5 transition-transform duration-300 ${isCollapsed ? 'rotate-0' : 'rotate-180'}`} />
      <span className="sr-only">Toggle Sidebar</span>
    </Button>
  )
}

// Create a separate component for the sidebar content
const SidebarContents = () => {
  const { toggleSidebar } = useSidebar()
  const pathname = usePathname()
  const router = useRouter()
  const { query, setQuery, results, isLoading, error, reset, getAllResults } = useGlobalSearch()
  const [showResults, setShowResults] = useState(false)
  const [favorites, setFavorites] = useState<Array<{id: string; name: string; iconName: string; favorited: boolean}>>([])
  
  // Function to map icon string to component
  const getIconComponent = (iconName: string) => {
    try {
      switch(iconName) {
        case 'Home': return Home;
        case 'ShoppingCart': return ShoppingCart;
        case 'Package': return Package;
        case 'BarChart3': 
        case 'BarChart2': return BarChart2;
        case 'Settings': return Settings;
        case 'Users': return Users;
        case 'Truck': return Truck;
        case 'Database': return Database;
        default: 
          console.warn(`Unknown icon name: ${iconName}, falling back to Package`);
          return Package;
      }
    } catch (error) {
      console.error('Error getting icon component:', error);
      return Package; // Fallback to Package icon
    }
  };
  
  // Load favorites when component mounts
  useEffect(() => {
    const loadFavorites = () => {
      try {
        if (typeof window !== 'undefined') {
          const savedFavorites = localStorage.getItem('dashboard-favorites')
          if (savedFavorites) {
            try {
              const favoritesData = JSON.parse(savedFavorites)
              if (Array.isArray(favoritesData)) {
                // Only keep the favorited items
                const filteredFavorites = favoritesData.filter((item: any) => 
                  item && typeof item === 'object' && item.favorited && item.id && item.name
                )
                setFavorites(filteredFavorites)
              } else {
                console.error('Favorites data is not an array:', favoritesData)
              }
            } catch (error) {
              console.error('Failed to parse favorites data:', error)
            }
          }
        }
      } catch (error) {
        console.error('Error loading favorites:', error)
      }
    }
    
    // Load favorites initially
    loadFavorites()
    
    // Setup event listener for storage changes
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'dashboard-favorites') {
        loadFavorites()
      }
    }
    
    // Setup event listener for custom event (when favorites change on the same page)
    const handleFavoritesChanged = () => {
      loadFavorites()
    }
    
    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('favoritesChanged', handleFavoritesChanged)
    
    // Clean up
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('favoritesChanged', handleFavoritesChanged)
    }
  }, [])
  
  // Recent accessed items
  const recentAccessed = [
    { id: "KD-1234", name: "Müller GmbH", type: "Kunde" },
    { id: "ORD-7345", name: "Auftrag #7345", type: "Auftrag" },
    { id: "KD-1156", name: "Schmidt AG", type: "Kunde" },
    { id: "ORD-7340", name: "Auftrag #7340", type: "Auftrag" },
    { id: "KD-1089", name: "Weber KG", type: "Kunde" },
  ]

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
    setShowResults(false)
  }

  const handleMenuItemClick = (id: string) => {
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
      // Add other menu navigation cases as needed
      default:
        // For other menu items that don't have routes yet
        console.log(`Clicked on menu item: ${id}`);
        break;
    }
  };
  
  return (
    <div className="relative z-10">
      <Sidebar>
        <SidebarHeader className="z-[1]">
          <div className="flex items-center px-2 py-2 relative">
            <div className="relative w-full">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Suchen..."
                className="w-full bg-background pl-8 pr-8"
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
              {favorites && favorites.length > 0 ? (
                <SidebarMenu>
                  {favorites.map((item) => {
                    // Safety check to ensure item has required properties
                    if (!item || !item.id || !item.name) {
                      return null;
                    }
                    
                    // Get icon component safely
                    const IconComponent = item.iconName ? getIconComponent(item.iconName) : Package;
                    
                    return (
                      <SidebarMenuItem key={item.id}>
                        <SidebarMenuButton asChild>
                          <Link 
                            href="#" 
                            onClick={(e) => {
                              e.preventDefault();
                              handleMenuItemClick(item.id);
                            }}
                          >
                            <IconComponent className="h-4 w-4" />
                            <span>{item.name}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              ) : (
                <div className="px-2 py-2 text-sm text-muted-foreground">
                  Keine Favoriten vorhanden.
                  Klicken Sie auf den Stern bei einem Menüpunkt, um ihn zu den Favoriten hinzuzufügen.
                </div>
              )}
            </SidebarGroupContent>
          </SidebarGroup>

          <SidebarGroup>
            <SidebarGroupLabel>Zuletzt aufgerufen</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {recentAccessed.map((item) => (
                  <SidebarMenuItem key={item.id}>
                    <SidebarMenuButton asChild>
                      <Link 
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          // Navigate based on the item type
                          if (item.type === "Kunde") {
                            router.push(`/customers/${item.id}`);
                          } else if (item.type === "Auftrag") {
                            router.push(`/orders/${item.id}`);
                          }
                        }}
                      >
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
    </div>
  )
}

interface MainLayoutProps {
  children: React.ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const pathname = usePathname()
  const isDashboard = pathname === '/dashboard'

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex pt-16">
        <SidebarProvider defaultOpen={isDashboard}>
          <MainLayoutContent>
            {children}
          </MainLayoutContent>
        </SidebarProvider>
      </div>
    </div>
  )
}

// New component that uses the sidebar context
const MainLayoutContent = ({ children }: { children: React.ReactNode }) => {
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"
  
  return (
    <div className="relative w-full">
      {/* Layer 1: Background */}
      {/* Already provided by the min-h-screen bg-background in the parent div */}
      
      {/* Layer 2: Header already at the top outside this container */}
      
      {/* Layer 3: Sidebar */}
      <SidebarContents />
      
      {/* Sidebar toggle button - positioned on the edge of the sidebar */}
      <AlwaysVisibleSidebarToggle />
      
      {/* Layer 4: Main content */}
      <main className="flex-1 p-6 relative" style={{ 
        position: 'absolute',
        left: isCollapsed ? '0' : 'var(--sidebar-width)',
        transform: 'none',
        width: isCollapsed ? '100%' : 'calc(100% - var(--sidebar-width))',
        maxWidth: '100%',
        zIndex: 0,
        transition: 'left 0.3s ease-in-out, width 0.3s ease-in-out'
      }}>
        <div className="mx-auto max-w-[1400px]">
          {children}
        </div>
      </main>
    </div>
  )
} 