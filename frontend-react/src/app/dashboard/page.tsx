'use client';

import Dashboard from "@/components/ui/dashboard"
import { ErrorBoundary } from "@/components/ui/error-boundary"

export default function DashboardPage() {
  return (
    <div className="container mx-auto py-10">
      <ErrorBoundary>
        <Dashboard />
      </ErrorBoundary>
    </div>
  )
}
