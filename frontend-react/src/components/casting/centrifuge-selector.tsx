"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Minus, Plus } from "lucide-react"

interface CentrifugeSelectorProps {
  onSelect: (count: number) => void
  defaultValue?: number
}

export default function CentrifugeSelector({
  onSelect,
  defaultValue = 1,
}: CentrifugeSelectorProps) {
  const [count, setCount] = useState(defaultValue)

  const increment = () => {
    setCount((prev) => Math.min(prev + 1, 6))
  }

  const decrement = () => {
    setCount((prev) => Math.max(prev - 1, 1))
  }

  const handleContinue = () => {
    onSelect(count)
  }

  return (
    <div className="max-w-md mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Wie viele Schleudermaschinen sind im Einsatz?</h2>
      
      <div className="flex items-center justify-center gap-4 my-8">
        <Button
          variant="outline"
          size="icon"
          className="h-12 w-12 text-lg rounded-full"
          onClick={decrement}
          disabled={count <= 1}
        >
          <Minus className="h-6 w-6" />
        </Button>
        
        <div className="text-5xl font-semibold w-20 text-center">{count}</div>
        
        <Button
          variant="outline"
          size="icon"
          className="h-12 w-12 text-lg rounded-full"
          onClick={increment}
          disabled={count >= 6}
        >
          <Plus className="h-6 w-6" />
        </Button>
      </div>
      
      <div className="text-center mb-8 text-sm text-muted-foreground">
        Mininum: 1, Maximum: 6 Schleudermaschinen
      </div>
      
      <Button
        size="lg"
        onClick={handleContinue}
        className="w-full py-6 text-lg"
      >
        Weiter
      </Button>
    </div>
  )
} 