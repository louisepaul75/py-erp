"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface CompartmentsInputProps {
  compartment1: string
  setCompartment1: (value: string) => void
  compartment2: string
  setCompartment2: (value: string) => void
  compartment3: string
  setCompartment3: (value: string) => void
  compartment4: string
  setCompartment4: (value: string) => void
  setCompartment1InputRef: (ref: HTMLInputElement | null) => void
}

export function CompartmentsInput({
  compartment1,
  setCompartment1,
  compartment2,
  setCompartment2,
  compartment3,
  setCompartment3,
  compartment4,
  setCompartment4,
  setCompartment1InputRef,
}: CompartmentsInputProps) {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-2">
        <div>
          <Label htmlFor="compartment-1" className="text-sm text-muted-foreground mb-1 block">
            Compartment 1
          </Label>
          <Input
            id="compartment-1"
            ref={setCompartment1InputRef}
            value={compartment1}
            onChange={(e) => setCompartment1(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && compartment1) {
                e.preventDefault()
                document.getElementById("compartment-2")?.focus()
              }
            }}
            placeholder="Scan compartment 1..."
            autoComplete="off"
            className="w-full"
          />
        </div>
        <div>
          <Label htmlFor="compartment-2" className="text-sm text-muted-foreground mb-1 block">
            Compartment 2
          </Label>
          <Input
            id="compartment-2"
            value={compartment2}
            onChange={(e) => setCompartment2(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && compartment2) {
                e.preventDefault()
                document.getElementById("compartment-3")?.focus()
              }
            }}
            placeholder="Scan compartment 2..."
            autoComplete="off"
            className="w-full"
          />
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-2">
        <div>
          <Label htmlFor="compartment-3" className="text-sm text-muted-foreground mb-1 block">
            Compartment 3
          </Label>
          <Input
            id="compartment-3"
            value={compartment3}
            onChange={(e) => setCompartment3(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && compartment3) {
                e.preventDefault()
                document.getElementById("compartment-4")?.focus()
              }
            }}
            placeholder="Scan compartment 3..."
            autoComplete="off"
            className="w-full"
          />
        </div>
        <div>
          <Label htmlFor="compartment-4" className="text-sm text-muted-foreground mb-1 block">
            Compartment 4
          </Label>
          <Input
            id="compartment-4"
            value={compartment4}
            onChange={(e) => setCompartment4(e.target.value)}
            placeholder="Scan compartment 4..."
            autoComplete="off"
            className="w-full"
            // No onKeyDown handler for Enter key in the last compartment
          />
        </div>
      </div>
    </div>
  )
}

