// components/ProductDetail/TabsNavigation.tsx
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Eye, FileText, Settings, PlusCircle, Plus } from "lucide-react";

interface TabsNavigationProps {
  activeTab: string;
  setActiveTab: (value: string) => void;
  onAddVariant?: () => void;
}

export default function TabsNavigation({ 
  activeTab, 
  setActiveTab,
  onAddVariant 
}: TabsNavigationProps) {
  console.log("TabsNavigation rendering with onAddVariant:", !!onAddVariant);
  
  return (
    <div className="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 lg:px-6">
      <div className="flex items-center justify-between h-14">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="">
          <TabsList className="rounded-full bg-slate-100 dark:bg-slate-800 p-1 h-9">
            <TabsTrigger
              value="mutter"
              className="rounded-full data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=inactive]:bg-transparent data-[state=inactive]:text-slate-600 dark:data-[state=inactive]:text-slate-300 px-4 py-1 text-sm"
            >
              Mutter
            </TabsTrigger>
            <TabsTrigger
              value="varianten"
              className="rounded-full data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=inactive]:bg-transparent data-[state=inactive]:text-slate-600 dark:data-[state=inactive]:text-slate-300 px-4 py-1 text-sm"
            >
              Varianten
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-2">
          {onAddVariant && (
            <Button 
              variant="outline" 
              size="sm" 
              className="rounded-full bg-red-100"
              onClick={onAddVariant}
            >
              <PlusCircle className="h-4 w-4 mr-1" />
              New Variant
            </Button>
          )}
          <Button variant="outline" size="sm" className="rounded-full">
            <Eye className="h-4 w-4 mr-1" />
            Vorschau
          </Button>
          <Button variant="outline" size="sm" className="rounded-full">
            <FileText className="h-4 w-4 mr-1" />
            Exportieren
          </Button>
          <Button variant="outline" size="sm" className="rounded-full">
            <Settings className="h-4 w-4 mr-1" />
            Einstellungen
          </Button>
        </div>
      </div>
    </div>
  );
}