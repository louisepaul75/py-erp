'use client';

import Dashboard from "@/components/ui/dashboard-content"
import { ErrorBoundary } from "@/components/ui/error-boundary"

export default function DashboardPage() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  )
}
