"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GoodsMovementTab } from "@/components/goods-movement/goods-movement-tab"
import { Plus, History } from "lucide-react"
import Link from "next/link"
import { Providers } from "@/components/providers"

// Interface für Tab-Daten mit Statusinformationen
interface TabData {
  id: string
  label: string
  allAssigned: boolean
}

function WarehousePageContent() {
  const [tabs, setTabs] = useState<TabData[]>([{ id: "1", label: "Tab 1", allAssigned: false }])
  const [activeTab, setActiveTab] = useState("1")

  const addTab = () => {
    const newTabId = (tabs.length + 1).toString()
    setTabs([
      ...tabs,
      {
        id: newTabId,
        label: `Tab ${newTabId}`,
        allAssigned: false,
      },
    ])
    setActiveTab(newTabId)
  }

  // Funktion zum Aktualisieren des Tab-Status
  const updateTabStatus = (tabId: string, allAssigned: boolean) => {
    setTabs((prevTabs) => prevTabs.map((tab) => (tab.id === tabId ? { ...tab, allAssigned } : tab)))
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl pb-20">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Warehouse Goods Movement</h1>
        <Link href="/history" className="flex items-center text-sm hover:underline">
          <History className="h-4 w-4 mr-1" />
          Verlauf anzeigen
        </Link>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center mb-4">
          <TabsList className="flex-grow overflow-x-auto p-1">
            {tabs.map((tab) => (
              <TabsTrigger key={tab.id} value={tab.id} className="min-w-[100px] relative">
                {tab.label}
                <span
                  className={`absolute top-1 right-1 w-2 h-2 rounded-full ${
                    tab.allAssigned ? "bg-green-500" : "bg-red-500"
                  }`}
                  aria-label={tab.allAssigned ? "Alle Artikel zugewiesen" : "Artikel zur Zuweisung verfügbar"}
                />
              </TabsTrigger>
            ))}
          </TabsList>
          <button
            onClick={addTab}
            className="ml-2 px-3 py-1 bg-primary text-primary-foreground rounded-md text-sm flex items-center"
          >
            <Plus className="h-4 w-4 mr-1" />
            Neuer Tab
          </button>
        </div>

        {tabs.map((tab) => (
          <TabsContent key={tab.id} value={tab.id} className="mt-0">
            <GoodsMovementTab tabId={tab.id} onStatusUpdate={(allAssigned) => updateTabStatus(tab.id, allAssigned)} />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}

export default function WarehousePage() {
  return (
    <Providers>
      <WarehousePageContent />
    </Providers>
  )
}

