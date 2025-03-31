import MoldManagementDashboard from "@/components/mold-management-dashboard"

/**
 * Main page component that renders the Mold Management Dashboard
 * This serves as the entry point for the application
 */
export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-6 lg:p-8">
      <MoldManagementDashboard />
    </main>
  )
}

