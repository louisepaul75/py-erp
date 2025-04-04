"use client";

import React, { useState, useEffect } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

import type { SyncWorkflow, WorkflowLogRow } from "@/types/settings/api";
import { fetchWorkflowLogs } from "@/lib/settings/system/api";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface LogsDrawerProps {
  workflow: SyncWorkflow | null;
  isOpen: boolean;
  onClose: () => void;
}

function parseLogMetrics(details?: string): Record<string, number | string> | null {
  if (!details) return null;
  try {
    const data = JSON.parse(details);
    if (data && typeof data === 'object' && data.status === 'success') {
      return {
        Processed: data.records_processed ?? 'N/A',
        Succeeded: data.records_succeeded ?? 'N/A',
        Failed: data.records_failed ?? 'N/A',
      };
    }
  } catch (error) {
    // Log parsing error if needed, but don't crash
    // console.error("Failed to parse log details:", error);
  }
  return null;
}

export const LogsDrawer: React.FC<LogsDrawerProps> = ({
  workflow,
  isOpen,
  onClose,
}) => {
  const [logs, setLogs] = useState<WorkflowLogRow[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useAppTranslation("settings_system_logs");

  useEffect(() => {
    if (isOpen && workflow) {
      const loadLogs = async (slug: string) => {
        setLoading(true);
        setError(null);
        try {
          const fetchedLogs = await fetchWorkflowLogs(slug);
          setLogs(fetchedLogs);
        } catch (err) {
          setError(
            err instanceof Error ? err.message : "Failed to load workflow logs.",
          );
          setLogs([]);
        } finally {
          setLoading(false);
        }
      };
      loadLogs(workflow.slug);
    } else {
      setLogs([]);
      setLoading(false);
      setError(null);
    }
  }, [isOpen, workflow]);

  const getBadgeVariant = (
    level: WorkflowLogRow["level"],
  ): "default" | "destructive" | "secondary" | "outline" => {
    switch (level) {
      case "success":
        return "default";
      case "error":
        return "destructive";
      case "warning":
        return "secondary";
      case "info":
      default:
        return "outline";
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-[500px] sm:w-[640px] flex flex-col">
        <SheetHeader>
          <SheetTitle>
            {t("logs_for", { workflowName: workflow?.name || "..." } as any)}
          </SheetTitle>
          <SheetDescription>
            {t("recent_activity_for", {
              workflowName: workflow?.name || t("selected_workflow"),
            } as any)}
          </SheetDescription>
        </SheetHeader>
        <ScrollArea className="flex-grow pr-4 -mr-4">
          <div className="space-y-4 py-4">
            {loading && (
              <>
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </>
            )}
            {error && (
              <Alert variant="destructive">
                <Terminal className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            {!loading && !error && logs.length === 0 && (
              <p className="text-sm text-muted-foreground">{t("no_logs_found")}</p>
            )}
            {!loading && !error && logs.map((log) => {
              const metrics = log.level === 'success' ? parseLogMetrics(log.details) : null;
              return (
                <div key={log.id} className="p-3 border rounded-md text-sm">
                   <div className="flex justify-between items-start mb-1">
                     <span className="font-mono text-xs text-muted-foreground">
                       {log.timestamp}
                     </span>
                     <Badge variant={getBadgeVariant(log.level)} className="capitalize">
                       {log.level}
                     </Badge>
                   </div>
                   <p className="mb-2">{log.message}</p>
                   {metrics && (
                     <div className="text-xs text-muted-foreground space-x-2 mb-2">
                       {Object.entries(metrics).map(([key, value]) => (
                         <span key={key}>{key}: <strong>{value}</strong></span>
                       ))}
                     </div>
                   )}
                   {log.details && (
                     <Accordion type="single" collapsible className="w-full">
                       <AccordionItem value={`item-${log.id}`} className="border-none">
                         <AccordionTrigger className="text-xs py-1 hover:no-underline justify-start [&[data-state=open]>svg]:rotate-90">
                           Show Raw Log
                         </AccordionTrigger>
                         <AccordionContent className="mt-2 p-2 bg-muted rounded text-xs">
                           <pre className="whitespace-pre-wrap break-words">
                             {log.details}
                           </pre>
                         </AccordionContent>
                       </AccordionItem>
                     </Accordion>
                   )}
                </div>
              );
            })}
          </div>
        </ScrollArea>
        <SheetClose asChild>
          <Button variant="outline" className="mt-4">
            {t("close")}
          </Button>
        </SheetClose>
      </SheetContent>
    </Sheet>
  );
};
