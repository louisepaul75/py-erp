// components/Header.tsx
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  Menu,
  X,
  Search,
  Bell,
  HelpCircle,
  Sun,
  Moon,
  Plus,
} from "lucide-react";

interface HeaderProps {
  showSidebar: boolean;
  setShowSidebar: (value: boolean) => void;
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

export default function Header({
  showSidebar,
  setShowSidebar,
  searchTerm,
  setSearchTerm,
  darkMode,
  toggleDarkMode,
}: HeaderProps) {
  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden h-9 w-9 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          onClick={() => setShowSidebar(!showSidebar)}
        >
          {showSidebar ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
        <h1 className="text-xl font-semibold hidden md:block text-slate-900 dark:text-slate-100">Produktverwaltung</h1>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative hidden md:block">
          <Input
            className="w-64 pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500 text-slate-900 dark:text-slate-100"
            placeholder="Suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2">
            <Search className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </div>
          {searchTerm && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              onClick={() => setSearchTerm("")}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-9 w-9 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" 
          onClick={toggleDarkMode}
        >
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-9 w-9 rounded-full relative text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500"></span>
        </Button>
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-9 w-9 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
        >
          <HelpCircle className="h-5 w-5" />
        </Button>
        <Separator orientation="vertical" className="h-8 bg-slate-200 dark:bg-slate-700" />
        <Button className="rounded-full bg-blue-600 hover:bg-blue-700 text-white">
          <Plus className="h-4 w-4 mr-2" />
          Neues Produkt
        </Button>
      </div>
    </header>
  );
}