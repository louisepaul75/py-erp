"use client"

import { useState } from "react"
import Link from "next/link"
import { BarChart3, Bell, Home, Package, Search, Settings, ShoppingCart, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <SidebarProvider>
      <div className="grid min-h-screen w-full grid-cols-[auto_1fr]">
        <Sidebar className="border-r">
          <SidebarHeader className="px-6 py-3">
            <h1 className="text-xl font-bold">pyERP</h1>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <Link href="/dashboard" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <Home className="h-5 w-5" />
                  <span>Dashboard</span>
                </Link>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <Link href="/inventory" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <Package className="h-5 w-5" />
                  <span>Inventory</span>
                </Link>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <Link href="/orders" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <ShoppingCart className="h-5 w-5" />
                  <span>Orders</span>
                </Link>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <Link href="/customers" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <Users className="h-5 w-5" />
                  <span>Customers</span>
                </Link>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <Link href="/reports" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <BarChart3 className="h-5 w-5" />
                  <span>Reports</span>
                </Link>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <Link href="/settings" className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                  <Settings className="h-5 w-5" />
                  <span>Settings</span>
                </Link>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter className="px-3 py-2">
            <SidebarTrigger />
          </SidebarFooter>
        </Sidebar>
        <div className="flex flex-col">
          <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-6">
            <div className="flex flex-1 items-center gap-4">
              <form className="flex-1 md:max-w-sm">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="search"
                    placeholder="Search..."
                    className="pl-10 h-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </form>
            </div>
            <Button size="icon" variant="outline" className="h-10 w-10 rounded-full">
              <Bell className="h-5 w-5" />
              <span className="sr-only">Toggle notifications</span>
            </Button>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6 md:gap-8 md:p-8">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card className="shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <div className="h-8 w-8 rounded-full bg-muted/30 flex items-center justify-center">
                    <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$45,231.89</div>
                  <p className="text-xs text-muted-foreground mt-1">+20.1% from last month</p>
                </CardContent>
              </Card>
              <Card className="shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">New Orders</CardTitle>
                  <div className="h-8 w-8 rounded-full bg-muted/30 flex items-center justify-center">
                    <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+124</div>
                  <p className="text-xs text-muted-foreground mt-1">+14% from last month</p>
                </CardContent>
              </Card>
              <Card className="shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Customers</CardTitle>
                  <div className="h-8 w-8 rounded-full bg-muted/30 flex items-center justify-center">
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">573</div>
                  <p className="text-xs text-muted-foreground mt-1">+6% from last month</p>
                </CardContent>
              </Card>
              <Card className="shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Inventory Items</CardTitle>
                  <div className="h-8 w-8 rounded-full bg-muted/30 flex items-center justify-center">
                    <Package className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1,324</div>
                  <p className="text-xs text-muted-foreground mt-1">+12 new items added</p>
                </CardContent>
              </Card>
            </div>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="w-full max-w-md grid grid-cols-3">
                <TabsTrigger value="overview" className="rounded-md">Overview</TabsTrigger>
                <TabsTrigger value="analytics" className="rounded-md">Analytics</TabsTrigger>
                <TabsTrigger value="reports" className="rounded-md">Reports</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="space-y-6 mt-6">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
                  <Card className="col-span-4 shadow-sm">
                    <CardHeader>
                      <CardTitle>Recent Orders</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        You have 12 new orders to process. Check the orders tab for more details.
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="col-span-3 shadow-sm">
                    <CardHeader>
                      <CardTitle>Inventory Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        5 items are low in stock. Check the inventory tab for more details.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              <TabsContent value="analytics" className="space-y-6 mt-6">
                <Card className="shadow-sm">
                  <CardHeader>
                    <CardTitle>Analytics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      View detailed analytics and reports for your business.
                    </p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="reports" className="space-y-6 mt-6">
                <Card className="shadow-sm">
                  <CardHeader>
                    <CardTitle>Reports</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Generate and download reports for your business.
                    </p>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
} 