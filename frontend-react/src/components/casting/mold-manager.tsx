"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import MoldList from "./mold-list"
import AddMoldModal from "./add-mold-modal"
import type { Mold } from "@/types/casting/mold"

interface MoldManagerProps {
  molds: Mold[]
  onAddMold: (mold: Mold) => void
  onRemoveMold: (moldId: string) => void
}

export default function MoldManager({ molds, onAddMold, onRemoveMold }: MoldManagerProps) {
  const [showAddMoldModal, setShowAddMoldModal] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Formen verwalten</h2>
        <Button 
          onClick={() => setShowAddMoldModal(true)} 
          disabled={molds.length >= 6}
        >
          <Plus className="h-4 w-4 mr-2" />
          Form hinzufügen
        </Button>
      </div>

      <MoldList molds={molds} onRemoveMold={onRemoveMold} />

      {molds.length >= 6 && (
        <div className="text-sm text-amber-600 bg-amber-50 p-2 rounded border border-amber-200">
          Maximale Anzahl an Formen erreicht (6/6).
        </div>
      )}

      <AddMoldModal 
        isOpen={showAddMoldModal} 
        onClose={() => setShowAddMoldModal(false)} 
        onAddMold={onAddMold} 
      />
    </div>
  )
} 