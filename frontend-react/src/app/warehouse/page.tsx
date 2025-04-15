import { redirect } from 'next/navigation';
import WarehouseLocationList from "@/components/warehouse-location-list"

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 h-full overflow-auto">
      <WarehouseLocationList />
    </main>
  )
}