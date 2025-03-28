"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { fetchEndpointLogs } from "@/lib/settings/system/api";
import type { ApiEndpoint, LogEntry, Automation } from "@/types/settings/api";
import {
  X,
  RefreshCw,
  Download,
  AlertCircle,
  Info,
  CheckCircle,
} from "lucide-react";
import type { JSX } from "react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface LogsDrawerProps {
  endpoint: ApiEndpoint | Automation;
  open: boolean;
  onClose: () => void;
}

export function LogsDrawer({ endpoint, open, onClose }: LogsDrawerProps) {
  const {
    data: logs = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["endpointLogs", endpoint.id],
    queryFn: () => fetchEndpointLogs(endpoint.id),
    enabled: open,
  });

  const { t } = useAppTranslation("settings_system");

  const getLogIcon = (level: string) => {
    switch (level) {
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case "info":
        return <Info className="h-4 w-4 text-blue-500" />;
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getLogClass = (level: string) => {
    switch (level) {
      case "error":
        return "bg-red-50 border-red-200";
      case "warning":
        return "bg-yellow-50 border-yellow-200";
      case "info":
        return "bg-blue-50 border-blue-200";
      case "success":
        return "bg-green-50 border-green-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-md md:max-w-lg lg:max-w-xl">
        <SheetHeader className="flex flex-row items-center justify-between">
          <div>
            <SheetTitle>Logs: {endpoint.name}</SheetTitle>
            <SheetDescription>
              View all logs for this{" "}
              {"url" in endpoint ? "API endpoint" : "automation"}
            </SheetDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              title="Refresh logs"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" title="Download logs">
              <Download className="h-4 w-4" />
            </Button>
            <SheetClose asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <X className="h-4 w-4" />
              </Button>
            </SheetClose>
          </div>
        </SheetHeader>

        <div className="mt-6">
          <Tabs defaultValue="all">
            <TabsList className="grid grid-cols-4 mb-4">
              <TabsTrigger value="all">{t("all")}</TabsTrigger>
              <TabsTrigger value="error">{t("errors")}</TabsTrigger>
              <TabsTrigger value="warning">{t("warnings")}</TabsTrigger>
              <TabsTrigger value="info">{t("info")}</TabsTrigger>
            </TabsList>

            <TabsContent value="all">
              <LogsList
                logs={logs}
                isLoading={isLoading}
                getLogIcon={getLogIcon}
                getLogClass={getLogClass}
              />
            </TabsContent>

            <TabsContent value="error">
              <LogsList
                logs={logs.filter((log) => log.level === "error")}
                isLoading={isLoading}
                getLogIcon={getLogIcon}
                getLogClass={getLogClass}
              />
            </TabsContent>

            <TabsContent value="warning">
              <LogsList
                logs={logs.filter((log) => log.level === "warning")}
                isLoading={isLoading}
                getLogIcon={getLogIcon}
                getLogClass={getLogClass}
              />
            </TabsContent>

            <TabsContent value="info">
              <LogsList
                logs={logs.filter(
                  (log) => log.level === "info" || log.level === "success"
                )}
                isLoading={isLoading}
                getLogIcon={getLogIcon}
                getLogClass={getLogClass}
              />
            </TabsContent>
          </Tabs>
        </div>
      </SheetContent>
    </Sheet>
  );
}

interface LogsListProps {
  logs: LogEntry[];
  isLoading: boolean;
  getLogIcon: (level: string) => JSX.Element;
  getLogClass: (level: string) => string;
}

function LogsList({ logs, isLoading, getLogIcon, getLogClass }: LogsListProps) {
  if (isLoading) {
    return <div className="text-center py-8">Loading logs...</div>;
  }

  if (logs.length === 0) {
    return <div className="text-center py-8">No logs found</div>;
  }

  return (
    <ScrollArea className="h-[calc(100vh-220px)]">
      <div className="space-y-3">
        {logs.map((log) => (
          <div
            key={log.id}
            className={`p-3 rounded-md border ${getLogClass(log.level)}`}
          >
            <div className="flex items-start gap-2">
              <div className="mt-0.5">{getLogIcon(log.level)}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <Badge variant="outline">{log.level}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="mt-2 text-sm">{log.message}</p>
                {log.details && (
                  <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto">
                    {typeof log.details === "string"
                      ? log.details
                      : JSON.stringify(log.details, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
