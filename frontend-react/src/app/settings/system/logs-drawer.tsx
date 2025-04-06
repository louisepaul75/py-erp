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
import { cn } from "@/lib/utils";

import type { SyncWorkflow, WorkflowLogRow } from "@/types/settings/api";
import { fetchWorkflowLogs } from "@/lib/settings/system/api";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface LogsDrawerProps {
  workflow: SyncWorkflow | null;
  isOpen: boolean;
  onClose: () => void;
}

interface LogMetrics {
  processed: number | string;
  created: number | string;
  updated: number | string;
  failed: number | string;
  startTime: string | null;
  duration: string | null;
}

// Helper to parse metrics from plain text log details
function parseLogMetrics(details?: string): LogMetrics | null {
  if (!details) return null;

  const metrics: LogMetrics = {
    processed: 'N/A',
    created: 'N/A',
    updated: 'N/A',
    failed: 'N/A',
    startTime: null,
    duration: null,
  };
  let foundAny = false;

  // Regex for start time
  const startTimeMatch = details.match(/Starting sync at (.*?)\.\.\./);
  if (startTimeMatch && startTimeMatch[1]) {
    metrics.startTime = startTimeMatch[1].trim();
    foundAny = true;
  }

  // Regex for duration
  const durationMatch = details.match(/Sync completed successfully in ([\d.]+) seconds/);
  if (durationMatch && durationMatch[1]) {
    metrics.duration = `${durationMatch[1]} seconds`;
    foundAny = true;
  }

  // Regex for statistics (check line by line after "Statistics:")
  const statsHeaderIndex = details.indexOf('Statistics:');
  if (statsHeaderIndex !== -1) {
      const statsBlock = details.substring(statsHeaderIndex);
      // Example: Processed: 113
      const processedMatch = statsBlock.match(/Processed:\s*(\d+)/);
      if (processedMatch && processedMatch[1]) {
          metrics.processed = parseInt(processedMatch[1], 10);
          foundAny = true;
      }
      // Example: Created: 0
      const createdMatch = statsBlock.match(/Created:\s*(\d+)/);
      if (createdMatch && createdMatch[1]) {
          metrics.created = parseInt(createdMatch[1], 10);
          foundAny = true;
      }
      // Example: Updated: 101
      const updatedMatch = statsBlock.match(/Updated:\s*(\d+)/);
      if (updatedMatch && updatedMatch[1]) {
          metrics.updated = parseInt(updatedMatch[1], 10);
          foundAny = true;
      }
      // Example: Failed: 12
      const failedMatch = statsBlock.match(/Failed:\s*(\d+)/);
      if (failedMatch && failedMatch[1]) {
          metrics.failed = parseInt(failedMatch[1], 10);
          foundAny = true;
      }
  }

  // Return metrics only if something was found
  return foundAny ? metrics : null;
}

// Helper to format ISO-like date string from logs
function formatLogDateTime(dateString: string | null): string {
  if (!dateString) return 'N/A';
  try {
    // Attempt to parse potentially non-standard format
    // Replace space before timezone offset if present
    const parsableDateString = dateString.replace(/ (\+\d{2}:\d{2})$/, '$1');
    return new Date(parsableDateString).toLocaleString();
  } catch {
    return dateString; // Fallback to original string if parsing fails
  }
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
              const metrics = parseLogMetrics(log.details);
              return (
                <div key={log.id} className="p-3 border rounded-md text-sm">
                   <div className="flex justify-between items-start mb-1">
                     <span className="font-mono text-xs text-muted-foreground">
                       {log.timestamp}
                     </span>
                     <Badge 
                       variant={getBadgeVariant(log.level)}
                       className={cn(
                         "capitalize",
                         {
                           "bg-[var(--status-success)] text-white border-transparent": log.level === 'success',
                           "bg-[var(--status-error)] text-white border-transparent": log.level === 'error',
                         }
                       )}
                     >
                       {log.level}
                     </Badge>
                   </div>
                   <p className="mb-2">{log.message}</p>
                   {metrics && (
                     <div className="text-xs text-muted-foreground space-y-1 mb-2">
                       <div>
                         <strong>Statistics:</strong>
                         <span className="ml-2">Processed: <strong>{metrics.processed}</strong></span>
                         <span className="ml-2">Created: <strong>{metrics.created}</strong></span>
                         <span className="ml-2">Updated: <strong>{metrics.updated}</strong></span>
                         <span className="ml-2">Failed: <strong>{metrics.failed}</strong></span>
                       </div>
                       {(metrics.startTime || metrics.duration) && (
                         <div>
                           <strong>Time:</strong>
                           {metrics.startTime && <span className="ml-2">Start: <strong>{formatLogDateTime(metrics.startTime)}</strong></span>}
                           {metrics.duration && <span className="ml-2">Duration: <strong>{metrics.duration}</strong></span>}
                         </div>
                       )}
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
