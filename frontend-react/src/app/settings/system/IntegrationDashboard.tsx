"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ApiEndpointsList } from "./api-endpoints-list";
import { AutomationsList } from "./automations-list";
import useAppTranslation from "@/hooks/useTranslationWrapper";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("endpoints");
  const { t } = useAppTranslation("settings_system");
  return (
    <Tabs
      defaultValue="endpoints"
      className="w-full"
      onValueChange={setActiveTab}
    >
      <TabsList className="grid w-full grid-cols-2 mb-8">
        <TabsTrigger value="endpoints">{t("api_endpoints")}</TabsTrigger>
        <TabsTrigger value="automations">{t("automations")}</TabsTrigger>
      </TabsList>

      <TabsContent value="endpoints" className="space-y-4">
        <ApiEndpointsList />
      </TabsContent>

      <TabsContent value="automations" className="space-y-4">
        <AutomationsList />
      </TabsContent>
    </Tabs>
  );
}
