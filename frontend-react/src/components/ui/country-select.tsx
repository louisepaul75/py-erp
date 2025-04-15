"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { COUNTRIES } from "@/lib/constants"
import { ScrollArea } from "@/components/ui/scroll-area"

/**
 * Komponente zur Auswahl eines Landes mit Dropdown und Suchfunktion
 *
 * @param props - Die Eigenschaften der Komponente
 * @param props.value - Der aktuell ausgewählte Länderwert
 * @param props.onValueChange - Callback-Funktion, die aufgerufen wird, wenn sich der ausgewählte Wert ändert
 * @param props.disabled - Gibt an, ob die Komponente deaktiviert ist
 * @param props.className - Zusätzliche CSS-Klassen für die Komponente
 * @param props.placeholder - Platzhaltertext, wenn kein Land ausgewählt ist
 */
export function CountrySelect({
  value,
  onValueChange,
  disabled = false,
  className,
  placeholder = "Land auswählen",
}: {
  value: string
  onValueChange: (value: string) => void
  disabled?: boolean
  className?: string
  placeholder?: string
}) {
  const [open, setOpen] = React.useState(false)
  const [searchQuery, setSearchQuery] = React.useState("")

  // Finde das ausgewählte Land in der Liste
  const selectedCountry = COUNTRIES.find((country) => country.code === value)

  // Filtere Länder basierend auf der Suchanfrage
  const filteredCountries = searchQuery
    ? COUNTRIES.filter((country) => country.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : COUNTRIES

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
          disabled={disabled}
        >
          {value && selectedCountry ? selectedCountry.name : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[300px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Land suchen..." value={searchQuery} onValueChange={setSearchQuery} />
          <div className="max-h-[300px] overflow-auto">
            <CommandList>
              <CommandEmpty>Kein Land gefunden.</CommandEmpty>
              <CommandGroup>
                <ScrollArea className="h-[300px]">
                  {filteredCountries.map((country) => (
                    <CommandItem
                      key={country.code}
                      value={country.name}
                      onSelect={() => {
                        onValueChange(country.code)
                        setOpen(false)
                        setSearchQuery("")
                      }}
                    >
                      <Check className={cn("mr-2 h-4 w-4", value === country.code ? "opacity-100" : "opacity-0")} />
                      {country.name}
                    </CommandItem>
                  ))}
                </ScrollArea>
              </CommandGroup>
            </CommandList>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  )
} 