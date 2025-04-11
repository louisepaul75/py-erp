"use client";

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertCircle, CheckCircle, Loader2, Play, FileText } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { de } from "date-fns/locale"; // Import German locale if needed

import type {
  SyncWorkflow,
  SyncJobStatus,
  TriggerWorkflowPayload,
} from "@/types/settings/api";
import { updateConnectionStatus, triggerWorkflowRun } from "@/lib/settings/system/api"; // Assuming api functions are here
import useAppTranslation from "@/hooks/useTranslationWrapper"; // Import translation hook
import { LogsDrawer } from './logs-drawer'; // Import the LogsDrawer

interface IntegrationGroupProps {
  connectionName: string;
  isEnabled: boolean;
  workflows: SyncWorkflow[];
  onStatusChange: (updatedData: any) => void; // Callback to update parent state
}

export function IntegrationGroup({
  connectionName,
  isEnabled,
  workflows,
  onStatusChange,
}: IntegrationGroupProps) {
  const [isLoadingToggle, setIsLoadingToggle] = useState(false);
  const [runningWorkflow, setRunningWorkflow] = useState<string | null>(null); // Track running workflow slug
  const [workflowParameters, setWorkflowParameters] = useState<Record<string, Record<string, boolean>>>({});
  const [selectedWorkflowForLogs, setSelectedWorkflowForLogs] = useState<SyncWorkflow | null>(null);
  const [isLogsDrawerOpen, setIsLogsDrawerOpen] = useState(false);
  const { toast } = useToast();
  const { t } = useAppTranslation("settings_system"); // Initialize translation

  // Handle toggling the connection status
  const handleToggle = async (checked: boolean) => {
    setIsLoadingToggle(true);
    try {
      const updatedData = await updateConnectionStatus(connectionName, checked);
      onStatusChange(updatedData); // Update parent state
      toast({
        title: t("connection_status_updated.title"),
        description: t("connection_status_updated.description", { connectionName }),
      });
    } catch (error: any) {
      console.error("Failed to update connection status:", error);
      toast({
        variant: "destructive",
        title: t("error_updating_connection.title"),
        description: error.message || t("error_updating_connection.description"),
      });
    } finally {
      setIsLoadingToggle(false);
    }
  };

  // Handle changes in workflow parameters (checkboxes)
  const handleParameterChange = (workflowSlug: string, paramName: string, checked: boolean) => {
    setWorkflowParameters(prev => ({
      ...prev,
      [workflowSlug]: {
        ...prev[workflowSlug],
        [paramName]: checked
      }
    }));
  };

  // Initialize parameters state when workflows load
  React.useEffect(() => {
    const initialParams: Record<string, Record<string, boolean>> = {};
    workflows.forEach(wf => {
      initialParams[wf.slug] = {};
      // Assuming parameters definition looks like: { "Debug Mode": { name: "debug_mode", type: "boolean" }, ... }
      // Adjust this based on your actual parameters definition structure in the model
      if (wf.parameters && typeof wf.parameters === 'object') {
         Object.entries(wf.parameters).forEach(([label, config]) => {
            if (typeof config === 'object' && config !== null && config.type === 'boolean') {
                initialParams[wf.slug][config.name] = false; // Default to false
            }
         });
      }
    });
    setWorkflowParameters(initialParams);
  }, [workflows]);

  // Handle running a workflow
  const handleRunWorkflow = async (workflow: SyncWorkflow) => {
    setRunningWorkflow(workflow.slug);
    try {
      const payload: TriggerWorkflowPayload = {
        parameters: workflowParameters[workflow.slug] || {}
      };
      const job = await triggerWorkflowRun(workflow.slug, payload);
      toast({
        title: t("workflow_triggered.title"),
        description: t("workflow_triggered.description", { workflowName: workflow.name, jobId: job.id }),
      });
      // Optionally, trigger a refresh of the data after a delay
      // setTimeout(() => /* refresh data */, 2000);
    } catch (error: any) {
      console.error("Failed to trigger workflow:", error);
      toast({
        variant: "destructive",
        title: t("error_triggering_workflow.title"),
        description: error.message || t("error_triggering_workflow.description"),
      });
    } finally {
      setRunningWorkflow(null);
    }
  };

  // Handle opening the logs drawer
  const handleShowLogs = (workflow: SyncWorkflow) => {
    setSelectedWorkflowForLogs(workflow);
    setIsLogsDrawerOpen(true);
  };

  // Helper to format last run time
  const formatLastRun = (isoDate: string | null) => {
    if (!isoDate) return t("never");
    try {
      return formatDistanceToNow(new Date(isoDate), {
        addSuffix: true,
        locale: de, // Use German locale
      });
    } catch {
      return t("invalid_date");
    }
  };

  // Helper to render status badge
  const renderStatusBadge = (status: SyncJobStatus | null) => {
    if (!status) {
      return <span className="text-xs text-gray-500">{t("status.no_runs")}</span>;
    }
    const statusStyles: Record<SyncJobStatus, string> = {
      SUCCESS: "text-green-600 bg-green-100",
      FAILURE: "text-red-600 bg-red-100",
      STARTED: "text-blue-600 bg-blue-100",
      PENDING: "text-yellow-600 bg-yellow-100",
      RETRY: "text-orange-600 bg-orange-100",
    };
    const Icon = {
      SUCCESS: CheckCircle,
      FAILURE: AlertCircle,
      STARTED: Loader2,
      PENDING: Loader2,
      RETRY: AlertCircle,
    }[status];

    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || "text-gray-600 bg-gray-100"}`}
      >
        <Icon className={`w-3 h-3 mr-1 ${status === 'STARTED' || status === 'PENDING' ? 'animate-spin' : ''}`} />
        {t(`status.${status.toLowerCase()}`)}
      </span>
    );
  };

  return (
    <Card className="mb-6">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <CardTitle className="text-xl font-medium capitalize">
            {connectionName.replace("_", " ")} {t("connection")}
          </CardTitle>
          <CardDescription>
             {t("manage_connection_and_workflows", { connectionName: connectionName.replace("_", " ") })}
          </CardDescription>
        </div>
        <div className="flex items-center space-x-2">
          <Label htmlFor={`toggle-${connectionName}`}>{isEnabled ? t("enabled") : t("disabled")}</Label>
          <Switch
            id={`toggle-${connectionName}`}
            checked={isEnabled}
            onCheckedChange={handleToggle}
            disabled={isLoadingToggle}
            aria-label={`Toggle ${connectionName} connection`}
          />
           {isLoadingToggle && <Loader2 className="h-4 w-4 animate-spin" />}
        </div>
      </CardHeader>
      <CardContent>
        {isEnabled ? (
          workflows.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[250px]">{t("workflow_name")}</TableHead>
                  <TableHead>{t("description")}</TableHead>
                  <TableHead>{t("last_status")}</TableHead>
                  <TableHead>{t("last_run")}</TableHead>
                  <TableHead>{t("parameters")}</TableHead>
                  <TableHead className="text-right">{t("actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workflows.map((wf) => (
                  <TableRow key={wf.slug}>
                    <TableCell className="font-medium">{wf.name}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {wf.description}
                    </TableCell>
                    <TableCell>{renderStatusBadge(wf.last_job_status)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatLastRun(wf.last_run_time)}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col space-y-1">
                       {workflowParameters[wf.slug] && Object.entries(workflowParameters[wf.slug]).map(([paramName, paramValue]) => {
                         // Find the parameter label from the definition
                         const paramDefinition = Object.entries(wf.parameters || {}).find(([_, config]) => 
                           typeof config === 'object' && config !== null && config.name === paramName
                         );
                         const paramLabel = paramDefinition ? paramDefinition[0] : paramName; 
                         return (
                           <div key={paramName} className="flex items-center space-x-2">
                             <Checkbox
                               id={`${wf.slug}-${paramName}`}
                               checked={paramValue}
                               onCheckedChange={(checked) =>
                                 handleParameterChange(wf.slug, paramName, !!checked)
                               }
                             />
                             <Label htmlFor={`${wf.slug}-${paramName}`} className="text-xs font-normal">
                               {paramLabel}
                             </Label>
                           </div>
                         );
                       })}
                       {(!workflowParameters[wf.slug] || Object.keys(workflowParameters[wf.slug]).length === 0) && (
                         <span className="text-xs text-gray-400">{t("no_parameters")}</span>
                       )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRunWorkflow(wf)}
                        disabled={runningWorkflow === wf.slug}
                      >
                        {runningWorkflow === wf.slug ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="mr-2 h-4 w-4" />
                        )}
                        {t("run")}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleShowLogs(wf)}
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        {t("logs")}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-sm text-muted-foreground italic">{t("no_workflows_for_connection")}</p>
          )
        ) : (
          <p className="text-sm text-muted-foreground italic">{t("connection_disabled_message")}</p>
        )}
      </CardContent>

      {/* Logs Drawer */} 
      <LogsDrawer 
        workflow={selectedWorkflowForLogs}
        isOpen={isLogsDrawerOpen}
        onClose={() => setIsLogsDrawerOpen(false)}
      />
    </Card>
  );
}
