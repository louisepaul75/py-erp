"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Settings } from "lucide-react"

export interface InventorySettings {
  tolerancePercentage: number
}

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  settings: InventorySettings
  onSaveSettings: (settings: InventorySettings) => void
}

export function SettingsDialog({ open, onOpenChange, settings, onSaveSettings }: SettingsDialogProps) {
  const [tolerancePercentage, setTolerancePercentage] = useState(settings.tolerancePercentage)

  const handleSave = () => {
    onSaveSettings({
      tolerancePercentage,
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Lagereinstellungen
          </DialogTitle>
        </DialogHeader>

        <div className="py-4 space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="tolerance">Toleranzwert für Bestandsdifferenzen</Label>
              <span className="text-sm font-medium">{tolerancePercentage}%</span>
            </div>
            <Slider
              id="tolerance"
              min={0}
              max={50}
              step={1}
              value={[tolerancePercentage]}
              onValueChange={(value) => setTolerancePercentage(value[0])}
              className="w-full"
            />
            <p className="text-sm text-muted-foreground">
              Bei Differenzen größer als {tolerancePercentage}% wird automatisch eine Teilentnahme angenommen.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tolerance-input">Toleranzwert manuell eingeben</Label>
            <Input
              id="tolerance-input"
              type="number"
              min={0}
              max={50}
              value={tolerancePercentage}
              onChange={(e) => setTolerancePercentage(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <div className="bg-muted p-3 rounded-md text-sm">
            <p className="font-medium mb-1">Beispiel:</p>
            <p>Bei einem Toleranzwert von {tolerancePercentage}%:</p>
            <ul className="list-disc list-inside space-y-1 mt-2">
              <li>
                Wenn 100 Stück im System sind und {100 - Math.floor(100 * (tolerancePercentage / 100))} oder weniger
                entnommen werden, wird eine Bestandsdifferenz vermutet.
              </li>
              <li>
                Wenn 100 Stück im System sind und weniger als {Math.floor(100 * (tolerancePercentage / 100))} entnommen
                werden, wird eine Teilentnahme angenommen.
              </li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Abbrechen
          </Button>
          <Button onClick={handleSave}>Speichern</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

