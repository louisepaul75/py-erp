"use client"

import React from "react"

import { useState, useEffect, useMemo } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { fetchPermissions, fetchPermissionsByModule } from "@/lib/api/permissions"
import { updateGroupPermissions } from "@/lib/api/groups"
import type { Group, Permission, PermissionModule } from "@/lib/types"

interface GroupPermissionsDialogProps {
  group: Group
  open: boolean
  onOpenChange: (open: boolean) => void
}

// Hilfsfunktion, um Berechtigungen nach Ressource zu gruppieren
interface PermissionGroup {
  resource: string
  permissions: Permission[]
}

function groupPermissionsByResource(permissions: Permission[]): PermissionGroup[] {
  const groups: Record<string, Permission[]> = {}

  permissions.forEach((permission) => {
    // Extrahiere die Ressource aus dem Code (z.B. "user" aus "user:create")
    const resource = permission.code.split(":")[0]
    if (!groups[resource]) {
      groups[resource] = []
    }
    groups[resource].push(permission)
  })

  // Sortiere die Berechtigungen innerhalb jeder Gruppe nach einer bestimmten Reihenfolge
  const actionOrder = ["view", "create", "edit", "delete", "cancel", "complete", "adjust", "export"]

  Object.values(groups).forEach((perms) => {
    perms.sort((a, b) => {
      const actionA = a.code.split(":")[1]
      const actionB = b.code.split(":")[1]
      return actionOrder.indexOf(actionA) - actionOrder.indexOf(actionB)
    })
  })

  // Konvertiere das Objekt in ein Array von Gruppen
  return Object.entries(groups).map(([resource, permissions]) => ({
    resource: resource.charAt(0).toUpperCase() + resource.slice(1), // Großschreibung für die Anzeige
    permissions,
  }))
}

export function GroupPermissionsDialog({ group, open, onOpenChange }: GroupPermissionsDialogProps) {
  const queryClient = useQueryClient()
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
  const [activeModule, setActiveModule] = useState<PermissionModule>("users")

  const { data: allPermissions = [] } = useQuery({
    queryKey: ["permissions"],
    queryFn: fetchPermissions,
  })

  const { data: modulePermissions = [] } = useQuery({
    queryKey: ["permissions", activeModule],
    queryFn: () => fetchPermissionsByModule(activeModule),
  })

  // Gruppiere die Berechtigungen nach Ressource
  const groupedPermissions = useMemo(() => groupPermissionsByResource(modulePermissions), [modulePermissions])

  const modules: PermissionModule[] = ["users", "warehouse", "sales", "production", "finance", "reporting"]

  useEffect(() => {
    if (group) {
      setSelectedPermissions(group.permissions?.map((permission) => permission.id) || [])
    }
  }, [group])

  const updateGroupPermissionsMutation = useMutation({
    mutationFn: (permissionIds: string[]) => updateGroupPermissions(group.id, permissionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] })
      onOpenChange(false)
    },
  })

  const handleTogglePermission = (permissionId: string) => {
    setSelectedPermissions((prev) =>
      prev.includes(permissionId) ? prev.filter((id) => id !== permissionId) : [...prev, permissionId],
    )
  }

  const handleToggleResourcePermissions = (resourcePermissions: Permission[], checked: boolean) => {
    const permissionIds = resourcePermissions.map((p) => p.id)

    if (checked) {
      // Füge alle Berechtigungen dieser Ressource hinzu
      setSelectedPermissions((prev) => [...new Set([...prev, ...permissionIds])])
    } else {
      // Entferne alle Berechtigungen dieser Ressource
      setSelectedPermissions((prev) => prev.filter((id) => !permissionIds.includes(id)))
    }
  }

  const isResourceFullySelected = (permissions: Permission[]): boolean => {
    return permissions.every((p) => selectedPermissions.includes(p.id))
  }

  const isResourcePartiallySelected = (permissions: Permission[]): boolean => {
    const selected = permissions.some((p) => selectedPermissions.includes(p.id))
    return selected && !isResourceFullySelected(permissions)
  }

  const handleSave = () => {
    updateGroupPermissionsMutation.mutate(selectedPermissions)
  }

  const getModuleLabel = (module: PermissionModule): string => {
    const labels: Record<PermissionModule, string> = {
      users: "Users & Access",
      warehouse: "Warehouse",
      sales: "Sales",
      production: "Production",
      finance: "Finance",
      reporting: "Reporting",
    }
    return labels[module]
  }

  const getPermissionCount = (module: PermissionModule): string => {
    const modulePerms = allPermissions.filter((p) => p.module === module)
    const selectedModulePerms = modulePerms.filter((p) => selectedPermissions.includes(p.id))
    return `${selectedModulePerms.length}/${modulePerms.length}`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Manage Group Permissions</DialogTitle>
          <DialogDescription>Assign permissions to the {group.name} group.</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col h-full">
          <Tabs
            defaultValue="users"
            value={activeModule}
            onValueChange={(value) => setActiveModule(value as PermissionModule)}
          >
            <TabsList className="grid grid-cols-3 md:grid-cols-6 mb-4">
              {modules.map((module) => (
                <TabsTrigger key={module} value={module} className="text-xs md:text-sm flex flex-col items-center py-2">
                  <span>{getModuleLabel(module)}</span>
                  <span className="text-xs text-muted-foreground mt-1">{getPermissionCount(module)}</span>
                </TabsTrigger>
              ))}
            </TabsList>

            {modules.map((module) => (
              <TabsContent key={module} value={module} className="border rounded-md">
                <div className="max-h-[400px] overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[50px]"></TableHead>
                        <TableHead>Permission Name</TableHead>
                        <TableHead className="hidden md:table-cell">Code</TableHead>
                        <TableHead className="hidden md:table-cell">Description</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {groupedPermissions.map((group) => (
                        <React.Fragment key={group.resource}>
                          {/* Ressourcen-Header mit Checkbox für alle Berechtigungen dieser Ressource */}
                          <TableRow className="bg-muted/50">
                            <TableCell>
                              <div className="relative">
                                <Checkbox
                                  checked={isResourceFullySelected(group.permissions)}
                                  // Korrigiere den indeterminate-Zustand
                                  ref={(checkbox) => {
                                    if (checkbox) {
                                      checkbox.indeterminate = isResourcePartiallySelected(group.permissions)
                                    }
                                  }}
                                  onCheckedChange={(checked) =>
                                    handleToggleResourcePermissions(group.permissions, checked as boolean)
                                  }
                                />
                              </div>
                            </TableCell>
                            <TableCell colSpan={3} className="font-medium">
                              {group.resource}
                              <Badge className="ml-2 bg-primary/10 text-primary text-xs">
                                {group.permissions.filter((p) => selectedPermissions.includes(p.id)).length}/
                                {group.permissions.length}
                              </Badge>
                            </TableCell>
                          </TableRow>

                          {/* Einzelne Berechtigungen dieser Ressource */}
                          {group.permissions.map((permission) => (
                            <TableRow key={permission.id} className="border-0">
                              <TableCell className="pl-8">
                                <Checkbox
                                  checked={selectedPermissions.includes(permission.id)}
                                  onCheckedChange={() => handleTogglePermission(permission.id)}
                                />
                              </TableCell>
                              <TableCell>{permission.name}</TableCell>
                              <TableCell className="hidden md:table-cell">
                                <code className="bg-muted px-1 py-0.5 rounded text-sm">{permission.code}</code>
                              </TableCell>
                              <TableCell className="hidden md:table-cell">{permission.description}</TableCell>
                            </TableRow>
                          ))}
                        </React.Fragment>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
        <DialogFooter className="mt-4">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="button" onClick={handleSave} disabled={updateGroupPermissionsMutation.isPending}>
            {updateGroupPermissionsMutation.isPending ? "Saving..." : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

