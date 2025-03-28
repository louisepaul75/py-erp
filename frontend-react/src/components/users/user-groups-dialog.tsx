"use client"

import { useState, useEffect } from "react"
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
import { fetchGroups } from "@/lib/api/groups"
import { updateUserGroups } from "@/lib/api/users"
import type { User } from "@/lib/types"

interface UserGroupsDialogProps {
  user: User
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function UserGroupsDialog({ user, open, onOpenChange }: UserGroupsDialogProps) {
  const queryClient = useQueryClient()
  const [selectedGroups, setSelectedGroups] = useState<string[]>([])

  const { data: groups = [] } = useQuery({
    queryKey: ["groups"],
    queryFn: fetchGroups,
  })

  useEffect(() => {
    if (user) {
      setSelectedGroups(user.groups?.map((group) => group.id) || [])
    }
  }, [user])

  const updateUserGroupsMutation = useMutation({
    mutationFn: (groupIds: string[]) => updateUserGroups(user.id, groupIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
      onOpenChange(false)
    },
  })

  const handleToggleGroup = (groupId: string) => {
    setSelectedGroups((prev) => (prev.includes(groupId) ? prev.filter((id) => id !== groupId) : [...prev, groupId]))
  }

  const handleSave = () => {
    updateUserGroupsMutation.mutate(selectedGroups)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Manage User Groups</DialogTitle>
          <DialogDescription>
            Assign {user.name} to groups. The user will have all permissions from all assigned groups.
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-[400px] overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Group Name</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {groups.map((group) => (
                <TableRow key={group.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedGroups.includes(group.id)}
                      onCheckedChange={() => handleToggleGroup(group.id)}
                    />
                  </TableCell>
                  <TableCell className="font-medium">{group.name}</TableCell>
                  <TableCell>{group.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="button" onClick={handleSave}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

