// components/MainSidebar.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  ChevronLeft,
  ChevronRight,
  Home,
  Package,
  BarChart2,
  Users,
  ShoppingCart,
  Truck,
  Database,
  MoreHorizontal,
  X,
} from "lucide-react";

interface MainSidebarProps {
  showSidebar: boolean;
  onHideSidebar?: () => void;
}

export default function MainSidebar({ showSidebar, onHideSidebar }: MainSidebarProps) {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);

  return (
    <div
      className={`${sidebarExpanded ? "w-64" : "w-20"} bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-all duration-300 ease-in-out ${showSidebar ? "" : "hidden md:flex"} relative`}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold mr-2">
            IM
          </div>
          {sidebarExpanded && <span className="font-semibold text-lg">Inventory</span>}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
            onClick={() => setSidebarExpanded(!sidebarExpanded)}
          >
            {sidebarExpanded ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 md:block"
            onClick={onHideSidebar}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Hide Sidebar</span>
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-4">
        <div className="px-3 mb-6">
          <Button className="w-full justify-start gap-3 bg-blue-50 hover:bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 dark:text-blue-400 h-11 rounded-xl">
            <Package className="h-5 w-5" />
            {sidebarExpanded && <span>Produkte</span>}
          </Button>
        </div>
        <div className="px-3 space-y-1">
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <Home className="h-5 w-5" />
            {sidebarExpanded && <span>Dashboard</span>}
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <BarChart2 className="h-5 w-5" />
            {sidebarExpanded && <span>Berichte</span>}
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <Users className="h-5 w-5" />
            {sidebarExpanded && <span>Kunden</span>}
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <ShoppingCart className="h-5 w-5" />
            {sidebarExpanded && <span>Bestellungen</span>}
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <Truck className="h-5 w-5" />
            {sidebarExpanded && <span>Lieferungen</span>}
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 h-11 rounded-xl"
          >
            <Database className="h-5 w-5" />
            {sidebarExpanded && <span>Lager</span>}
          </Button>
        </div>
      </div>

      {/* User */}
      <div className="border-t border-slate-200 dark:border-slate-800 p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              JD
            </AvatarFallback>
          </Avatar>
          {sidebarExpanded && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">John Doe</p>
              <p className="text-xs text-slate-500 dark:text-slate-400 truncate">admin@example.com</p>
            </div>
          )}
          {sidebarExpanded && (
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}