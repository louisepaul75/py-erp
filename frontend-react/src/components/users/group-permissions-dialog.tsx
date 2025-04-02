"use client"

import React, { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"
import {
  fetchPermissions,
  fetchPermissionCategories,
  fetchGroupPermissions,
  updateGroupPermissions,
  type Permission,
  type PermissionCategory
} from "@/lib/api/groups"

interface GroupPermissionsDialogProps {
  groupId: string | number
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function GroupPermissionsDialog({ groupId, open, onOpenChange }: GroupPermissionsDialogProps) {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<string>("")
  const [selectedPermissions, setSelectedPermissions] = useState<Set<number>>(new Set())

  // Fetch all permissions
  const permissionsQuery = useQuery({
    queryKey: ["permissions"],
    queryFn: fetchPermissions,
  })

  // Fetch permission categories
  const categoriesQuery = useQuery({
    queryKey: ["permission-categories"],
    queryFn: fetchPermissionCategories,
  })

  // Fetch group permissions
  const groupPermissionsQuery = useQuery({
    queryKey: ["group-permissions", groupId],
    queryFn: () => fetchGroupPermissions(groupId),
  })

  // Initialize selected permissions when group permissions are loaded
  useEffect(() => {
    if (groupPermissionsQuery.data) {
      setSelectedPermissions(new Set(groupPermissionsQuery.data.map(p => p.id)))
    }
  }, [groupPermissionsQuery.data])

  // Set initial active tab when categories are loaded
  useEffect(() => {
    if (categoriesQuery.data?.length && !activeTab) {
      setActiveTab(categoriesQuery.data[0].name)
    }
  }, [categoriesQuery.data, activeTab])

  // Update permissions mutation
  const { mutate: updatePermissions, isPending: isUpdating } = useMutation({
    mutationFn: () => updateGroupPermissions(groupId, Array.from(selectedPermissions)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group-permissions", groupId] })
      onOpenChange(false)
    },
  })

  // Handle permission toggle
  const handlePermissionToggle = (permissionId: number) => {
    setSelectedPermissions((prev) => {
      const next = new Set(prev)
      if (next.has(permissionId)) {
        next.delete(permissionId)
      } else {
        next.add(permissionId)
      }
      return next
    })
  }

  const isLoading = permissionsQuery.isLoading || categoriesQuery.isLoading || groupPermissionsQuery.isLoading
  const error = permissionsQuery.error || categoriesQuery.error || groupPermissionsQuery.error

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Failed to load permissions: {(error as Error).message}</AlertDescription>
      </Alert>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Manage Group Permissions</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center p-4">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : (
          <>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 overflow-hidden">
              <div className="border-b">
                <div className="relative w-full overflow-hidden">
                  <ScrollArea className="w-full overflow-x-auto">
                    <div className="flex pb-3">
                      <TabsList>
                        {categoriesQuery.data?.map((category, index) => (
                          <TabsTrigger key={`perm-trigger-${index}`} value={category.name}>
                            {category.name}
                          </TabsTrigger>
                        ))}
                      </TabsList>
                    </div>
                  </ScrollArea>
                </div>
              </div>

              <ScrollArea className="flex-1 p-4">
                {categoriesQuery.data?.map((category, index) => (
                  <TabsContent key={`perm-content-${index}`} value={category.name} className="mt-0">
                    <div className="space-y-4">
                      {category.permissions?.map((permission) => (
                        <div key={permission.id} className="flex items-center space-x-2">
                          <Checkbox
                            id={`permission-${permission.id}`}
                            checked={selectedPermissions.has(permission.id)}
                            onCheckedChange={() => handlePermissionToggle(permission.id)}
                          />
                          <label
                            htmlFor={`permission-${permission.id}`}
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                          >
                            {permission.name}
                          </label>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                ))}
              </ScrollArea>
            </Tabs>

            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button onClick={() => updatePermissions()} disabled={isUpdating}>
                {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save Changes
              </Button>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}

