"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { ActivityLogEntry} from "@/types/mold/activity-log"
import { ActivityType, EntityType, currentUser } from "@/types/mold/activity-log"

/**
 * Mock API functions for activity logs
 * In a real application, these would be replaced with actual API calls
 */
const mockActivityLogs: ActivityLogEntry[] = [
  {
    id: "log1",
    timestamp: new Date(Date.now() - 3600000 * 24 * 2).toISOString(), // 2 days ago
    userId: "user1",
    userName: "Admin User",
    activityType: ActivityType.CREATE,
    entityType: EntityType.MOLD,
    entityId: "1",
    entityName: "F10001",
    details: "Created new mold F10001",
  },
  {
    id: "log2",
    timestamp: new Date(Date.now() - 3600000 * 12).toISOString(), // 12 hours ago
    userId: "user2",
    userName: "Production Manager",
    activityType: ActivityType.UPDATE,
    entityType: EntityType.MOLD,
    entityId: "1",
    entityName: "F10001",
    details: "Updated mold F10001",
    changes: [
      {
        field: "isActive",
        oldValue: true,
        newValue: false,
      },
    ],
  },
  {
    id: "log3",
    timestamp: new Date(Date.now() - 3600000 * 5).toISOString(), // 5 hours ago
    userId: "user3",
    userName: "Quality Inspector",
    activityType: ActivityType.UPDATE,
    entityType: EntityType.ARTICLE,
    entityId: "1",
    entityName: "N-456",
    details: "Updated article N-456 status",
    changes: [
      {
        field: "status",
        oldValue: "active",
        newValue: "inactive",
      },
    ],
  },
  {
    id: "log4",
    timestamp: new Date(Date.now() - 3600000 * 2).toISOString(), // 2 hours ago
    userId: "user1",
    userName: "Admin User",
    activityType: ActivityType.CREATE,
    entityType: EntityType.ARTICLE,
    entityId: "3",
    entityName: "N-458",
    details: "Added new article N-458 to mold F10003",
  },
  {
    id: "log5",
    timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    userId: "user2",
    userName: "Production Manager",
    activityType: ActivityType.DELETE,
    entityType: EntityType.ARTICLE_INSTANCE,
    entityId: "2-2",
    entityName: "N-457 Position 2",
    details: "Removed article instance N-457 Position 2",
  },
]

/**
 * Custom hook for managing activity logs
 */
export function useActivityLog() {
  const queryClient = useQueryClient()

  /**
   * Fetch all activity logs
   */
  const fetchActivityLogs = async (): Promise<ActivityLogEntry[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockActivityLogs
  }

  /**
   * Create a new activity log entry
   */
  const createActivityLogFn = async (
    logEntry: Omit<ActivityLogEntry, "id" | "timestamp" | "userId" | "userName">,
  ): Promise<ActivityLogEntry> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 300))

    // Generate a new ID
    const newId = `log${mockActivityLogs.length + 1}`

    // Create the new log entry
    const newLogEntry: ActivityLogEntry = {
      ...logEntry,
      id: newId,
      timestamp: new Date().toISOString(),
      userId: currentUser.id,
      userName: currentUser.name,
    }

    // Add to mock data
    mockActivityLogs.unshift(newLogEntry) // Add to the beginning of the array

    return newLogEntry
  }

  /**
   * Query for fetching activity logs
   */
  const query = useQuery({
    queryKey: ["activityLogs"],
    queryFn: fetchActivityLogs,
  })

  /**
   * Mutation for creating an activity log
   */
  const createMutation = useMutation({
    mutationFn: createActivityLogFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["activityLogs"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createActivityLog: createMutation.mutateAsync,
  }
}

