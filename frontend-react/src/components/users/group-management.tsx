"use client"

import React, { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, Plus, Settings } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { GroupPermissionsDialog } from "./group-permissions-dialog"
import { fetchGroups, deleteGroup, type Group } from "@/lib/api/groups"
import { AddGroupDialog } from "./add-group-dialog"

export function GroupManagement() {
  const queryClient = useQueryClient()
  const [selectedGroupId, setSelectedGroupId] = useState<string | number | null>(null)
  const [permissionsDialogOpen, setPermissionsDialogOpen] = useState(false)
  const [addDialogOpen, setAddDialogOpen] = useState(false)

  // Fetch groups
  const { data: groups = [], isLoading, error } = useQuery<Group[]>({
    queryKey: ["groups"],
    queryFn: fetchGroups
  })

  // Delete group mutation
  const { mutate: deleteGroupMutation, isPending: isDeleting } = useMutation({
    mutationFn: deleteGroup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] })
    }
  })

  // Handle opening permissions dialog
  const handleOpenPermissions = (groupId: string | number) => {
    setSelectedGroupId(groupId)
    setPermissionsDialogOpen(true)
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Failed to load groups: {(error as Error).message}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Groups</h2>
        <Button onClick={() => setAddDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Group
        </Button>
      </div>

      <AddGroupDialog 
        open={addDialogOpen} 
        onOpenChange={setAddDialogOpen} 
      />

      {isLoading ? (
        <div className="flex justify-center p-4">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Permissions</TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {groups.map((group) => (
                <TableRow key={group.id}>
                  <TableCell className="font-medium">{group.name}</TableCell>
                  <TableCell>{group.description || "-"}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {group.permissions?.length || 0} permissions
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpenPermissions(group.id)}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {selectedGroupId && (
        <GroupPermissionsDialog
          groupId={selectedGroupId}
          open={permissionsDialogOpen}
          onOpenChange={setPermissionsDialogOpen}
        />
      )}
    </div>
  )
}

