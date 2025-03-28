"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { fetchEndpointChanges } from "@/lib/settings/system/api";
import type {
  ApiEndpoint,
  ChangeEntry,
  Automation,
} from "@/types/settings/api";
import { RefreshCw, Download, Plus, Minus, Edit } from "lucide-react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface ChangesModalProps {
  endpoint: ApiEndpoint | Automation;
  open: boolean;
  onClose: () => void;
}

export function ChangesModal({ endpoint, open, onClose }: ChangesModalProps) {
  const {
    data: changes = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["endpointChanges", endpoint.id],
    queryFn: () => fetchEndpointChanges(endpoint.id),
    enabled: open,
  });

  const { t } = useAppTranslation("settings_system");

  const getChangeIcon = (type: string) => {
    switch (type) {
      case "added":
        return <Plus className="h-4 w-4 text-green-500" />;
      case "removed":
        return <Minus className="h-4 w-4 text-red-500" />;
      case "modified":
        return <Edit className="h-4 w-4 text-blue-500" />;
      default:
        return <Edit className="h-4 w-4" />;
    }
  };

  const getChangeClass = (type: string) => {
    switch (type) {
      case "added":
        return "bg-green-50 border-green-200";
      case "removed":
        return "bg-red-50 border-red-200";
      case "modified":
        return "bg-blue-50 border-blue-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md md:max-w-lg lg:max-w-xl">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle>
                {t("changes")}: {endpoint.name}
              </DialogTitle>
              <DialogDescription>
                {t("view_all_changes")}{" "}
                {"url" in endpoint ? "API endpoint" : "automation"}
              </DialogDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                title="Refresh changes"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" title={t("download_changes")}>
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-4">
          <Tabs defaultValue="all">
            <TabsList className="grid grid-cols-4 mb-4">
              <TabsTrigger value="all">{t("all")}</TabsTrigger>
              <TabsTrigger value="added">{t("added")}</TabsTrigger>
              <TabsTrigger value="removed">{t("removed")}</TabsTrigger>
              <TabsTrigger value="modified">{t("modified")}</TabsTrigger>
            </TabsList>

            <TabsContent value="all">
              <ChangesList
                changes={changes}
                isLoading={isLoading}
                getChangeIcon={getChangeIcon}
                getChangeClass={getChangeClass}
              />
            </TabsContent>

            <TabsContent value="added">
              <ChangesList
                changes={changes.filter((change) => change.type === "added")}
                isLoading={isLoading}
                getChangeIcon={getChangeIcon}
                getChangeClass={getChangeClass}
              />
            </TabsContent>

            <TabsContent value="removed">
              <ChangesList
                changes={changes.filter((change) => change.type === "removed")}
                isLoading={isLoading}
                getChangeIcon={getChangeIcon}
                getChangeClass={getChangeClass}
              />
            </TabsContent>

            <TabsContent value="modified">
              <ChangesList
                changes={changes.filter((change) => change.type === "modified")}
                isLoading={isLoading}
                getChangeIcon={getChangeIcon}
                getChangeClass={getChangeClass}
              />
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface ChangesListProps {
  changes: ChangeEntry[];
  isLoading: boolean;
  getChangeIcon: (type: string) => JSX.Element;
  getChangeClass: (type: string) => string;
}

function ChangesList({
  changes,
  isLoading,
  getChangeIcon,
  getChangeClass,
}: ChangesListProps) {
  const { t } = useAppTranslation("settings_system");

  if (isLoading) {
    return <div className="text-center py-8">{t("loading_changes")}</div>;
  }

  if (changes.length === 0) {
    return <div className="text-center py-8">{t("no_change")}</div>;
  }

  return (
    <ScrollArea className="h-[calc(100vh-300px)]">
      <div className="space-y-3">
        {changes.map((change) => (
          <div
            key={change.id}
            className={`p-3 rounded-md border ${getChangeClass(change.type)}`}
          >
            <div className="flex items-start gap-2">
              <div className="mt-0.5">{getChangeIcon(change.type)}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{change.entity}</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(change.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="mt-1 text-sm">{change.description}</p>
                {change.details && (
                  <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                    {change.type === "modified" &&
                      change.details.before &&
                      change.details.after && (
                        <>
                          <div>
                            <div className="text-xs font-medium mb-1">
                              {t("before")}:
                            </div>
                            <pre className="p-2 bg-muted rounded text-xs overflow-x-auto">
                              {typeof change.details.before === "string"
                                ? change.details.before
                                : JSON.stringify(
                                    change.details.before,
                                    null,
                                    2
                                  )}
                            </pre>
                          </div>
                          <div>
                            <div className="text-xs font-medium mb-1">
                            {t("after")}:
                            </div>
                            <pre className="p-2 bg-muted rounded text-xs overflow-x-auto">
                              {typeof change.details.after === "string"
                                ? change.details.after
                                : JSON.stringify(change.details.after, null, 2)}
                            </pre>
                          </div>
                        </>
                      )}
                    {(change.type === "added" ||
                      change.type === "removed" ||
                      !change.details.before) && (
                      <pre className="p-2 bg-muted rounded text-xs overflow-x-auto col-span-2">
                        {typeof change.details === "string"
                          ? change.details
                          : JSON.stringify(change.details, null, 2)}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
