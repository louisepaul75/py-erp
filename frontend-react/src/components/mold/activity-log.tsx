"use client";

import React, { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  RefreshCw,
  X,
  ChevronDown,
  ChevronRight,
  ArrowRight,
} from "lucide-react";
import { useActivityLog } from "@/hooks/mold/use-activity-log";
import { ActivityType, EntityType } from "@/types/mold/activity-log";
import { format, parseISO, isAfter, isBefore, subDays } from "date-fns";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * ActivityLog component displays a table of activity logs with filtering and search capabilities
 */
export default function ActivityLog() {
  // Fetch activity logs
  const { data: activityLogs, isLoading, error } = useActivityLog();

  // State for search term
  const [searchTerm, setSearchTerm] = useState("");

  // State for expanded rows
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  const { t } = useAppTranslation("mold");

  // State for filters
  const [filters, setFilters] = useState({
    activityType: "" as ActivityType | "",
    entityType: "" as EntityType | "",
    userId: "",
    dateRange: "all" as "all" | "today" | "yesterday" | "week" | "month",
  });

  // Toggle row expansion
  const toggleRowExpanded = (logId: string) => {
    setExpandedRows((prev) => ({
      ...prev,
      [logId]: !prev[logId],
    }));
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = parseISO(dateString);
      return format(date, "MMM d, yyyy HH:mm:ss");
    } catch (error) {
      return dateString;
    }
  };

  // Get relative time for display
  const getRelativeTime = (dateString: string) => {
    try {
      const date = parseISO(dateString);
      const now = new Date();
      const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

      if (diffInSeconds < 60) {
        return `${diffInSeconds} seconds ago`;
      }

      const diffInMinutes = Math.floor(diffInSeconds / 60);
      if (diffInMinutes < 60) {
        return `${diffInMinutes} minute${diffInMinutes === 1 ? "" : "s"} ago`;
      }

      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours === 1 ? "" : "s"} ago`;
      }

      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 30) {
        return `${diffInDays} day${diffInDays === 1 ? "" : "s"} ago`;
      }

      const diffInMonths = Math.floor(diffInDays / 30);
      return `${diffInMonths} month${diffInMonths === 1 ? "" : "s"} ago`;
    } catch (error) {
      return "Unknown time";
    }
  };

  // Get activity type badge
  const getActivityTypeBadge = (type: ActivityType) => {
    switch (type) {
      case ActivityType.CREATE:
        return (
          <Badge className="bg-green-500">{t("dialog_submit_create")}</Badge>
        );
      case ActivityType.UPDATE:
        return <Badge className="bg-blue-500">{t("update_button")}</Badge>;
      case ActivityType.DELETE:
        return <Badge className="bg-red-500">{t("delete_button")}</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  // Get entity type badge
  const getEntityTypeBadge = (type: EntityType) => {
    switch (type) {
      case EntityType.MOLD:
        return (
          <Badge
            variant="outline"
            className="border-purple-500 text-purple-500"
          >
            Mold
          </Badge>
        );
      case EntityType.ARTICLE:
        return (
          <Badge variant="outline" className="border-amber-500 text-amber-500">
            Article
          </Badge>
        );
      case EntityType.ARTICLE_INSTANCE:
        return (
          <Badge variant="outline" className="border-cyan-500 text-cyan-500">
            Instance
          </Badge>
        );
      case EntityType.TECHNOLOGY:
        return (
          <Badge
            variant="outline"
            className="border-indigo-500 text-indigo-500"
          >
            Technology
          </Badge>
        );
      case EntityType.ALLOY:
        return (
          <Badge
            variant="outline"
            className="border-emerald-500 text-emerald-500"
          >
            Alloy
          </Badge>
        );
      case EntityType.TAG:
        return (
          <Badge variant="outline" className="border-pink-500 text-pink-500">
            Tag
          </Badge>
        );
      case EntityType.MOLD_SIZE:
        return (
          <Badge
            variant="outline"
            className="border-orange-500 text-orange-500"
          >
            Mold Size
          </Badge>
        );
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  // Format value for display
  const formatValue = (value: any) => {
    if (value === undefined || value === null) return "None";
    if (value === true) return "Yes";
    if (value === false) return "No";
    if (Array.isArray(value)) return value.join(", ") || "None";
    return String(value) || "None";
  };

  // Filter logs based on search term and filters
  const filteredLogs = useMemo(() => {
    if (!activityLogs) return [];

    return activityLogs.filter((log) => {
      // Search term filter
      const searchMatch =
        searchTerm === "" ||
        log.entityName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.userName.toLowerCase().includes(searchTerm.toLowerCase());

      // Activity type filter
      const activityTypeMatch =
        filters.activityType === "" ||
        log.activityType === filters.activityType;

      // Entity type filter
      const entityTypeMatch =
        filters.entityType === "" || log.entityType === filters.entityType;

      // User filter
      const userMatch = filters.userId === "" || log.userId === filters.userId;

      // Date range filter
      let dateMatch = true;
      if (filters.dateRange !== "all") {
        const logDate = parseISO(log.timestamp);
        const now = new Date();
        const today = new Date(
          now.getFullYear(),
          now.getMonth(),
          now.getDate()
        );
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        switch (filters.dateRange) {
          case "today":
            dateMatch = isAfter(logDate, today);
            break;
          case "yesterday":
            dateMatch = isAfter(logDate, yesterday) && isBefore(logDate, today);
            break;
          case "week":
            dateMatch = isAfter(logDate, subDays(now, 7));
            break;
          case "month":
            dateMatch = isAfter(logDate, subDays(now, 30));
            break;
        }
      }

      return (
        searchMatch &&
        activityTypeMatch &&
        entityTypeMatch &&
        userMatch &&
        dateMatch
      );
    });
  }, [activityLogs, searchTerm, filters]);

  // Get unique users for filter
  const uniqueUsers = useMemo(() => {
    if (!activityLogs) return [];
    const users = new Map();
    activityLogs.forEach((log) => {
      users.set(log.userId, log.userName);
    });
    return Array.from(users.entries()).map(([id, name]) => ({ id, name }));
  }, [activityLogs]);

  // Clear all filters
  const handleClearFilters = () => {
    setFilters({
      activityType: "",
      entityType: "",
      userId: "",
      dateRange: "all",
    });
    setSearchTerm("");
  };

  // Render table content based on loading state
  const renderTableContent = () => {
    if (isLoading) {
      return Array(5)
        .fill(0)
        .map((_, index) => (
          <TableRow key={`skeleton-${index}`}>
            {Array(5)
              .fill(0)
              .map((_, cellIndex) => (
                <TableCell key={`cell-${index}-${cellIndex}`}>
                  <Skeleton className="h-6 w-full" />
                </TableCell>
              ))}
          </TableRow>
        ));
    }

    if (error) {
      return (
        <TableRow>
          <TableCell colSpan={5} className="text-center py-8 text-red-500">
          {t("no_data_activity_logs")}
          </TableCell>
        </TableRow>
      );
    }

    if (!filteredLogs.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={5}
            className="text-center py-8 text-muted-foreground"
          >
            No activity logs found. Try adjusting your filters.
          </TableCell>
        </TableRow>
      );
    }

    return filteredLogs.map((log) => (
      <React.Fragment key={log.id}>
        <TableRow
          className={`cursor-pointer hover:bg-muted/50 ${
            expandedRows[log.id] ? "bg-muted/30" : ""
          }`}
          onClick={() => toggleRowExpanded(log.id)}
        >
          <TableCell className="whitespace-nowrap">
            <div className="flex flex-col">
              <span>{formatDate(log.timestamp)}</span>
              <span className="text-xs text-muted-foreground">
                {getRelativeTime(log.timestamp)}
              </span>
            </div>
          </TableCell>
          <TableCell>{getActivityTypeBadge(log.activityType)}</TableCell>
          <TableCell>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                {getEntityTypeBadge(log.entityType)}
                <span className="font-medium">{log.entityName}</span>
              </div>
              <span className="text-sm text-muted-foreground">
                {log.details}
              </span>
            </div>
          </TableCell>
          <TableCell>{log.userName}</TableCell>
          <TableCell>
            <div className="flex items-center justify-between">
              {log.changes && log.changes.length > 0 ? (
                <Badge variant="outline" className="bg-muted">
                  {log.changes.length} change{log.changes.length > 1 ? "s" : ""}
                </Badge>
              ) : (
                <span className="text-sm text-muted-foreground">
                  {t("no_changes")}
                </span>
              )}
              {log.changes && log.changes.length > 0 && (
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  {expandedRows[log.id] ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              )}
            </div>
          </TableCell>
        </TableRow>

        {/* Expanded row for changes */}
        {expandedRows[log.id] && log.changes && log.changes.length > 0 && (
          <TableRow key={`${log.id}-expanded`} className="bg-muted/20">
            <TableCell colSpan={5} className="p-0">
              <div className="p-4">
                <h4 className="text-sm font-medium mb-3">{t("detailed_changes")}</h4>
                <div className="space-y-3">
                  {log.changes.map((change, index) => (
                    <div
                      key={index}
                      className="grid grid-cols-3 gap-2 items-center"
                    >
                      <div className="font-medium text-sm">{change.field}</div>
                      <div className="flex items-center gap-2">
                        <div className="bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300 p-2 rounded text-sm flex-1 overflow-x-auto">
                          {formatValue(change.oldValue)}
                        </div>
                        <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      </div>
                      <div className="bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300 p-2 rounded text-sm overflow-x-auto">
                        {formatValue(change.newValue)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TableCell>
          </TableRow>
        )}
      </React.Fragment>
    ));
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row justify-between gap-4">
        <div className="relative w-full md:w-72">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={t("search_logs_placeholder")}
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Select
            value={filters.activityType}
            onValueChange={(value) =>
              setFilters({
                ...filters,
                activityType: value as ActivityType | "",
              })
            }
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue
                placeholder={t("select_placeholder_activity_type")}
              />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("all_activities")}</SelectItem>
              <SelectItem value={ActivityType.CREATE}>
                {t("dialog_submit_create")}
              </SelectItem>
              <SelectItem value={ActivityType.UPDATE}>
                {t("update_button")}
              </SelectItem>
              <SelectItem value={ActivityType.DELETE}>
                {t("delete_button")}
              </SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={filters.entityType}
            onValueChange={(value) =>
              setFilters({ ...filters, entityType: value as EntityType | "" })
            }
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder={t("select_placeholder_entity_type")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("all_entities")}</SelectItem>
              <SelectItem value={EntityType.MOLD}>
                {t("entity_mold")}
              </SelectItem>
              <SelectItem value={EntityType.ARTICLE}>
                {t("entity_article")}
              </SelectItem>
              <SelectItem value={EntityType.ARTICLE_INSTANCE}>
                {t("entity_instance")}
              </SelectItem>
              <SelectItem value={EntityType.TECHNOLOGY}>
                {t("entity_technology")}
              </SelectItem>
              <SelectItem value={EntityType.ALLOY}>
                {t("entity_alloy")}
              </SelectItem>
              <SelectItem value={EntityType.TAG}>{t("entity_tag")}</SelectItem>
              <SelectItem value={EntityType.MOLD_SIZE}>
                {t("entity_mold_size")}
              </SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={filters.userId}
            onValueChange={(value) => setFilters({ ...filters, userId: value })}
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder={t("select_placeholder_user")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("all_users")}</SelectItem>
              {uniqueUsers.map((user) => (
                <SelectItem key={user.id} value={user.id}>
                  {user.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.dateRange}
            onValueChange={(value) =>
              setFilters({ ...filters, dateRange: value as any })
            }
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder={t("select_placeholder_date_range")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("all_time")}</SelectItem>
              <SelectItem value="today">{t("date_range_today")}</SelectItem>
              <SelectItem value="yesterday">
                {t("date_range_yesterday")}
              </SelectItem>
              <SelectItem value="week">
                {t("date_range_last_7_days")}
              </SelectItem>
              <SelectItem value="month">
                {t("date_range_last_30_days")}
              </SelectItem>
            </SelectContent>
          </Select>

          {(searchTerm !== "" ||
            filters.activityType !== "" ||
            filters.entityType !== "" ||
            filters.userId !== "" ||
            filters.dateRange !== "all") && (
            <Button
              variant="outline"
              onClick={handleClearFilters}
              className="flex items-center gap-1"
            >
              <X className="h-4 w-4" /> {t("clear_filters")}
            </Button>
          )}

          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            className="flex items-center gap-1"
          >
            <RefreshCw className="h-4 w-4" /> {t("refresh")}
          </Button>
        </div>
      </div>

      <div className="rounded-md border overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[180px]">
                  {t("tablehead_timestamp")}
                </TableHead>
                <TableHead className="w-[100px]">
                  {t("tablehead_activity")}
                </TableHead>
                <TableHead>{t("tablehead_details")}</TableHead>
                <TableHead className="w-[150px]">
                  {t("tablehead_user")}
                </TableHead>
                <TableHead className="w-[150px]">
                  {t("tablehead_changes")}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
