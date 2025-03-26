"use client"

import { ExternalLink } from "lucide-react"
import { Label } from "@/components/ui/label"

interface ContainerLocationTabProps {
  locationInfo: {
    location: string
    shelf: number
    compartment: number
    floor: number
    status: string
  }
  onNavigateToLocation: () => void
}

export default function ContainerLocationTab({ locationInfo, onNavigateToLocation }: ContainerLocationTabProps) {
  return (
    <div className="space-y-6">
      <h3 className="font-medium text-lg">Lagerort-Informationen</h3>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Lagerort</Label>
          <div className="p-2 border rounded-md bg-gray-50">{locationInfo.location}</div>
        </div>

        <div className="space-y-2">
          <Label>Status</Label>
          <div className="p-2 border rounded-md bg-gray-50">{locationInfo.status}</div>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Regal/Fach/Boden</Label>
        <button
          className="p-2 border rounded-md bg-gray-50 w-full text-left flex items-center justify-between hover:bg-gray-100 text-blue-600"
          onClick={onNavigateToLocation}
        >
          <span>
            {locationInfo.shelf}/{locationInfo.compartment}/{locationInfo.floor}
          </span>
          <ExternalLink className="h-4 w-4 text-blue-500" />
        </button>
      </div>
    </div>
  )
}

