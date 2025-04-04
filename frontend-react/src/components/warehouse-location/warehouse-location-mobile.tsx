"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"
import type { WarehouseLocation } from "@/types/warehouse-types"

interface WarehouseLocationMobileProps {
  filteredLocations: WarehouseLocation[]
  selectedLocations: string[]
  handleSelectLocation: (id: string, checked: boolean) => void
  handleRowClick: (location: WarehouseLocation) => void
  handleDeleteClick: (location: WarehouseLocation) => void
}

export default function WarehouseLocationMobile({
  filteredLocations,
  selectedLocations,
  handleSelectLocation,
  handleRowClick,
  handleDeleteClick,
}: WarehouseLocationMobileProps) {
  return (
    <div className="md:hidden space-y-4 mt-4">
      {filteredLocations.length > 0 ? (
        filteredLocations.slice(0, 20).map((location) => (
          <div key={location.id} className="border rounded-md p-4 bg-card" onClick={() => handleRowClick(location)}>
            <div className="flex items-center justify-between mb-2">
              <div className="font-medium">{location.laNumber}</div>
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    location.status === "free" ? "bg-status-success/10 text-status-success-foreground" : "bg-status-warning/10 text-status-warning-foreground"
                  }`}
                >
                  {location.status === "free" ? "Frei" : "Belegt"}
                </span>
                <Checkbox
                  checked={selectedLocations.includes(location.id)}
                  onCheckedChange={(checked) => handleSelectLocation(location.id, !!checked)}
                  aria-label={`Lagerort ${location.laNumber} auswählen`}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Ort/Gebäude:</div>
              <div>{location.location}</div>

              <div className="text-muted-foreground">Abverkauf:</div>
              <div>{location.forSale ? "✅" : "❌"}</div>

              <div className="text-muted-foreground">Sonderlager:</div>
              <div>{location.specialStorage ? "✅" : "❌"}</div>

              <div className="text-muted-foreground">Regal/Fach/Boden:</div>
              <div>
                {location.shelf}/{location.compartment}/{location.floor}
              </div>

              <div className="text-muted-foreground">Anzahl Schütten:</div>
              <div>{location.containerCount}</div>
            </div>
            <div className="mt-3 flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  handleDeleteClick(location)
                }}
                disabled={location.containerCount > 0}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        ))
      ) : (
        <div className="text-center py-6 text-muted-foreground">Keine Lagerorte gefunden</div>
      )}
      {filteredLocations.length > 20 && (
        <div className="text-center py-3 text-muted-foreground bg-muted rounded-md">
          Weitere Einträge auf der nächsten Seite.
        </div>
      )}
    </div>
  )
}

