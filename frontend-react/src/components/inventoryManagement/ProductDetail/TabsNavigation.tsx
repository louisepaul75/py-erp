// components/ProductDetail/TabsNavigation.tsx
import { Button } from "@/components/ui/button";
import { Eye, FileText, Settings } from "lucide-react";

interface TabsNavigationProps {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

export default function TabsNavigation({ activeTab, setActiveTab }: TabsNavigationProps) {
  return (
    <div className="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 lg:px-6">
      <div className="flex items-center h-14">
        <Button
          variant={activeTab === "mutter" ? "default" : "ghost"}
          className={`rounded-full ${activeTab === "mutter" ? "bg-blue-600 text-white hover:bg-blue-700" : ""}`}
          onClick={() => setActiveTab("mutter")}
        >
          Mutter
        </Button>
        <Button
          variant={activeTab === "varianten" ? "default" : "ghost"}
          className={`rounded-full ml-2 ${activeTab === "varianten" ? "bg-blue-600 text-white hover:bg-blue-700" : ""}`}
          onClick={() => setActiveTab("varianten")}
        >
          Varianten
        </Button>
        <div className="ml-auto flex items-center gap-2">
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