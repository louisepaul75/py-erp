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
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useGlobalSearch, SearchResult } from "@/hooks/useGlobalSearch"
import { SearchResultsDropdown } from "@/components/ui/search-results-dropdown"
import { useState } from 'react'

// Custom sidebar toggle that's always visible
const AlwaysVisibleSidebarToggle = () => {
  const { state, toggleSidebar } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <Button
      variant="outline"
      size="icon"
      className="absolute top-1/2 -translate-y-1/2 -right-8 z-[60] h-12 w-8 rounded-r-lg shadow-md bg-background border-l-0 hover:bg-accent transition-all duration-300"
      onClick={toggleSidebar}
    >
      <ChevronRight className={`h-5 w-5 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} />
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
  
  return (
    <div className="relative">
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
              <div className="px-2 py-2 text-sm text-muted-foreground">
                Keine Favoriten vorhanden.
                Klicken Sie auf den Stern bei einem Menüpunkt, um ihn zu den Favoriten hinzuzufügen.
              </div>
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
      <AlwaysVisibleSidebarToggle />
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
          <SidebarContents />
          <main className="flex-1 p-6 relative z-10" style={{ 
            marginLeft: 'var(--sidebar-width)',
          }}>
            <div className="mx-auto max-w-7xl">
              {children}
            </div>
          </main>
        </SidebarProvider>
      </div>
    </div>
  )
} 