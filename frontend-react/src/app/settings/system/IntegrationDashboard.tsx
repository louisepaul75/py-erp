"use client";

import React, { useState, useEffect } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal, Loader2 } from "lucide-react";
import { IntegrationGroup } from "./IntegrationGroup";
import { fetchSystemIntegrationData } from "@/lib/settings/system/api";
import type { SystemIntegrationData } from "@/types/settings/api";
import useAppTranslation from "@/hooks/useTranslationWrapper";

export default function IntegrationDashboard() {
  const [integrationData, setIntegrationData] =
    useState<SystemIntegrationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useAppTranslation("settings_system");

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchSystemIntegrationData();
        setIntegrationData(data);
      } catch (err: any) {
        console.error("Failed to load integration data:", err);
        setError(err.message || t("error_loading_data"));
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [t]);

  const handleStatusChange = (updatedData: SystemIntegrationData) => {
    setIntegrationData(updatedData);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-10">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="ml-2 text-muted-foreground">{t("loading_integrations")}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <Terminal className="h-4 w-4" />
        <AlertTitle>{t("error")}</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!integrationData || Object.keys(integrationData).length === 0) {
    return <p className="text-muted-foreground italic">{t("no_integrations_found")}</p>;
  }

  return (
    <div className="space-y-4">
      {Object.entries(integrationData).map(
        ([connectionName, { enabled, workflows }]) => (
          <IntegrationGroup
            key={connectionName}
            connectionName={connectionName}
            isEnabled={enabled}
            workflows={workflows}
            onStatusChange={handleStatusChange}
          />
        ),
      )}
    </div>
  );
}
