"use client"
import * as SelectPrimitive from "@radix-ui/react-select"
import { Check, ChevronDown } from "lucide-react"

import { cn } from "@/lib/utils"

interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  value: string
  onValueChange: (value: string) => void
  placeholder?: string
  options: SelectOption[]
  error?: string
}

// Update the validateOptions function to handle undefined options
function validateOptions(options: SelectOption[] = []): SelectOption[] {
  if (!Array.isArray(options)) {
    return []
  }

  return options.map((option) => ({
    ...option,
    value: option.value || "placeholder", // Replace empty values with 'placeholder'
  }))
}

// Update the Select component to provide a default empty array for options
export function Select({ value, onValueChange, placeholder, options = [], error }: SelectProps) {
  // Validiere die Optionen, um leere Werte zu vermeiden
  const validatedOptions = validateOptions(options)

  return (
    <SelectPrimitive.Root value={value} onValueChange={onValueChange}>
      <SelectPrimitive.Trigger
        className={cn(
          "flex h-10 w-full items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus:ring-slate-300",
          error && "border-red-500",
        )}
      >
        <SelectPrimitive.Value placeholder={placeholder} />
        <SelectPrimitive.Icon asChild>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>
      <SelectPrimitive.Portal>
        <SelectPrimitive.Content
          className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border border-slate-200 bg-white text-slate-950 shadow-md animate-in fade-in-80 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-50"
          position="popper"
          sideOffset={5}
        >
          <SelectPrimitive.Viewport className="p-1">
            {validatedOptions.map((option) => (
              <SelectPrimitive.Item
                key={option.value}
                value={option.value}
                className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-slate-100 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 dark:focus:bg-slate-800"
              >
                <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                  <SelectPrimitive.ItemIndicator>
                    <Check className="h-4 w-4" />
                  </SelectPrimitive.ItemIndicator>
                </span>
                <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
              </SelectPrimitive.Item>
            ))}
          </SelectPrimitive.Viewport>
          <SelectScrollUpButton />
          <SelectScrollDownButton />
        </SelectPrimitive.Content>
      </SelectPrimitive.Portal>
    </SelectPrimitive.Root>
  )
}

export const SelectGroup = SelectPrimitive.Group
export const SelectTrigger = SelectPrimitive.Trigger
export const SelectValue = SelectPrimitive.Value
export const SelectContent = SelectPrimitive.Content
export const SelectLabel = SelectPrimitive.Label
export const SelectItem = SelectPrimitive.Item
export const SelectSeparator = SelectPrimitive.Separator

function SelectScrollUpButton() {
  return (
    <SelectPrimitive.ScrollUpButton className="flex items-center justify-center h-6 w-full cursor-default rounded-t py-0.5 bg-white dark:bg-slate-950">
      <span className="text-xs text-slate-400 dark:text-slate-500">Scroll up</span>
    </SelectPrimitive.ScrollUpButton>
  )
}

function SelectScrollDownButton() {
  return (
    <SelectPrimitive.ScrollDownButton className="flex items-center justify-center h-6 w-full cursor-default rounded-b py-0.5 bg-white dark:bg-slate-950">
      <span className="text-xs text-slate-400 dark:text-slate-500">Scroll down</span>
    </SelectPrimitive.ScrollDownButton>
  )
}

export { SelectScrollUpButton, SelectScrollDownButton }

