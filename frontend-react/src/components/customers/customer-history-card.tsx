"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchCustomerHistory } from "@/lib/api/customers"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { formatDate } from "@/lib/utils"
import { History } from "lucide-react"

/**
 * Komponente zur Anzeige der Kundenhistorie
 */
export default function CustomerHistoryCard({
  customerId,
}: {
  customerId: string
}) {
  // Fetch customer history using TanStack Query
  const { data: history, isLoading } = useQuery({
    queryKey: ["customerHistory", customerId],
    queryFn: () => fetchCustomerHistory(customerId),
  })

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <History className="h-5 w-5" />
        <CardTitle>Kundenhistorie</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4">Historie wird geladen...</div>
        ) : !history || history.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">
            Keine Historieneinträge für diesen Kunden gefunden.
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((entry) => (
              <div key={entry.id} className="flex items-start gap-4 rounded-lg border p-4">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={entry.user.avatar} />
                  <AvatarFallback>
                    {entry.user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{entry.user.name}</p>
                    <p className="text-xs text-muted-foreground">{formatDate(entry.timestamp)}</p>
                  </div>
                  <p className="text-sm font-medium">{entry.action}</p>
                  {entry.details && <p className="text-sm text-muted-foreground">{entry.details}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
