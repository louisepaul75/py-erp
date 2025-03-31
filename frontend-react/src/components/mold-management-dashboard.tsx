"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MoldTable from "@/components/mold/mold-table";
import SettingsDialog from "@/components/mold/settings-dialog";
import ActivityLog from "@/components/mold/activity-log";
import { Cog, History } from "lucide-react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Main dashboard component for the mold management system
 */
export default function MoldManagementDashboard() {
  // State to control the settings dialog
  const [showSettings, setShowSettings] = useState(false);

  const { t } = useAppTranslation("mold");

  // State for active tab
  const [activeTab, setActiveTab] = useState("molds");

  return (
    <div className="space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {t("mold_management_system")}
          </h1>
          <p className="text-muted-foreground mt-2">
            {t("mold_management_description")}
          </p>
        </div>
        <div className="flex gap-2 self-end md:self-auto">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowSettings(true)}
            className="h-10 w-10 md:h-10 md:w-10"
          >
            <Cog className="h-5 w-5" />
            <span className="sr-only">{t("settings_dialog_title")}</span>
          </Button>
        </div>
      </header>

      {/* Main content with tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="molds" className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-box"
            >
              <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
              <path d="m3.3 7 8.7 5 8.7-5" />
              <path d="M12 22V12" />
            </svg>
            <span>{t("tab_molds")}</span>
          </TabsTrigger>
          <TabsTrigger value="activity" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            <span>{t("tab_activity_log")}</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="molds" className="mt-6">
          <MoldTable />
        </TabsContent>

        <TabsContent value="activity" className="mt-6">
          <ActivityLog />
        </TabsContent>
      </Tabs>

      {/* Settings Dialog */}
      <SettingsDialog open={showSettings} onOpenChange={setShowSettings} />
    </div>
  );
}
