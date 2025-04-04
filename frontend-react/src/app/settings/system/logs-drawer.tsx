"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, Info, Loader2, RefreshCw } from "lucide-react";
import { format, parseISO } from "date-fns";
import { de } from "date-fns/locale";

import type { SyncWorkflow, WorkflowLogRow } from "@/types/settings/api";
import { fetchWorkflowLogs } from "@/lib/settings/system/api";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface LogsDrawerProps {
  workflow: SyncWorkflow | null;
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
}

export function LogsDrawer({
  workflow,
  isOpen,
  onOpenChange,
}: LogsDrawerProps) {
  const [logs, setLogs] = useState<WorkflowLogRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useAppTranslation("settings_system_logs");

  const loadLogs = async (slug: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedLogs = await fetchWorkflowLogs(slug);
      setLogs(fetchedLogs);
    } catch (err: any) {
      console.error("Failed to fetch logs:", err);
      setError(err.message || t("error_fetching_logs"));
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && workflow) {
      loadLogs(workflow.slug);
    } else {
      setLogs([]);
      setError(null);
      setIsLoading(false);
    }
  }, [isOpen, workflow]);

  const levelIcons = useMemo(
    () => ({
      info: <Info className="h-4 w-4 text-blue-500" />,
      success: <CheckCircle className="h-4 w-4 text-green-500" />,
      warning: <AlertCircle className="h-4 w-4 text-yellow-500" />,
      error: <AlertCircle className="h-4 w-4 text-red-500" />,
    }),
    [],
  );

  const formatTimestamp = (isoDate: string) => {
    try {
      return format(parseISO(isoDate), "dd.MM.yyyy HH:mm:ss", { locale: de });
    } catch {
      return t("invalid_date");
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="sm:max-w-xl lg:max-w-3xl xl:max-w-4xl w-full">
        <SheetHeader>
          <SheetTitle>
            {t("logs_for", { workflowName: workflow?.name || "..." })}
          </SheetTitle>
          <SheetDescription>
            {t("recent_activity_for", {
              workflowName: workflow?.name || t("selected_workflow"),
            })}
          </SheetDescription>
        </SheetHeader>
        <div className="py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => workflow && loadLogs(workflow.slug)}
            disabled={isLoading}
            className="mb-4"
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            {t("refresh_logs")}
          </Button>

          {error && (
            <p className="text-red-600 text-sm mb-4">{t("error")} {error}</p>
          )}

          {isLoading && logs.length === 0 ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="ml-2 text-muted-foreground">{t("loading_logs")}...</p>
            </div>
          ) : logs.length > 0 ? (
            <div className="overflow-auto" style={{ maxHeight: "calc(100vh - 200px)" }}>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40px]">{/* Icon */}</TableHead>
                    <TableHead className="w-[150px]">{t("timestamp")}</TableHead>
                    <TableHead>{t("message")}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{levelIcons[log.level] || levelIcons.info}</TableCell>
                      <TableCell className="text-xs whitespace-nowrap">
                        {formatTimestamp(log.timestamp)}
                      </TableCell>
                      <TableCell>
                        <p className="text-sm font-medium">{log.message}</p>
                        {log.details && (
                          <pre className="mt-1 text-xs text-muted-foreground bg-gray-50 p-2 rounded overflow-auto whitespace-pre-wrap">
                            {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                          </pre>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            !isLoading && <p className="text-muted-foreground italic text-center py-10">{t("no_logs_found")}</p>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
