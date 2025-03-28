"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  RefreshCw,
  Play,
  Pause,
  Calendar,
  Settings,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";
import { ScheduleModal } from "./schedule-modal";
import { LogsDrawer } from "./logs-drawer";
import { ChangesModal } from "./changes-modal";
import { fetchAutomations } from "@/lib/settings/system/api";
import type { Automation } from "@/types/settings/api";
import useAppTranslation from "@/hooks/useTranslationWrapper";

export function AutomationsList() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAutomation, setSelectedAutomation] =
    useState<Automation | null>(null);
  const [scheduleOpen, setScheduleOpen] = useState(false);
  const [logsOpen, setLogsOpen] = useState(false);
  const [changesOpen, setChangesOpen] = useState(false);

  const {
    data: automations = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["automations"],
    queryFn: fetchAutomations,
  });

  const filteredAutomations = automations.filter(
    (automation) =>
      automation.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      automation.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSchedule = (automation: Automation) => {
    setSelectedAutomation(automation);
    setScheduleOpen(true);
  };

  const { t } = useAppTranslation("settings_system");

  const handleViewLogs = (automation: Automation) => {
    setSelectedAutomation(automation);
    setLogsOpen(true);
  };

  const handleViewChanges = (automation: Automation) => {
    setSelectedAutomation(automation);
    setChangesOpen(true);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return (
          <Badge className="bg-green-500">
            <CheckCircle className="h-3 w-3 mr-1" /> {t("running")}
          </Badge>
        );
      case "stopped":
        return (
          <Badge variant="secondary">
            <Pause className="h-3 w-3 mr-1" /> {t("stopped")}
          </Badge>
        );
      case "failed":
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" /> {t("failed")}
          </Badge>
        );
      case "scheduled":
        return (
          <Badge variant="outline" className="bg-blue-100 text-blue-800">
            <Clock className="h-3 w-3 mr-1" /> {t("scheduled")}
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle>{t("django_erp_automations")}</CardTitle>
              <CardDescription>
                {t("manage_automations")}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-full md:w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder={t("search_automations")}
                  className="pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => refetch()}
                title="Refresh"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("name")}</TableHead>
                  <TableHead className="hidden md:table-cell">
                  {t("description")}
                  </TableHead>
                  <TableHead>{t("status")}</TableHead>
                  <TableHead>{t("schedule")}</TableHead>
                  <TableHead>{t("last_run")}</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                    {t("loading_automations")}
                    </TableCell>
                  </TableRow>
                ) : filteredAutomations.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                    {t("no_automations_found")}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredAutomations.map((automation) => (
                    <TableRow key={automation.id}>
                      <TableCell className="font-medium">
                        {automation.name}
                      </TableCell>
                      <TableCell className="hidden md:table-cell truncate max-w-[200px]">
                        {automation.description}
                      </TableCell>
                      <TableCell>{getStatusBadge(automation.status)}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-2" />
                          <span>{automation.schedule}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span>
                            {new Date(automation.lastRun).toLocaleDateString()}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(automation.lastRun).toLocaleTimeString()}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex flex-wrap justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewLogs(automation)}
                          >
                            {t("logs")}
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewChanges(automation)}
                          >
                             {t("changes")}
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSchedule(automation)}
                          >
                            <Settings className="h-4 w-4 mr-1" />  {t("schedule")}
                          </Button>
                          {automation.status === "running" ? (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-yellow-600"
                            >
                              <Pause className="h-4 w-4 mr-1" />  {t("pause")}
                            </Button>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-green-600"
                            >
                              <Play className="h-4 w-4 mr-1" /> {t("start")}
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {selectedAutomation && (
        <>
          <ScheduleModal
            automation={selectedAutomation}
            open={scheduleOpen}
            onClose={() => setScheduleOpen(false)}
          />
          <LogsDrawer
            endpoint={selectedAutomation}
            open={logsOpen}
            onClose={() => setLogsOpen(false)}
          />
          <ChangesModal
            endpoint={selectedAutomation}
            open={changesOpen}
            onClose={() => setChangesOpen(false)}
          />
        </>
      )}
    </>
  );
}
