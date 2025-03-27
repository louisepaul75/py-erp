"use client"

import type { ReactNode } from "react"
import { usePermissions } from "@/lib/hooks/use-permissions"

interface PermissionCheckProps {
  userId: string
  requiredPermission: string
  children: ReactNode
  fallback?: ReactNode
}

export function PermissionCheck({ userId, requiredPermission, children, fallback = null }: PermissionCheckProps) {
  const { hasPermission, isLoading } = usePermissions(userId)

  if (isLoading) {
    return <div>Checking permissions...</div>
  }

  return hasPermission(requiredPermission) ? <>{children}</> : <>{fallback}</>
}

