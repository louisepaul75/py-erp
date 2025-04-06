// components/ProductDetail/VariantenTabs.tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DetailsTab from "./DetailsTab";
import TeileTab from "@/components/teile-tab";
import BilderTab from "@/components/bilder-tab";
import GewogenTab from "@/components/gewogen-tab";
import LagerorteTab from "@/components/lagerorte-tab";
import UmsatzeTab from "@/components/umsatze-tab";
import BewegungenTab from "@/components/bewegungen-tab";
import { Card } from "@/components/ui/card";

interface VariantenTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  detailsTab: React.ReactNode; // Accept DetailsTab as a prop
}

export default function VariantenTabs({
  activeTab,
  onTabChange,
  detailsTab, // Destructure detailsTab
}: VariantenTabsProps) {
  return (
    <Card>
      <Tabs
        defaultValue="details"
        value={activeTab}
        onValueChange={onTabChange}
        className="w-full"
      >
        <div className="border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
          <TabsList className="bg-slate-50 dark:bg-slate-800/50 h-auto p-2 rounded-none flex-nowrap">
            <TabsTrigger
              value="details"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Details
            </TabsTrigger>
            <TabsTrigger
              value="teile"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Teile
            </TabsTrigger>
            <TabsTrigger
              value="bilder"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Bilder
            </TabsTrigger>
            <TabsTrigger
              value="gewogen"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Gewogen
            </TabsTrigger>
            <TabsTrigger
              value="lagerorte"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Lagerorte
            </TabsTrigger>
            <TabsTrigger
              value="umsatze"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Umsätze
            </TabsTrigger>
            <TabsTrigger
              value="bewegungen"
              className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
            >
              Bewegungen
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="details" className="p-0 m-0">
        {detailsTab}
        </TabsContent>
        <TabsContent value="teile" className="p-0 m-0">
          <TeileTab />
        </TabsContent>
        <TabsContent value="bilder" className="p-0 m-0">
          <BilderTab />
        </TabsContent>
        <TabsContent value="gewogen" className="p-0 m-0">
          <GewogenTab />
        </TabsContent>
        <TabsContent value="lagerorte" className="p-0 m-0">
          <LagerorteTab />
        </TabsContent>
        <TabsContent value="umsatze" className="p-0 m-0">
          <UmsatzeTab />
        </TabsContent>
        <TabsContent value="bewegungen" className="p-0 m-0">
          <BewegungenTab />
        </TabsContent>
      </Tabs>
    </Card>
  );
}
