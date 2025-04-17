"use client"

import { useQuery } from "@tanstack/react-query"
import { ProfileManagement } from "@/components/users/profile-management"
import { fetchUsers } from "@/lib/api/users"
import { Skeleton } from "@/components/ui/skeleton"

// In einer echten App würde man die aktuelle Benutzer-ID aus der Session oder einem Auth-Context beziehen
const CURRENT_USER_ID = "1" // Beispiel: der eingeloggte Benutzer

export default function ProfilePage() {
  const { data: users, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  })

  const currentUser = users?.find((user) => user.id === CURRENT_USER_ID)

  return (
    <div className="container py-6 md:py-10 h-full overflow-auto">
      <h1 className="text-3xl font-bold mb-6">Mein Profil</h1>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      ) : currentUser ? (
        <ProfileManagement user={currentUser} />
      ) : (
        <div className="p-4 border rounded bg-red-50 text-red-800">Benutzer nicht gefunden</div>
      )}
    </div>
  )
}

