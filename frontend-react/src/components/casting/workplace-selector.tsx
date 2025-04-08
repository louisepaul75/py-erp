"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface WorkplaceSelectorProps {
  selectedWorkplace: string
  onSelectWorkplace: (workplace: string) => void
}

export default function WorkplaceSelector({
  selectedWorkplace,
  onSelectWorkplace,
}: WorkplaceSelectorProps) {
  const workplaces = ["Arbeitsplatz 1", "Arbeitsplatz 2", "Arbeitsplatz 3", "Arbeitsplatz 4"]
  const [selected, setSelected] = useState(selectedWorkplace || "")

  const handleSelect = (workplace: string) => {
    setSelected(workplace)
  }

  const handleContinue = () => {
    if (selected) {
      onSelectWorkplace(selected)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Wählen Sie einen Arbeitsplatz</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-8">
        {workplaces.map((workplace) => (
          <Button
            key={workplace}
            variant={selected === workplace ? "default" : "outline"}
            className="h-20 text-lg"
            onClick={() => handleSelect(workplace)}
          >
            {workplace}
          </Button>
        ))}
      </div>
      
      <Button
        size="lg"
        onClick={handleContinue}
        disabled={!selected}
        className="w-full py-6 text-lg"
      >
        Weiter
      </Button>
    </div>
  )
} 