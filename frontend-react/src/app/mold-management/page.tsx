import MoldManagementDashboard from "@/components/mold-management-dashboard"

/**
 * Main page component that renders the Mold Management Dashboard
 * This serves as the entry point for the application
 */
export default function Home() {
  return (
    <main className=" p-4 md:p-6 lg:p-8 h-full overflow-auto">
      <MoldManagementDashboard />
    </main>
  )
}

