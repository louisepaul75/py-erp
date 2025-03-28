"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, RefreshCw, AlertCircle, CheckCircle, Clock } from "lucide-react"
import { LogsDrawer } from "./logs-drawer"
import { ChangesModal } from "./changes-modal"
import { fetchApiEndpoints } from "@/lib/settings/system/api"
import type { ApiEndpoint } from "@/types/settings/api"
import useAppTranslation from "@/hooks/useTranslationWrapper"

export function ApiEndpointsList() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint | null>(null)
  const [logsOpen, setLogsOpen] = useState(false)
  const [changesOpen, setChangesOpen] = useState(false)
  const { t } = useAppTranslation("settings_system");

  const {
    data: endpoints = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["apiEndpoints"],
    queryFn: fetchApiEndpoints,
  })

  const filteredEndpoints = endpoints.filter(
    (endpoint) =>
      endpoint.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      endpoint.url.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleViewLogs = (endpoint: ApiEndpoint) => {
    setSelectedEndpoint(endpoint)
    setLogsOpen(true)
  }

  const handleViewChanges = (endpoint: ApiEndpoint) => {
    setSelectedEndpoint(endpoint)
    setChangesOpen(true)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge className="bg-green-500">
            <CheckCircle className="h-3 w-3 mr-1" /> {t("active")}
          </Badge>
        )
      case "error":
        return (
          <Badge variant="destructive">
            <AlertCircle className="h-3 w-3 mr-1" /> {t("error")}
          </Badge>
        )
      case "pending":
        return (
          <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
            <Clock className="h-3 w-3 mr-1" /> {t("pending")}
          </Badge>
        )
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle>{t("external_api_endpoints")}</CardTitle>
              <CardDescription>{t("manage_api_endpoints")}</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-full md:w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder={t("search_placeholder")}
                  className="pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button variant="outline" size="icon" onClick={() => refetch()} title="Refresh">
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
                  <TableHead className="hidden md:table-cell">URL</TableHead>
                  <TableHead>{t("status")}</TableHead>
                  <TableHead>{t("last_sync")}</TableHead>
                  <TableHead className="text-right">{t("actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8">
                      {t("loading_endpoints")}
                    </TableCell>
                  </TableRow>
                ) : filteredEndpoints.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8">
                      {t("no_endpoints_found")}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredEndpoints.map((endpoint) => (
                    <TableRow key={endpoint.id}>
                      <TableCell className="font-medium">{endpoint.name}</TableCell>
                      <TableCell className="hidden md:table-cell truncate max-w-[200px]">{endpoint.url}</TableCell>
                      <TableCell>{getStatusBadge(endpoint.status)}</TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span>{new Date(endpoint.lastSync).toLocaleDateString()}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(endpoint.lastSync).toLocaleTimeString()}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm" onClick={() => handleViewLogs(endpoint)}>
                            {t("logs")}
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleViewChanges(endpoint)}>
                            {t("changes")}
                          </Button>
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

      {selectedEndpoint && (
        <>
          <LogsDrawer endpoint={selectedEndpoint} open={logsOpen} onClose={() => setLogsOpen(false)} />
          <ChangesModal endpoint={selectedEndpoint} open={changesOpen} onClose={() => setChangesOpen(false)} />
        </>
      )}
    </>
  )
}

