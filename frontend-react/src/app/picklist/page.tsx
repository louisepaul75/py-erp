import { Suspense } from "react"
import PicklistDashboard from "@/components/picklist-dashboard"
import { PicklistSkeleton } from "@/components/picklist-skeleton"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col p-4 md:p-6">
      <h1 className="text-2xl font-bold mb-6">Lager Pickliste</h1>
      <Suspense fallback={<PicklistSkeleton />}>
        <PicklistDashboard />
      </Suspense>
    </main>
  )
}

